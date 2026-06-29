"""DataLens AI — main landing page."""
from __future__ import annotations
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="DataLens AI — Data Analysis Workspace",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS_PATH = Path(__file__).parent / "assets" / "styles.css"
if CSS_PATH.exists():
    st.markdown(f"<style>{CSS_PATH.read_text()}</style>", unsafe_allow_html=True)

defaults = {
    "df": None,
    "df_clean": None,
    "filename": None,
    "filesize": 0,
    "dataset_kind": None,
    "ai_enabled": False,
    "chat_history": [],
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### DataLens **AI**")
    st.caption("Interactive data analysis workspace")
    st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)

    if st.session_state.df is not None:
        df = st.session_state.df
        st.markdown(
            "<div class='dl-pill'><span class='dot'></span> Dataset loaded</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"**{st.session_state.filename or 'dataset'}**")
        st.caption(f"{len(df):,} rows · {df.shape[1]} columns")
    else:
        st.info("No dataset loaded. Head to **Upload Data**.")

    st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)
    st.markdown("#### 🤖 AI Assistant")
    st.session_state.ai_enabled = st.toggle(
        "Enable AI Analysis",
        value=st.session_state.ai_enabled,
        help="Uses Groq API (llama-3.3-70b-versatile) for natural-language insights.",
    )
    if st.session_state.ai_enabled and not os.environ.get("GROQ_API_KEY"):
        st.warning("GROQ_API_KEY not set in .env — get a free key at console.groq.com")

    with st.expander("Custom Groq API Key (optional)"):
        custom = st.text_input(
            "Groq API Key", value="", type="password",
            help="Overrides the key in .env for this session.",
        )
        if custom:
            os.environ["GROQ_API_KEY"] = custom
            st.success("Key applied for this session.")

    st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)
    st.caption("v1.0.0 · MVP")


# ---------- platform heading ----------
st.markdown("""
<div style="text-align:center; padding: 6px 0 18px 0;">
    <span style="
        font-size: 48px;
        font-weight: 900;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #22d3ee, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    ">🔭 DataLens AI</span>
    <div style="color:#475569; font-size:13px; letter-spacing:0.12em; text-transform:uppercase; margin-top:6px;">
        Interactive Data Analysis Workspace
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- hero ----------
st.markdown("""
<div class="dl-hero">
  <span class="dl-tag">Data Analysis · Visualization · Insights</span>
  <h1>See what your data is trying to tell you</h1>
  <p>DataLens AI is an interactive workspace that turns raw spreadsheets into clean dashboards, statistical
  insights, and executive reports — without writing a single line of code. Upload a dataset, explore it,
  ask questions in plain English, and export a board-ready PDF.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

c1, c2, c3, c4 = st.columns(4)
for col, label, value, sub in [
    (c1, "Step 01", "Upload", "CSV · XLSX · XLS"),
    (c2, "Step 02", "Profile", "Health score & shape"),
    (c3, "Step 03", "Analyze", "Stats · Trends · Outliers"),
    (c4, "Step 04", "Report", "One-click PDF export"),
]:
    with col:
        st.markdown(
            f"""<div class='dl-kpi'>
                <div class='label'>{label}</div>
                <div class='value'>{value}</div>
                <div class='sub'>{sub}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.write("")
st.write("")

left, right = st.columns([1.1, 1])
with left:
    st.markdown("### 🚀 Quick start")
    st.markdown("""
1. **Upload Data** — drop a CSV or Excel file.
2. **Data Profiling** — review shape, missing values, and health score.
3. **Data Cleaning** — fix missing values, drop duplicates, convert types.
4. **Dashboard** — auto-generated KPI cards and interactive Plotly charts.
5. **Analytics** — correlation matrix, outliers, distributions, trends.
6. **Data Analyst Assistant** — ask questions in natural language.
7. **Report Generator** — export an executive PDF.
    """)
    cta1, cta2 = st.columns([1, 1])
    with cta1:
        if st.button("📤 Upload a dataset", use_container_width=True, key="cta-upload"):
            st.switch_page("pages/1_Upload_Data.py")
    with cta2:
        if st.button("🎯 Try sample data", use_container_width=True, key="cta-sample"):
            import pandas as pd
            sample_path = Path(__file__).parent / "data" / "sample_sales.csv"
            if sample_path.exists():
                df = pd.read_csv(sample_path)
                st.session_state.df = df
                st.session_state.df_clean = df.copy()
                st.session_state.filename = "sample_sales.csv"
                st.session_state.filesize = sample_path.stat().st_size
                from modules.loader import classify_dataset
                st.session_state.dataset_kind = classify_dataset(df)
                st.success("Sample dataset loaded — open **Data Profiling** in the sidebar.")
            else:
                st.error("Sample dataset not found.")

with right:
    st.markdown("### ✨ What you get")
    st.markdown("""
- **Smart Insight Engine** that explains *why* a number matters.
- **Dataset Intelligence** — auto-classifies sales / HR / finance / marketing / customer / job-market data.
- **Groq-powered AI Assistant** — privacy-safe; never sends your raw dataframe.
- **Streamlit caching** for snappy interaction on 100k+ rows.
    """)
    if st.session_state.df is not None:
        st.success(f"Active dataset: **{st.session_state.filename}** "
                   f"({len(st.session_state.df):,} rows)")
