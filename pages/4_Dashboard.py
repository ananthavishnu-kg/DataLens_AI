"""Auto Dashboard page."""
from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.loader import detect_column_roles  # noqa
from modules.dashboard import (  # noqa
    kpi_for_numeric, bar_chart, pie_chart, histogram, scatter, line_chart, box_plot,
)

st.set_page_config(page_title="Dashboard · DataLens AI", page_icon="📊", layout="wide")
css = (ROOT / "assets" / "styles.css")
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

st.markdown("<span class='dl-tag'>Step 04</span>", unsafe_allow_html=True)
st.title("📊 Auto Dashboard")
st.caption("KPI cards and interactive Plotly charts — auto-generated from your data.")

# ✅ Fixed: safe DataFrame check (no 'or' on DataFrame)
df = st.session_state.get("df_clean")
if df is None:
    df = st.session_state.get("df")
if df is None:
    st.warning("No dataset loaded. Go to **Upload Data** first.")
    st.stop()

roles = detect_column_roles(df)
nums, cats, dates = roles["numeric"], roles["categorical"], roles["date"]

with st.expander("🎚️ Filters", expanded=False):
    fcols = st.columns(3)
    filt = df.copy()
    with fcols[0]:
        if dates:
            dcol = st.selectbox("Date column", ["—"] + dates, key="filter-date-col")
            if dcol != "—":
                parsed = pd.to_datetime(filt[dcol], errors="coerce")
                valid = parsed.dropna()
                if not valid.empty:
                    lo, hi = valid.min().date(), valid.max().date()
                    rng = st.date_input("Range", (lo, hi), key="filter-date-rng")
                    if isinstance(rng, tuple) and len(rng) == 2:
                        mask = (parsed.dt.date >= rng[0]) & (parsed.dt.date <= rng[1])
                        filt = filt[mask.fillna(False)]
    with fcols[1]:
        if cats:
            ccol = st.selectbox("Category column", ["—"] + cats, key="filter-cat-col")
            if ccol != "—":
                opts = filt[ccol].dropna().unique().tolist()[:200]
                sel = st.multiselect("Values", opts, default=opts, key="filter-cat-val")
                filt = filt[filt[ccol].isin(sel)]
    with fcols[2]:
        if nums:
            ncol = st.selectbox("Numeric column", ["—"] + nums, key="filter-num-col")
            if ncol != "—":
                s = filt[ncol].dropna()
                if not s.empty:
                    lo, hi = float(s.min()), float(s.max())
                    rng = st.slider("Range", lo, hi, (lo, hi), key="filter-num-rng")
                    filt = filt[(filt[ncol] >= rng[0]) & (filt[ncol] <= rng[1])]
    if len(filt) != len(df):
        st.caption(f"Filtered: **{len(filt):,}** / {len(df):,} rows")
    df = filt

st.markdown("### Key metrics")
if nums:
    kpi_cols = st.columns(min(4, len(nums)))
    for col, name in zip(kpi_cols, nums[:4]):
        k = kpi_for_numeric(df, name)
        col.markdown(
            f"""<div class='dl-kpi'>
                <div class='label'>{name}</div>
                <div class='value'>{k['sum']:,.2f}</div>
                <div class='sub'>μ {k['mean']:,.2f}  ·  min {k['min']:,.2f}  ·  max {k['max']:,.2f}</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("No numeric columns detected — KPI cards skipped.")

st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)

chart_tabs = st.tabs(["📊 Bar", "🥧 Pie", "📈 Histogram", "✨ Scatter", "📉 Line", "📦 Box"])

with chart_tabs[0]:
    if cats and nums:
        c1, c2, c3 = st.columns(3)
        cat = c1.selectbox("Category", cats, key="bar-cat")
        num = c2.selectbox("Metric", nums, key="bar-num")
        agg = c3.selectbox("Aggregate", ["sum", "mean", "median", "count"], key="bar-agg")
        st.plotly_chart(bar_chart(df, cat, num, agg), use_container_width=True)
    else:
        st.info("Need at least one categorical and one numeric column.")

with chart_tabs[1]:
    if cats:
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Category", cats, key="pie-cat")
        num = c2.selectbox("Metric (optional)", ["count"] + nums, key="pie-num")
        st.plotly_chart(pie_chart(df, cat, None if num == "count" else num), use_container_width=True)
    else:
        st.info("Need a categorical column.")

with chart_tabs[2]:
    if nums:
        c1, c2 = st.columns([2, 1])
        num = c1.selectbox("Numeric column", nums, key="hist-num")
        bins = c2.slider("Bins", 10, 80, 30, key="hist-bins")
        st.plotly_chart(histogram(df, num, bins), use_container_width=True)
    else:
        st.info("Need a numeric column.")

with chart_tabs[3]:
    if len(nums) >= 2:
        c1, c2, c3 = st.columns(3)
        x = c1.selectbox("X", nums, key="sc-x")
        y = c2.selectbox("Y", [n for n in nums if n != x], key="sc-y")
        color = c3.selectbox("Color", ["—"] + cats, key="sc-c")
        st.plotly_chart(scatter(df, x, y, None if color == "—" else color), use_container_width=True)
    else:
        st.info("Need at least two numeric columns.")

with chart_tabs[4]:
    if dates and nums:
        c1, c2 = st.columns(2)
        x = c1.selectbox("Date", dates, key="line-x")
        y = c2.selectbox("Value", nums, key="line-y")
        st.plotly_chart(line_chart(df, x, y), use_container_width=True)
    else:
        st.info("Need a date column and a numeric column.")

with chart_tabs[5]:
    if nums:
        c1, c2 = st.columns(2)
        num = c1.selectbox("Numeric", nums, key="box-n")
        cat = c2.selectbox("Group by (optional)", ["—"] + cats, key="box-c")
        st.plotly_chart(box_plot(df, num, None if cat == "—" else cat), use_container_width=True)
    else:
        st.info("Need a numeric column.")

if st.button("🧪 Run Analytics →", type="primary", use_container_width=False):
    st.switch_page("pages/5_Analytics.py")        
