"""Render a profile and quality findings into a standalone HTML report.

Charts are rendered with matplotlib and embedded as base64 PNGs, so the output
is a single self-contained file with no external assets.
"""
from __future__ import annotations

import base64
import html
import io
from datetime import datetime

import matplotlib

matplotlib.use("Agg")  # headless backend, no display needed
import matplotlib.pyplot as plt
import pandas as pd

from .profiler import ColumnProfile, DatasetProfile
from .quality import Issue

_SEVERITY_COLOR = {"high": "#d64545", "medium": "#e08a1e", "low": "#3a7ca5"}


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=90)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _chart_for_column(df: pd.DataFrame, col: ColumnProfile) -> str | None:
    series = df[col.name].dropna()
    if series.empty:
        return None
    fig, ax = plt.subplots(figsize=(4, 2.4))
    if col.inferred_type == "numeric":
        ax.hist(series.astype(float), bins=min(30, max(5, col.unique)), color="#3a7ca5")
        ax.set_ylabel("count")
    elif col.top_values:
        labels = [str(v)[:18] for v, _ in col.top_values]
        counts = [c for _, c in col.top_values]
        ax.barh(labels[::-1], counts[::-1], color="#3a7ca5")
        ax.set_xlabel("count")
    else:
        plt.close(fig)
        return None
    ax.set_title(col.name, fontsize=9)
    ax.tick_params(labelsize=7)
    return _fig_to_base64(fig)


def render_html(df: pd.DataFrame, profile: DatasetProfile, issues: list[Issue]) -> str:
    """Return a complete HTML document as a string."""
    esc = html.escape
    parts: list[str] = []
    parts.append(f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>csvscope report</title>
<style>
 body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; color: #1c2733; background:#f6f8fa; }}
 .wrap {{ max-width: 1000px; margin: 0 auto; padding: 32px; }}
 h1 {{ margin-bottom: 4px; }}
 .sub {{ color:#647488; margin-top:0; }}
 .cards {{ display:flex; gap:16px; flex-wrap:wrap; margin:24px 0; }}
 .card {{ background:#fff; border:1px solid #e1e6eb; border-radius:10px; padding:16px 20px; flex:1; min-width:120px; }}
 .card .n {{ font-size:26px; font-weight:700; }}
 .card .l {{ color:#647488; font-size:13px; }}
 table {{ border-collapse:collapse; width:100%; background:#fff; border-radius:10px; overflow:hidden; }}
 th, td {{ text-align:left; padding:8px 12px; border-bottom:1px solid #eef1f4; font-size:13px; }}
 th {{ background:#eef2f6; }}
 .pill {{ display:inline-block; padding:2px 8px; border-radius:12px; color:#fff; font-size:11px; }}
 .col {{ background:#fff; border:1px solid #e1e6eb; border-radius:10px; padding:16px; margin:14px 0; display:flex; gap:18px; align-items:center; }}
 .col img {{ border-radius:6px; }}
 .col .meta {{ flex:1; }}
 .tag {{ font-size:11px; color:#647488; text-transform:uppercase; letter-spacing:.04em; }}
 code {{ background:#eef2f6; padding:1px 5px; border-radius:4px; }}
</style></head><body><div class="wrap">""")

    parts.append(f"<h1>Data Profile Report</h1>")
    parts.append(f'<p class="sub">Generated {esc(datetime.now().strftime("%Y-%m-%d %H:%M"))} &middot; csvscope</p>')

    mem_kb = round(profile.memory_bytes / 1024, 1)
    parts.append('<div class="cards">')
    for n, l in [
        (profile.n_rows, "rows"),
        (profile.n_cols, "columns"),
        (profile.duplicate_rows, "duplicate rows"),
        (f"{mem_kb} KB", "in memory"),
        (len(issues), "quality issues"),
    ]:
        parts.append(f'<div class="card"><div class="n">{esc(str(n))}</div><div class="l">{esc(l)}</div></div>')
    parts.append("</div>")

    # Quality issues
    parts.append("<h2>Data-quality issues</h2>")
    if not issues:
        parts.append("<p>No issues detected. 🎉</p>")
    else:
        parts.append("<table><tr><th>Severity</th><th>Column</th><th>Issue</th></tr>")
        for it in issues:
            color = _SEVERITY_COLOR[it.severity]
            parts.append(
                f'<tr><td><span class="pill" style="background:{color}">{esc(it.severity)}</span></td>'
                f"<td><code>{esc(it.column)}</code></td><td>{esc(it.message)}</td></tr>"
            )
        parts.append("</table>")

    # Per-column detail
    parts.append("<h2>Columns</h2>")
    for col in profile.columns:
        img = _chart_for_column(df, col)
        img_tag = (
            f'<img src="data:image/png;base64,{img}" alt="chart for {esc(col.name)}">'
            if img else ""
        )
        meta = [
            f'<span class="tag">{esc(col.inferred_type)} &middot; {esc(col.dtype)}</span>',
            f"<h3 style='margin:4px 0'>{esc(col.name)}</h3>",
            f"missing: {col.missing} ({col.missing_pct}%) &nbsp; unique: {col.unique} ({col.unique_pct}%)",
        ]
        if col.stats:
            s = col.stats
            meta.append(
                f"<br>min {s['min']:.2f} &middot; mean {s['mean']:.2f} &middot; "
                f"median {s['median']:.2f} &middot; max {s['max']:.2f} &middot; std {s['std']:.2f}"
            )
        parts.append(f'<div class="col"><div class="meta">{"".join(meta)}</div>{img_tag}</div>')

    parts.append("</div></body></html>")
    return "".join(parts)
