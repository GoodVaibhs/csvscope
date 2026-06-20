"""Column-level profiling: type inference and descriptive statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class ColumnProfile:
    name: str
    dtype: str
    inferred_type: str          # "numeric" | "categorical" | "datetime" | "boolean" | "text"
    count: int
    missing: int
    missing_pct: float
    unique: int
    unique_pct: float
    stats: dict[str, Any] = field(default_factory=dict)
    top_values: list[tuple[Any, int]] = field(default_factory=list)


@dataclass
class DatasetProfile:
    n_rows: int
    n_cols: int
    memory_bytes: int
    duplicate_rows: int
    columns: list[ColumnProfile] = field(default_factory=list)


def _infer_type(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    non_null = series.dropna()
    if non_null.empty:
        return "text"
    # Heuristic: low-cardinality strings are categorical, else free text.
    nunique = non_null.nunique()
    if nunique <= max(20, int(0.5 * len(non_null))):
        return "categorical"
    return "text"


def profile_column(series: pd.Series) -> ColumnProfile:
    n = len(series)
    missing = int(series.isna().sum())
    non_null = series.dropna()
    unique = int(non_null.nunique())
    inferred = _infer_type(series)

    stats: dict[str, Any] = {}
    if inferred == "numeric" and not non_null.empty:
        desc = non_null.astype(float)
        q1, q3 = float(desc.quantile(0.25)), float(desc.quantile(0.75))
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = int(((desc < lo) | (desc > hi)).sum())
        stats = {
            "min": float(desc.min()),
            "max": float(desc.max()),
            "mean": float(desc.mean()),
            "median": float(desc.median()),
            "std": float(desc.std()) if len(desc) > 1 else 0.0,
            "q1": q1,
            "q3": q3,
            "outliers": outliers,
            "zeros": int((desc == 0).sum()),
        }

    top_values: list[tuple[Any, int]] = []
    if inferred in {"categorical", "boolean", "text"} and not non_null.empty:
        vc = non_null.value_counts().head(10)
        top_values = [(idx, int(cnt)) for idx, cnt in vc.items()]

    return ColumnProfile(
        name=str(series.name),
        dtype=str(series.dtype),
        inferred_type=inferred,
        count=int(n - missing),
        missing=missing,
        missing_pct=round(100 * missing / n, 2) if n else 0.0,
        unique=unique,
        unique_pct=round(100 * unique / (n - missing), 2) if (n - missing) else 0.0,
        stats=stats,
        top_values=top_values,
    )


def profile_dataframe(df: pd.DataFrame) -> DatasetProfile:
    """Produce a full profile of every column plus dataset-level metadata."""
    return DatasetProfile(
        n_rows=len(df),
        n_cols=df.shape[1],
        memory_bytes=int(df.memory_usage(deep=True).sum()),
        duplicate_rows=int(df.duplicated().sum()),
        columns=[profile_column(df[c]) for c in df.columns],
    )
