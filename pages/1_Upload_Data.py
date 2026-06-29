"""Upload Data page."""
from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.loader import load_dataframe, classify_dataset, detect_column_roles  # noqa

st.set_page_config(page_title="Upload Data · DataLens AI", page_icon="📤", layout="wide")
css = (ROOT / "assets" / "styles.css")
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

st.markdown("<span class='dl-tag'>Step 01</span>", unsafe_allow_html=True)
st.title("📤 Upload Data")
st.caption("Drop a CSV, XLSX, or XLS file to start your analysis.")

left, right = st.columns([1.2, 1])

with left:
    uploaded = st.file_uploader(
        "Choose a file", type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
        help="Supported: CSV, XLSX, XLS. Max 200 MB.",
    )

    if uploaded is not None:
        df, msg = load_dataframe(uploaded)
        if df is None:
            st.error(msg)
        else:
            st.session_state.df = df
            st.session_state.df_clean = df.copy()
            st.session_state.filename = uploaded.name
            st.session_state.filesize = uploaded.size
            st.session_state.dataset_kind = classify_dataset(df)
            try:
                (ROOT / "uploads").mkdir(exist_ok=True)
                with open(ROOT / "uploads" / uploaded.name, "wb") as f:
                    uploaded.seek(0)
                    f.write(uploaded.read())
            except Exception:  # noqa: BLE001
                pass
            st.success(f"Loaded **{uploaded.name}** successfully.")

with right:
    st.markdown("#### Try sample data")
    if st.button("🎯 Load sample sales dataset", use_container_width=True):
        import pandas as pd
        sample = ROOT / "data" / "sample_sales.csv"
        if sample.exists():
            df = pd.read_csv(sample)
            st.session_state.df = df
            st.session_state.df_clean = df.copy()
            st.session_state.filename = "sample_sales.csv"
            st.session_state.filesize = sample.stat().st_size
            st.session_state.dataset_kind = classify_dataset(df)
            st.success("Sample dataset loaded.")
        else:
            st.error("Sample file missing.")


df = st.session_state.get("df")
if df is not None:
    st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)
    st.markdown("### Dataset preview")

    cols = st.columns(4)
    metrics = [
        ("File", st.session_state.filename or "—", ""),
        ("Size", f"{(st.session_state.filesize or 0)/1024:,.1f} KB", ""),
        ("Rows", f"{len(df):,}", ""),
        ("Columns", f"{df.shape[1]}", st.session_state.dataset_kind or ""),
    ]
    for col, (label, value, sub) in zip(cols, metrics):
        with col:
            st.markdown(
                f"<div class='dl-kpi'><div class='label'>{label}</div>"
                f"<div class='value'>{value}</div><div class='sub'>{sub}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("")
    st.markdown("#### First 10 rows")
    st.dataframe(df.head(10), use_container_width=True, height=360)

    roles = detect_column_roles(df)
    st.markdown(
        f"<div class='dl-card'>📊 Detected: "
        f"<b style='color:#67e8f9'>{len(roles['numeric'])}</b> numeric, "
        f"<b style='color:#c4b5fd'>{len(roles['categorical'])}</b> categorical, "
        f"<b style='color:#f9a8d4'>{len(roles['date'])}</b> date columns. "
        f"Likely dataset type: <b>{st.session_state.dataset_kind}</b>.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("")
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("🔬 Analyze Dataset", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Data_Profiling.py")
else:
    st.info("👆 Upload a file to get started, or load the sample dataset on the right.")
