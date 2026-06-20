import pandas as pd

from csvscope.profiler import profile_dataframe
from csvscope.quality import check_quality
from csvscope.report import render_html


def test_render_html_is_self_contained():
    df = pd.DataFrame({"age": [20, 30, 40, 50], "city": ["A", "B", "A", "C"]})
    profile = profile_dataframe(df)
    issues = check_quality(profile)
    html = render_html(df, profile, issues)
    assert html.startswith("<!DOCTYPE html>")
    assert "Data Profile Report" in html
    assert "data:image/png;base64," in html  # embedded chart, no external assets
