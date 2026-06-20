"""Command-line interface for csvscope.

    python -m csvscope.cli data.csv -o report.html
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from .profiler import profile_dataframe
from .quality import check_quality
from .report import render_html


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Profile a CSV and write an HTML data-quality report.")
    p.add_argument("csv", help="Path to the input CSV file")
    p.add_argument("-o", "--output", default="csvscope_report.html", help="Output HTML path")
    p.add_argument("--sep", default=",", help="CSV delimiter (default: ',')")
    p.add_argument("--no-report", action="store_true", help="Print a text summary instead of writing HTML")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.csv)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    df = pd.read_csv(path, sep=args.sep)
    profile = profile_dataframe(df)
    issues = check_quality(profile)

    if args.no_report:
        print(f"{path.name}: {profile.n_rows} rows x {profile.n_cols} cols, "
              f"{profile.duplicate_rows} duplicates")
        for col in profile.columns:
            print(f"  {col.name:<24} {col.inferred_type:<12} "
                  f"missing={col.missing_pct}% unique={col.unique}")
        print(f"\n{len(issues)} quality issue(s):")
        for it in issues:
            print(f"  [{it.severity:<6}] {it.column}: {it.message}")
        return 0

    html = render_html(df, profile, issues)
    Path(args.output).write_text(html, encoding="utf-8")
    print(f"Wrote report to {args.output} "
          f"({profile.n_rows} rows, {profile.n_cols} cols, {len(issues)} issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
