# liteprofile.py
from __future__ import annotations
import math
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Try to use Polars for speed; fall back to pandas
try:
    import polars as pl
    _HAS_POLARS = True
except Exception:
    _HAS_POLARS = False

try:
    import pandas as pd
    _HAS_PANDAS = True
except Exception:
    _HAS_PANDAS = False


def _to_polars(df: Any) -> "pl.DataFrame":
    if _HAS_POLARS and isinstance(df, pl.DataFrame):
        return df
    if _HAS_POLARS and _HAS_PANDAS and isinstance(df, pd.DataFrame):
        return pl.from_pandas(df)
    if _HAS_POLARS and isinstance(df, list):
        return pl.DataFrame(df)
    if _HAS_PANDAS and isinstance(df, pd.DataFrame):
        # last resort: convert pandas-like to polars via records
        return pl.from_pandas(df)
    raise TypeError("Provide a polars.DataFrame, pandas.DataFrame, or list of dicts.")


def _is_numeric(dtype: Any) -> bool:
    """Check if a Polars dtype (or fallback) is numeric."""
    if _HAS_POLARS:
        # Works across Polars versions
        try:
            import polars.datatypes as dt
            return dt.is_numeric_dtype(dtype) if hasattr(dt, "is_numeric_dtype") else dtype in (
                pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                pl.Float32, pl.Float64
            )
        except Exception:
            return dtype in (
                pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                pl.Float32, pl.Float64
            )
    # fallback for non-Polars mode
    try:
        import numpy as np
        return np.issubdtype(dtype, np.number)
    except Exception:
        return False


def _sample_values(col: "pl.Series", k: int = 5) -> List[str]:
    # small deterministic sample from head/tail + unique
    vals = []
    head_vals = col.head(k).to_list()
    tail_vals = col.tail(k).to_list() if len(col) > k else []
    for v in head_vals + tail_vals:
        s = repr(v)
        if s not in vals:
            vals.append(s)
        if len(vals) >= k:
            break
    return vals


