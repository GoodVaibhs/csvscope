import numpy as np
import pandas as pd

from csvscope.profiler import profile_column, profile_dataframe


def make_df():
    return pd.DataFrame(
        {
            "age": [25, 32, 47, np.nan, 51, 33, 29, 1000],   # 1000 is an outlier
            "city": ["NY", "LA", "NY", "SF", "LA", "NY", "SF", "LA"],
            "id": list(range(8)),
            "constant": ["x"] * 8,
        }
    )


def test_numeric_profile():
    p = profile_column(make_df()["age"])
    assert p.inferred_type == "numeric"
    assert p.missing == 1
    assert p.stats["max"] == 1000.0
    assert p.stats["outliers"] >= 1


def test_categorical_profile():
    p = profile_column(make_df()["city"])
    assert p.inferred_type == "categorical"
    assert p.top_values[0][0] in {"NY", "LA"}


def test_dataset_profile_shape():
    prof = profile_dataframe(make_df())
    assert prof.n_rows == 8
    assert prof.n_cols == 4
    assert len(prof.columns) == 4
