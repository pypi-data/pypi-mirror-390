# 🪶 liteprofile

> A lightweight, fast alternative inspired by [ydata-profiling (pandas-profiling)](https://github.com/ydataai/ydata-profiling) — built on [Polars](https://www.pola.rs/).

---

### ⚡️ Why

`liteprofile` is inspired by the great work of `ydata-profiling`.  
While that library provides **rich and detailed statistical reports**, `liteprofile` focuses on **speed, simplicity, and small output** for quick exploratory data analysis (EDA).

It’s designed as a **complement** — use `ydata-profiling` when you need deep insights, and `liteprofile` when you need a fast, clear overview.

| Tool | Focus | Typical use-case | Output | Dependencies |
|------|--------|------------------|---------|---------------|
| ydata-profiling | full statistical profiling | comprehensive analysis | large HTML report | heavy |
| sweetviz | visualization-focused | visual EDA | HTML dashboard | medium |
| **liteprofile** | lightweight summaries | fast checks / CI / CLI | Markdown or compact HTML | minimal |

---

### 🚀 Features

- ⚡ Super-fast summaries with **Polars** or **DuckDB**
- 📊 Numeric stats: mean, std, quantiles, outliers
- 🔢 Categorical summaries: top frequencies
- 🔗 Optional numeric correlations
- 🧠 Smart warnings (constant / missing / high-cardinality)
- 🧰 CLI and Python API
- 💾 Outputs: Markdown or minimal HTML
- 🧩 Easy to extend — build your own “lite” analytics blocks

---

### 🧰 Installation

```bash
pip install liteprofile
# or from source
pip install git+https://github.com/inezvl/liteprofile.git
```

---

### 💡 Quickstart

#### From Python

```python
import polars as pl
from liteprofile import profile, profile_html

df = pl.DataFrame({
    "id": [1, 2, 3, 4, 5],
    "city": ["Antwerp", "Ghent", "Ghent", "Brussels", None],
    "price": [100.0, 200.5, 180.2, 300.0, 300.0]
})

# Markdown summary
print(profile(df))

# HTML summary
html = profile_html(df)
with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)
```

#### From CLI

```bash
python -m liteprofile data.csv --html --out report.html
open report.html
```

---

### 🪶 Example Output (Markdown)

```
# liteprofile report

## Overview
| metric          | value |
|-----------------|--------|
| rows            | 5      |
| columns         | 3      |
| duplicate_rows  | 0      |

## Columns
| column | dtype | nulls | null_% | unique | mean | std | min | q1 | median | q3 | max | outliers_iqr | sample |
|--------|--------|-------|--------|---------|------|-----|-----|----|---------|----|-----|---------------|---------|
| id     | Int64  | 0 | 0 | 5 | 3 | 1.58 | 1 | 2 | 3 | 4 | 5 | 0 | [1, 2, 3, 4, 5] |
| city   | Utf8   | 1 | 20 | 3 |  |  |  |  |  |  |  |  | ['Antwerp', 'Ghent', 'Ghent', 'Brussels', None] |
| price  | Float64 | 0 | 0 | 3 | 216 | 83.8 | 100 | 180 | 200 | 300 | 300 | 0 | [100.0, 200.5, 180.2, 300.0, 300.0] |
```

---

### 🧩 Roadmap

| Feature | Status | Notes |
|----------|---------|-------|
| Core Markdown summary | ✅ | already implemented |
| HTML summary | ✅ | minimal & lightweight |
| CLI support | ✅ | `python -m liteprofile` |
| DuckDB backend | 🧠 planned | for large datasets |
| Sampling mode | 🧠 planned | for millions of rows |
| YAML profiles (speed/deep) | 🧠 planned | toggle stats easily |
| PyPI release | 🚧 | coming soon |

---

### 🧠 Philosophy

`liteprofile` aims to **complement** existing data-profiling tools.  
Instead of competing, it offers a minimal mode for everyday use — perfect for quick checks before going deeper with heavier frameworks.

> _Inspired by the community feedback around the need for a “fast mode” in ydata-profiling._

---

### 🤝 Contributing

Contributions are welcome!  
You can help by:
- Adding backends (DuckDB, Arrow, SQLite)
- Enhancing HTML rendering
- Building small extensions (e.g., histograms, missing-value heatmaps)
- Benchmarking against other profilers

---

### 📜 License

MIT © [Inez Van Laer](https://github.com/inezvl)

---

### ⭐️ Support

If you like the project:
- Leave a ⭐️ on GitHub — it really helps  
- Open a Discussion for feedback or feature ideas  
- Tell us what you’d love to see in the next release!
