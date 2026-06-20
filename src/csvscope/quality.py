"""Rule-based data-quality checks that surface common problems automatically."""
from __future__ import annotations

from dataclasses import dataclass

from .profiler import DatasetProfile


@dataclass
class Issue:
    severity: str   # "high" | "medium" | "low"
    column: str
    message: str


_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def check_quality(
    profile: DatasetProfile,
    *,
    high_missing_pct: float = 50.0,
    medium_missing_pct: float = 10.0,
) -> list[Issue]:
    """Inspect a dataset profile and return a sorted list of data-quality issues."""
    issues: list[Issue] = []

    if profile.duplicate_rows > 0:
        pct = round(100 * profile.duplicate_rows / profile.n_rows, 1) if profile.n_rows else 0
        issues.append(
            Issue("medium", "<dataset>", f"{profile.duplicate_rows} duplicate rows ({pct}%).")
        )

    for col in profile.columns:
        if col.missing_pct >= high_missing_pct:
            issues.append(Issue("high", col.name, f"{col.missing_pct}% of values are missing."))
        elif col.missing_pct >= medium_missing_pct:
            issues.append(Issue("medium", col.name, f"{col.missing_pct}% of values are missing."))

        # Constant columns carry no information.
        if col.count > 0 and col.unique == 1:
            issues.append(Issue("low", col.name, "Column is constant (a single unique value)."))

        # Likely identifier columns (every value unique).
        if col.inferred_type != "numeric" and col.count > 1 and col.unique == col.count:
            issues.append(
                Issue("low", col.name, "Every value is unique - likely an identifier, not a feature.")
            )

        # Heavy outlier presence in numeric columns.
        outliers = col.stats.get("outliers", 0)
        if col.count and outliers and outliers / col.count >= 0.05:
            pct = round(100 * outliers / col.count, 1)
            issues.append(Issue("medium", col.name, f"{pct}% of values are statistical outliers."))

    issues.sort(key=lambda i: (_SEVERITY_ORDER[i.severity], i.column))
    return issues
