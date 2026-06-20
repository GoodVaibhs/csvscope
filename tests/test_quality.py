import numpy as np
import pandas as pd

from csvscope.profiler import profile_dataframe
from csvscope.quality import check_quality


def test_detects_missing_and_constant():
    df = pd.DataFrame(
        {
            "mostly_missing": [1, None, None, None, None],
            "constant": [7, 7, 7, 7, 7],
            "ok": [1, 2, 3, 4, 5],
        }
    )
    issues = check_quality(profile_dataframe(df))
    cols_with_issues = {i.column for i in issues}
    assert "mostly_missing" in cols_with_issues
    assert "constant" in cols_with_issues
    severities = {i.severity for i in issues}
    assert "high" in severities  # mostly_missing column


def test_detects_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    issues = check_quality(profile_dataframe(df))
    assert any("duplicate" in i.message.lower() for i in issues)


def test_clean_data_has_no_high_issues():
    df = pd.DataFrame({"a": range(100), "b": [i * 2 for i in range(100)]})
    issues = check_quality(profile_dataframe(df))
    assert all(i.severity != "high" for i in issues)
