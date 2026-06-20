"""csvscope - automated data profiling and quality reporting for CSV files.

Point it at a CSV and get a self-contained HTML report: column types, summary
statistics, distributions, and an automatic data-quality audit.
"""
from .profiler import ColumnProfile, DatasetProfile, profile_column, profile_dataframe
from .quality import Issue, check_quality
from .report import render_html

__version__ = "0.1.0"

__all__ = [
    "ColumnProfile",
    "DatasetProfile",
    "profile_column",
    "profile_dataframe",
    "Issue",
    "check_quality",
    "render_html",
]
