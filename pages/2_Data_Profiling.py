"""Data Profiling page."""
from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.profiler import (  # noqa
    basic_metrics, column_summary, dtype_distribution, health_score, missing_heatmap_data,
)

st.set_page_config(page_title="Profiling · DataLens AI", page_icon="🔬", layout="wide")
css = (ROOT / "assets" / "styles.css")
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

st.markdown("<span class='dl-tag'>Step 02</span>", unsafe_allow_html=True)
st.title("🔬 Data Profiling")
st.caption("Shape, missing values, types, and a 0–100 health score.")

df = st.session_state.get("df")
if df is None:
    st.warning("No dataset loaded. Go to **Upload Data** first.")
    st.stop()

m = basic_metrics(df)
score, breakdown = health_score(df)

cols = st.columns(5)
metrics = [
    ("Rows", f"{m['rows']:,}"),
    ("Columns", f"{m['columns']}"),
    ("Missing", f"{m['missing']:,} ({m['missing_pct']}%)"),
    ("Duplicates", f"{m['duplicates']:,}"),
    ("Memory", f"{m['memory_mb']} MB"),
]
for col, (label, value) in zip(cols, metrics):
    with col:
        st.markdown(
            f"<div class='dl-kpi'><div class='label'>{label}</div>"
            f"<div class='value'>{value}</div></div>",
            unsafe_allow_html=True,
        )

st.write("")

left, right = st.columns([1, 1.4])
with left:
    color = "#22d3ee" if score >= 75 else ("#fbbf24" if score >= 50 else "#f87171")
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#94a3b8"},
            "bar": {"color": color},
            "bgcolor": "rgba(255,255,255,0.04)",
            "steps": [
                {"range": [0, 50], "color": "rgba(248,113,113,0.15)"},
                {"range": [50, 75], "color": "rgba(251,191,36,0.15)"},
                {"range": [75, 100], "color": "rgba(34,211,238,0.15)"},
            ],
        },
        number={"font": {"color": "#fff", "size": 44}},
        title={"text": "Dataset Health Score", "font": {"color": "#cbd5e1", "size": 14}},
    ))
    gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=300, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(gauge, use_container_width=True)
    st.markdown(
        f"<div class='dl-card'>"
        f"<b>Breakdown</b><br/>"
        f"Missing-value sub-score: <b>{breakdown['missing']}</b><br/>"
        f"Duplicate sub-score: <b>{breakdown['duplicates']}</b><br/>"
        f"Consistency sub-score: <b>{breakdown['consistency']}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

with right:
    st.markdown("#### Data type distribution")
    dt = dtype_distribution(df)
    if not dt.empty:
        fig = px.bar(
            dt, x="dtype", y="count", template="plotly_dark",
            color="dtype",
            color_discrete_sequence=["#22d3ee", "#a78bfa", "#f472b6", "#fbbf24", "#34d399"],
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
            height=260, margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
            font=dict(color="#e6edf3"),
        )
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)")
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Missing-value heatmap (sample)")
    hm = missing_heatmap_data(df, max_rows=400)
    if hm.size > 0:
        fig = go.Figure(go.Heatmap(
            z=hm, colorscale=[[0, "#0f172a"], [1, "#f472b6"]],
            showscale=False,
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=260, margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False),
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)
st.markdown("#### Column summary")
st.dataframe(column_summary(df), use_container_width=True, height=380)

st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)
if st.button("🧹 Clean Data →", type="primary", use_container_width=False):
    st.switch_page("pages/3_Data_Cleaning.py")