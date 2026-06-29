"""Data Cleaning page."""
from __future__ import annotations
import sys
import time
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.cleaner import (  # noqa
    fill_missing, drop_missing, remove_duplicates, convert_dtype, detect_outliers_iqr,
)

st.set_page_config(page_title="Cleaning · DataLens AI", page_icon="🧹", layout="wide")
css = (ROOT / "assets" / "styles.css")
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

# toast notification helper
def toast(msg: str, icon: str = "✅"):
    st.toast(msg, icon=icon)

st.markdown("<span class='dl-tag'>Step 03</span>", unsafe_allow_html=True)
st.title("🧹 Data Cleaning")
st.caption("Fix missing values, drop duplicates, convert types — interactively.")

if st.session_state.get("df") is None:
    st.warning("No dataset loaded. Go to **Upload Data** first.")
    st.stop()

if st.session_state.get("df_clean") is None:
    st.session_state.df_clean = st.session_state.df.copy()

df = st.session_state.df_clean

c1, c2, c3 = st.columns(3)
c1.metric("Rows", f"{len(df):,}")
c2.metric("Missing", f"{int(df.isna().sum().sum()):,}")
c3.metric("Duplicates", f"{int(df.duplicated().sum()):,}")

st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)

tabs = st.tabs(["🧩 Missing values", "🗑️ Duplicates", "🔀 Data types", "📦 Outliers (IQR)", "👀 Preview"])

with tabs[0]:
    cols = st.multiselect("Apply to columns", options=df.columns.tolist(),
                          default=[c for c in df.columns if df[c].isna().any()])
    strategy = st.radio(
        "Strategy", ["mean", "median", "mode", "zero", "unknown", "drop rows", "drop columns"],
        horizontal=True,
    )
    if st.button("✅ Apply", key="apply-missing", use_container_width=False):
        if not cols:
            st.toast("No columns selected!", icon="⚠️")
        else:
            with st.spinner("Applying..."):
                time.sleep(0.3)
                if strategy == "drop rows":
                    st.session_state.df_clean = drop_missing(df, cols, "rows")
                elif strategy == "drop columns":
                    st.session_state.df_clean = drop_missing(df, cols, "columns")
                else:
                    st.session_state.df_clean = fill_missing(df, cols, strategy)
            st.toast(f"✅ Applied '{strategy}' on {len(cols)} column(s)!", icon="✅")
            time.sleep(0.5)
            st.rerun()

with tabs[1]:
    dup_count = int(df.duplicated().sum())
    st.write(f"Detected **{dup_count}** duplicate rows.")
    if st.button("🗑️ Remove duplicates", key="apply-dups", use_container_width=False):
        if dup_count == 0:
            st.toast("No duplicates found!", icon="ℹ️")
        else:
            with st.spinner("Removing duplicates..."):
                time.sleep(0.3)
                st.session_state.df_clean = remove_duplicates(df)
            st.toast(f"🗑️ Removed {dup_count} duplicate rows!", icon="✅")
            time.sleep(0.5)
            st.rerun()

with tabs[2]:
    cols = st.multiselect("Columns to convert", options=df.columns.tolist(), key="conv-cols")
    target = st.radio("Convert to", ["numeric", "datetime", "string"], horizontal=True)
    if st.button("🔀 Convert", key="apply-conv", use_container_width=False):
        if not cols:
            st.toast("No columns selected!", icon="⚠️")
        else:
            with st.spinner("Converting..."):
                time.sleep(0.3)
                st.session_state.df_clean = convert_dtype(df, cols, target)
            st.toast(f"🔀 Converted {len(cols)} column(s) to {target}!", icon="✅")
            time.sleep(0.5)
            st.rerun()

with tabs[3]:
    nums = df.select_dtypes(include="number").columns.tolist()
    sel = st.multiselect("Numeric columns", nums, default=nums[:5])
    if sel:
        out_df = detect_outliers_iqr(df, sel)
        st.dataframe(out_df, use_container_width=True)
    else:
        st.info("Select at least one numeric column.")

with tabs[4]:
    st.dataframe(df.head(50), use_container_width=True, height=420)

st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)
left, right = st.columns([1, 1])
with left:
    csv = st.session_state.df_clean.to_csv(index=False).encode("utf-8")
    if st.download_button(
        "⬇️ Export cleaned CSV", csv,
        file_name=f"cleaned_{st.session_state.get('filename') or 'dataset.csv'}",
        mime="text/csv", use_container_width=True,
    ):
        st.toast("⬇️ CSV exported successfully!", icon="✅")

with right:
    if st.button("↩️ Reset to original", use_container_width=True):
        with st.spinner("Resetting..."):
            time.sleep(0.4)
            st.session_state.df_clean = st.session_state.df.copy()
        st.toast("↩️ Dataset reset to original!", icon="✅")
        time.sleep(0.5)
        st.rerun()

if st.button("📊 View Dashboard →", type="primary", use_container_width=False):
    st.switch_page("pages/4_Dashboard.py")        