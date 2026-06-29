"""Auto-dashboard helpers (Plotly figures)."""
from __future__ import annotations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


THEME = dict(
    template="plotly_dark",
    color_discrete_sequence=["#22d3ee", "#a78bfa", "#f472b6", "#fbbf24", "#34d399",
                              "#60a5fa", "#f87171", "#c084fc", "#facc15", "#4ade80"],
)


def _style(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#e6edf3"),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")
    return fig


def kpi_for_numeric(df: pd.DataFrame, col: str) -> dict:
    s = df[col].dropna()
    if s.empty:
        return {"sum": 0, "mean": 0, "min": 0, "max": 0}
    return {
        "sum": float(s.sum()),
        "mean": float(s.mean()),
        "min": float(s.min()),
        "max": float(s.max()),
    }


def bar_chart(df: pd.DataFrame, cat: str, num: str, agg: str = "sum", top: int = 12) -> go.Figure:
    grouped = df.groupby(cat, dropna=False)[num].agg(agg).reset_index().sort_values(num, ascending=False).head(top)
    fig = px.bar(grouped, x=cat, y=num, title=f"{agg.title()} of {num} by {cat}", **THEME)
    return _style(fig)


def pie_chart(df: pd.DataFrame, cat: str, num: str = None, top: int = 8) -> go.Figure:
    if num and num in df.columns:
        grouped = df.groupby(cat, dropna=False)[num].sum().reset_index().sort_values(num, ascending=False).head(top)
        fig = px.pie(grouped, names=cat, values=num, title=f"Share of {num} by {cat}", hole=0.5, **THEME)
    else:
        counts = df[cat].value_counts(dropna=False).head(top).reset_index()
        counts.columns = [cat, "count"]
        fig = px.pie(counts, names=cat, values="count", title=f"Distribution of {cat}", hole=0.5, **THEME)
    return _style(fig)


def histogram(df: pd.DataFrame, num: str, bins: int = 30) -> go.Figure:
    fig = px.histogram(df, x=num, nbins=bins, title=f"Distribution of {num}", **THEME)
    return _style(fig)


def scatter(df: pd.DataFrame, x: str, y: str, color: str | None = None) -> go.Figure:
    fig = px.scatter(df, x=x, y=y, color=color, title=f"{y} vs {x}", **THEME)
    return _style(fig)


def line_chart(df: pd.DataFrame, x: str, y: str) -> go.Figure:
    d = df[[x, y]].dropna().sort_values(x)
    fig = px.line(d, x=x, y=y, title=f"{y} over {x}", markers=True, **THEME)
    return _style(fig)


def box_plot(df: pd.DataFrame, num: str, cat: str | None = None) -> go.Figure:
    fig = px.box(df, x=cat, y=num, title=f"Box plot of {num}" + (f" by {cat}" if cat else ""), **THEME)
    return _style(fig)
