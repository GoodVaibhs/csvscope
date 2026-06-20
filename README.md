# csvscope

Point it at a CSV and get an instant, **self-contained HTML data-profile report** —
column types, summary statistics, distribution charts, and an automatic
**data-quality audit** that flags missing values, duplicates, constant columns,
likely ID columns and statistical outliers.

[![CI](https://github.com/GoodVaibhs/csvscope/actions/workflows/ci.yml/badge.svg)](https://github.com/GoodVaibhs/csvscope/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Why

Before you model or chart data, you have to understand it. `csvscope` automates
that first pass: one command turns a raw CSV into a shareable report so you spot
data-quality problems before they become modelling problems. The report is a
single HTML file — charts are embedded as base64, so there are no external assets
to host or email around.

## Install

```bash
git clone https://github.com/GoodVaibhs/csvscope.git
cd csvscope
pip install -e .
```

## Usage

```bash
# Generate the demo dataset (synthetic, reproducible)
python examples/generate_sample.py

# Build an HTML report
python -m csvscope.cli examples/customers.csv -o report.html

# Or print a quick text summary to the terminal
python -m csvscope.cli examples/customers.csv --no-report
```

After `pip install -e .` you can also just run `csvscope examples/customers.csv`.

## Library API

```python
import pandas as pd
from csvscope import profile_dataframe, check_quality, render_html

df = pd.read_csv("data.csv")
profile = profile_dataframe(df)          # types + statistics per column
issues  = check_quality(profile)         # ranked data-quality findings
html    = render_html(df, profile, issues)
open("report.html", "w").write(html)
```

## What it checks

| Check | Severity | What it catches |
|-------|----------|-----------------|
| Missing values | high / medium | Columns with ≥50% / ≥10% nulls |
| Duplicate rows | medium | Exact duplicate records |
| Outliers | medium | ≥5% of values beyond 1.5×IQR |
| Constant columns | low | Columns with a single unique value |
| Identifier columns | low | Non-numeric columns where every value is unique |

## How it works

- **Type inference** distinguishes numeric, categorical, datetime, boolean and
  free-text columns with sensible cardinality heuristics.
- **Profiling** computes per-column statistics (quartiles, IQR-based outliers,
  zero counts, cardinality) and top value frequencies.
- **Quality rules** turn that profile into a ranked list of actionable issues.
- **Reporting** renders distribution histograms and category bar charts with
  matplotlib, embedded inline so the report is one portable file.

## Testing

```bash
pip install -e ".[dev]"
pytest -v
```

## Project layout

```
src/csvscope/
  profiler.py   type inference + per-column statistics
  quality.py    rule-based data-quality checks
  report.py     self-contained HTML report with embedded charts
  cli.py        command-line interface
tests/          pytest suite
examples/       synthetic dataset generator
```

## License

MIT — see [LICENSE](LICENSE).
