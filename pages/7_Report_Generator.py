"""Report Generator page."""
from __future__ import annotations
import sys
from datetime import datetime
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.profiler import basic_metrics, health_score  # noqa
from modules.insights import generate_insights  # noqa
from modules.loader import detect_column_roles, classify_dataset  # noqa
from modules.dashboard import kpi_for_numeric  # noqa
from modules.reporting import build_report  # noqa

st.set_page_config(page_title="Reports · DataLens AI", page_icon="📑", layout="wide")
css = (ROOT / "assets" / "styles.css")
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

st.markdown("<span class='dl-tag'>Step 07</span>", unsafe_allow_html=True)
st.title("📑 Report Generator")
st.caption("Generate a board-ready executive PDF in one click.")

# ✅ Fixed: safe DataFrame check (no 'or' on DataFrame)
df = st.session_state.get("df_clean")
if df is None:
    df = st.session_state.get("df")
if df is None:
    st.warning("No dataset loaded. Go to **Upload Data** first.")
    st.stop()

dataset_name = st.session_state.get("filename") or "dataset.csv"
kind = st.session_state.get("dataset_kind") or classify_dataset(df)
metrics = basic_metrics(df)
score = health_score(df)
insights = generate_insights(df, max_insights=6)

roles = detect_column_roles(df)
kpis = {n: kpi_for_numeric(df, n) for n in roles["numeric"][:8]}

recs = []
if metrics["missing_pct"] > 5:
    recs.append("Address missing values — consider imputation or row removal for high-missing columns.")
if metrics["duplicates"] > 0:
    recs.append(f"Remove {metrics['duplicates']:,} duplicate rows to improve data quality.")
if score[0] < 75:
    recs.append("Run a cleaning pass on the dataset to raise the health score above 75.")
if roles["date"] and roles["numeric"]:
    recs.append(f"Schedule recurring trend reviews on {roles['date'][0]} vs {roles['numeric'][0]}.")
if not recs:
    recs.append("Dataset is healthy — proceed with deeper segment-level analysis or modeling.")

left, right = st.columns([1, 1])
with left:
    st.markdown(
        f"""<div class='dl-card'>
            <div class='dl-tag'>Report preview</div>
            <h3 style='margin:8px 0 6px 0'>DataLens AI — Executive Report</h3>
            <div style='color:#94a3b8'>Dataset: <b>{dataset_name}</b> · Type: <b>{kind}</b></div>
            <div style='color:#94a3b8'>Generated: {datetime.now().strftime('%B %d, %Y · %H:%M')}</div>
            <hr style='border-color:rgba(255,255,255,0.08)'/>
            <div><b>{metrics['rows']:,}</b> rows · <b>{metrics['columns']}</b> columns · health <b>{score[0]}/100</b></div>
            <div style='color:#94a3b8;margin-top:8px'>Sections: Executive Summary · Dataset Overview · KPI Summary · Key Findings · Recommendations · Appendix</div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Top recommendations")
    for r in recs:
        st.markdown(f"- {r}")

with right:
    st.markdown("#### Key findings (preview)")
    for i, ins in enumerate(insights[:6], 1):
        st.markdown(
            f"<div class='dl-card' style='margin-bottom:8px'>"
            f"<span class='dl-tag'>Finding {i:02d}</span>"
            f"<div style='margin-top:8px'>{ins}</div></div>",
            unsafe_allow_html=True,
        )

st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)

if st.button("📑 Generate executive PDF", type="primary", use_container_width=True):
    with st.spinner("Building report…"):
        pdf = build_report(
            df=df, dataset_name=dataset_name, kind=kind,
            metrics=metrics, insights=insights, health=score,
            kpis=kpis, recommendations=recs,
        )
        (ROOT / "reports").mkdir(exist_ok=True)
        fname = f"datalens_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        out = ROOT / "reports" / fname
        out.write_bytes(pdf)
    st.success(f"Report ready · saved to /reports/{fname}")
    st.download_button(
        "⬇️ Download PDF", data=pdf, file_name=fname,
        mime="application/pdf", use_container_width=True,
    )
