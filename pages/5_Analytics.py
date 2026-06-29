"""Analytics page — correlations, outliers, trends, distributions, insights."""
from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.loader import detect_column_roles  # noqa
from modules.analytics import (  # noqa
    correlation_matrix, strong_correlations,
    outliers_zscore, trend_analysis, distribution_stats,
)
from modules.cleaner import detect_outliers_iqr  # noqa
from modules.insights import generate_insights  # noqa

st.set_page_config(page_title="Analytics · DataLens AI", page_icon="🧪", layout="wide")
css = (ROOT / "assets" / "styles.css")
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

st.markdown("<span class='dl-tag'>Step 05</span>", unsafe_allow_html=True)
st.title("🧪 Analytics")
st.caption("Statistical analysis & smart insights — automated from your data.")

# ✅ Fixed: safe DataFrame check (no 'or' on DataFrame)
df = st.session_state.get("df_clean")
if df is None:
    df = st.session_state.get("df")
if df is None:
    st.warning("No dataset loaded. Go to **Upload Data** first.")
    st.stop()

roles = detect_column_roles(df)
nums, cats, dates = roles["numeric"], roles["categorical"], roles["date"]

tabs = st.tabs(["🧠 Smart insights", "🔗 Correlation", "📦 Outliers", "📈 Trend", "📊 Distribution"])

with tabs[0]:
    import re
    ins = generate_insights(df, max_insights=10)
    st.markdown("### 💡 Automated findings")
    icons = ["📊","🏆","🔗","📈","⚠️","💡","🎯","📉","🔍","✅"]
    colors = ["#22d3ee","#a78bfa","#f472b6","#fbbf24","#34d399",
              "#60a5fa","#f87171","#c084fc","#facc15","#4ade80"]
    for i, item in enumerate(ins, 1):
        clean = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', item)
        color = colors[(i-1) % len(colors)]
        icon = icons[(i-1) % len(icons)]
        st.markdown(f"""
        <div style='
            background: rgba(18,26,51,0.6);
            border: 1px solid {color}40;
            border-left: 4px solid {color};
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 10px;
            display: flex;
            align-items: flex-start;
            gap: 14px;
        '>
            <div style='font-size:22px;margin-top:2px'>{icon}</div>
            <div>
                <div style='color:#64748b;font-size:10px;letter-spacing:0.1em;
                            text-transform:uppercase;margin-bottom:4px'>
                    Insight {i:02d}
                </div>
                <div style='color:#e6edf3;font-size:14px;line-height:1.6'>{clean}</div>
            </div>
        </div>""", unsafe_allow_html=True)
        

with tabs[1]:
    corr = correlation_matrix(df)
    if corr.empty:
        st.info("Need at least 2 numeric columns.")
    else:
        fig = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale=[
                (0.0, "#f472b6"), (0.5, "#0b1020"), (1.0, "#22d3ee"),
            ],
            zmin=-1, zmax=1, template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=520, margin=dict(l=10, r=10, t=30, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        sc = strong_correlations(df, threshold=0.5)
        if sc:
            st.markdown("#### Strong correlations (|r| ≥ 0.5)")
            for c in sc[:10]:
                arrow = "↗" if c["corr"] > 0 else "↘"
                st.markdown(
                    f"<div class='dl-card' style='margin-bottom:8px'>"
                    f"<b>{c['a']}</b> {arrow} <b>{c['b']}</b> · "
                    f"r = <b style='color:#67e8f9'>{c['corr']}</b></div>",
                    unsafe_allow_html=True,
                )

with tabs[2]:
    sel = st.multiselect("Numeric columns", nums, default=nums[:5])
    if sel:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### IQR method")
            st.dataframe(detect_outliers_iqr(df, sel), use_container_width=True)
        with c2:
            st.markdown("#### Z-score method (|z| > 3)")
            st.dataframe(outliers_zscore(df, sel), use_container_width=True)

with tabs[3]:
    if dates and nums:
        c1, c2 = st.columns(2)
        d = c1.selectbox("Date column", dates, key="trend-date")
        n = c2.selectbox("Numeric column", nums, key="trend-num")
        t = trend_analysis(df, d, n)
        if not t:
            st.info("Not enough data to analyze trend.")
        else:
            color = "#22d3ee" if t["direction"] == "Growth" else ("#f472b6" if t["direction"] == "Decline" else "#fbbf24")
            st.markdown(
                f"<div class='dl-card'>"
                f"<div style='font-size:14px;color:#94a3b8'>Trend over <b>{d}</b></div>"
                f"<div style='font-size:36px;font-weight:800;color:{color};margin:6px 0'>"
                f"{t['direction']} · {t['growth_pct']:+.2f}%</div>"
                f"<div style='color:#cbd5e1'>"
                f"First half mean: <b>{t['first_half_mean']:,.2f}</b> &nbsp;·&nbsp; "
                f"Second half mean: <b>{t['second_half_mean']:,.2f}</b> &nbsp;·&nbsp; "
                f"Seasonality index: <b>{t['seasonality_idx']}</b>"
                f"</div></div>",
                unsafe_allow_html=True,
            )
            import pandas as pd
            d_df = df[[d, n]].dropna().copy()
            d_df[d] = pd.to_datetime(d_df[d], errors="coerce")
            d_df = d_df.dropna().sort_values(d)
            fig = px.line(d_df, x=d, y=n, template="plotly_dark",
                          color_discrete_sequence=["#22d3ee"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(255,255,255,0.02)",
                              font=dict(color="#e6edf3"),
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need a date column and a numeric column for trend analysis.")

with tabs[4]:
    sel = st.multiselect("Numeric columns", nums, default=nums[:6], key="dist-sel")
    if sel:
        st.dataframe(distribution_stats(df, sel), use_container_width=True)

if st.button("🤖 Ask Assistant →", type="primary", use_container_width=False):
    st.switch_page("pages/6_Data_Analyst_Assistant.py")