def _markdown_table(rows: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
    if not rows:
        return "_(no rows)_"
    if headers is None:
        headers = list(rows[0].keys())
    # widths
    cols = headers
    data = [[str(r.get(c, "")) for c in cols] for r in rows]
    widths = [max(len(str(h)), max((len(row[i]) for row in data), default=0)) for i, h in enumerate(cols)]
    # header
    out = []
    out.append("| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(cols)) + " |")
    out.append("| " + " | ".join("-" * widths[i] for i in range(len(cols))) + " |")
    # rows
    for row in data:
        out.append("| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(cols))) + " |")
    return "\n".join(out)


def _format_float(x: Optional[float], nd: int = 6) -> str:
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return ""
    return f"{x:.{nd}g}"


def _iqr_outlier_count(s: "pl.Series") -> int:
    try:
        q1 = s.quantile(0.25, interpolation="nearest")
        q3 = s.quantile(0.75, interpolation="nearest")
        iqr = q3 - q1
        if iqr == 0:
            return 0
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return int(s.filter((s < lower) | (s > upper)).len())
    except Exception:
        return 0


def _corr_matrix_numeric(df: "pl.DataFrame", numeric_cols: List[str]) -> List[Dict[str, Any]]:
    if len(numeric_cols) < 2:
        return []
    rows = []
    # Efficient column extraction
    num_df = df.select(numeric_cols)
    for i, c1 in enumerate(numeric_cols):
        for j, c2 in enumerate(numeric_cols):
            if j <= i:
                continue
            try:
                c = num_df.select(pl.corr(c1, c2)).item()
            except Exception:
                # older polars
                c = num_df.select(pl.col(c1).pearson_corr(pl.col(c2))).item()
            rows.append({"col_1": c1, "col_2": c2, "pearson_r": _format_float(c, 4)})
    return rows


def _dtype_name(dt: Any) -> str:
    try:
        return str(dt)
    except Exception:
        return repr(dt)


def profile(df_like: Any, top_n_cat: int = 10, max_rows_preview: int = 5) -> str:
    """
    Return a Markdown EDA report string.
    - df_like: polars.DataFrame, pandas.DataFrame, or list of dicts
    """
    df = _to_polars(df_like)
    n_rows, n_cols = df.height, df.width
    est_mem = getattr(df, "estimated_size", None)
    mem_mb = None
    if callable(est_mem):
        try:
            mem_mb = est_mem() / (1024 * 1024)
        except Exception:
            mem_mb = None

    # --- Overview
    overview_rows = [
        {"metric": "rows", "value": n_rows},
        {"metric": "columns", "value": n_cols},
        {"metric": "memory_mb", "value": _format_float(mem_mb, 3) if mem_mb is not None else ""},
        {"metric": "duplicate_rows", "value": int(n_rows - df.unique().height)},
    ]

    # --- Per-column summary
    col_rows: List[Dict[str, Any]] = []
    numeric_cols: List[str] = []

    for col in df.columns:
        s = df[col]
        dt = s.dtype
        is_num = _is_numeric(dt)
        if is_num:
            numeric_cols.append(col)
        nulls = s.null_count()
        nuniq = s.n_unique()
        samples = ", ".join(_sample_values(s, 5))
        row = {
            "column": col,
            "dtype": _dtype_name(dt),
            "nulls": nulls,
            "null_%": _format_float((nulls / n_rows * 100) if n_rows else 0.0, 4),
            "unique": nuniq,
            "sample": samples
        }
        # numeric stats
        if is_num:
            desc = df.select(
                pl.col(col).mean().alias("mean"),
                pl.col(col).std(ddof=1).alias("std"),
                pl.col(col).min().alias("min"),
                pl.col(col).quantile(0.25, interpolation="nearest").alias("q1"),
                pl.col(col).median().alias("median"),
                pl.col(col).quantile(0.75, interpolation="nearest").alias("q3"),
                pl.col(col).max().alias("max"),
            ).to_dicts()[0]
            for k in ["mean", "std", "min", "q1", "median", "q3", "max"]:
                row[k] = _format_float(desc[k], 6)
            row["outliers_iqr"] = _iqr_outlier_count(s)
        col_rows.append(row)

    # --- Top categories for non-numeric
    cat_sections: List[Tuple[str, str]] = []
    for col in df.columns:
        s = df[col]
        if _is_numeric(s.dtype):
            continue
        try:
            freq = (
                df.select(pl.col(col))
                  .drop_nulls()
                  .group_by(col).len()
                  .sort("len", descending=True)
                  .head(top_n_cat)
            )
            rows = [{"value": repr(r[col]), "count": r["len"]} for r in freq.to_dicts()]
            cat_sections.append((col, _markdown_table(rows, headers=["value","count"])))
        except Exception:
            pass

    # --- Correlations
    corr_rows = _corr_matrix_numeric(df, numeric_cols)

    # --- Preview
    preview_rows = []
    if n_rows > 0:
        preview_df = df.head(max_rows_preview)
        preview_rows = preview_df.to_dicts()

    # --- Warnings
    warnings: List[str] = []
    for r in col_rows:
        try:
            if int(r.get("unique", 0)) == 1:
                warnings.append(f"`{r['column']}` is constant.")
            if float(r.get("null_%", 0) or 0) > 50:
                warnings.append(f"`{r['column']}` has >50% missing.")
            if int(r.get("unique", 0)) > max(50, n_rows * 0.9):
                warnings.append(f"`{r['column']}` may be high-cardinality.")
        except Exception:
            continue

    # --- Compose Markdown
    md: List[str] = []
    md.append(f"# liteprofile report\n")
    md.append("## Overview\n")
    md.append(_markdown_table(overview_rows, headers=["metric", "value"]))
    md.append("\n")

    md.append("## Columns\n")
    md.append(_markdown_table(col_rows,
        headers=[
            "column","dtype","nulls","null_%","unique",
            "mean","std","min","q1","median","q3","max","outliers_iqr","sample"
        ]))
    md.append("\n")

    if cat_sections:
        md.append("## Categorical Frequencies (Top)\n")
        for col, table in cat_sections:
            md.append(f"### {col}\n")
            md.append(table + "\n")

    if corr_rows:
        md.append("## Correlations (numeric only)\n")
        md.append(_markdown_table(corr_rows, headers=["col_1","col_2","pearson_r"]))
        md.append("\n")

    if preview_rows:
        md.append("## Preview\n")
        # convert dicts to string rows with stable columns
        cols = list(preview_rows[0].keys())
        md.append(_markdown_table(preview_rows, headers=cols))
        md.append("\n")

    if warnings:
        md.append("## Warnings\n")
        for w in warnings:
            md.append(f"- {w}")
        md.append("\n")

    return "\n".join(md)


def profile_html(df_like: Any, **kwargs) -> str:
    """Very small HTML wrapper around the Markdown output."""
    md = profile(df_like, **kwargs)
    # cheap and cheerful: wrap in <pre> to keep alignment;
    # you can replace this with a markdown->HTML converter later.
    escaped = (
        md.replace("&","&amp;")
          .replace("<","&lt;")
          .replace(">","&gt;")
    )
    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>liteprofile report</title>
<style>
body {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; padding: 16px; }}
pre {{ white-space: pre-wrap; }}
a {{ color: inherit; }}
</style>
<pre>{escaped}</pre>
</html>"""


# --- CLI entry --------------------------------------------------------------
def main() -> None:
    import argparse, sys, os, time
    from pathlib import Path

    p = argparse.ArgumentParser(description="liteprofile - tiny EDA summaries")
    p.add_argument("input", help="Path to a CSV/Parquet file")
    p.add_argument("--html", action="store_true", help="Output HTML (default: markdown)")
    p.add_argument("--out", help="Write to file (default: stdout)")
    p.add_argument("--top-n-cat", type=int, default=10)
    p.add_argument("--preview", type=int, default=5)
    p.add_argument("--verbose", "-v", action="store_true", help="Print progress messages")
    args = p.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"[liteprofile] ❌ File not found: {src}", file=sys.stderr)
        sys.exit(2)

    if args.verbose:
        print(f"[liteprofile] Loading {src} ...")

    # Load with polars if possible, otherwise pandas
    df = None
    try:
        if _HAS_POLARS:
            if src.suffix.lower() == ".parquet":
                df = pl.read_parquet(src)
            else:
                df = pl.read_csv(src, infer_schema_length=2000)
            n_rows, n_cols = df.height, len(df.columns)
        elif _HAS_PANDAS:
            if src.suffix.lower() == ".parquet":
                df = pd.read_parquet(src)
            else:
                df = pd.read_csv(src)
            n_rows, n_cols = df.shape
        else:
            raise RuntimeError("Install polars or pandas to load files.")
    except Exception as e:
        print(f"[liteprofile] ❌ Failed to load {src}: {e}", file=sys.stderr)
        sys.exit(3)

    if args.verbose:
        print(f"[liteprofile] ✅ Loaded dataframe with {n_rows:,} rows × {n_cols} columns")

    t0 = time.perf_counter()
    out_str = (
        profile_html(df, top_n_cat=args.top_n_cat, max_rows_preview=args.preview)
        if args.html
        else profile(df, top_n_cat=args.top_n_cat, max_rows_preview=args.preview)
    )
    dt = time.perf_counter() - t0

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(out_str, encoding="utf-8")
        size_kb = out_path.stat().st_size / 1024
        kind = "HTML" if args.html else "Markdown"
        print(
            f"[liteprofile] ✅ Wrote {kind} report → {out_path} "
            f"({size_kb:.1f} KB) in {dt:.2f}s — processed {n_rows:,} rows × {n_cols} columns"
        )
    else:
        # print to stdout (Markdown)
        print(out_str)
        if args.verbose:
            print(f"[liteprofile] ✅ Printed report to stdout in {dt:.2f}s — processed {n_rows:,} rows × {n_cols} columns")


if __name__ == "__main__":
    main()
