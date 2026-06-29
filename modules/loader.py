"""Dataset loader and intelligence module."""
from __future__ import annotations
import io
import os
from typing import Optional, Tuple
import pandas as pd


SUPPORTED_EXT = {".csv", ".xlsx", ".xls"}


def load_dataframe(uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
    """Load a CSV/XLS/XLSX from a Streamlit UploadedFile-like object."""
    name = getattr(uploaded_file, "name", "uploaded")
    ext = os.path.splitext(name)[1].lower()
    if ext not in SUPPORTED_EXT:
        return None, f"Unsupported file type: {ext}. Use CSV, XLS, or XLSX."
    try:
        raw = uploaded_file.read()
        buf = io.BytesIO(raw)
        if ext == ".csv":
            try:
                df = pd.read_csv(buf)
            except UnicodeDecodeError:
                buf.seek(0)
                df = pd.read_csv(buf, encoding="latin-1")
        else:
            df = pd.read_excel(buf)
    except Exception as e:  # noqa: BLE001
        return None, f"Failed to parse file: {e}"
    return df, "ok"


def classify_dataset(df: pd.DataFrame) -> str:
    """Heuristically classify the dataset domain from column names."""
    if df is None or df.empty:
        return "Generic Dataset"
    cols = [c.lower() for c in df.columns]
    text = " ".join(cols)

    rules = [
        ("Sales Dataset",     ["sales", "revenue", "order", "quantity", "product", "discount"]),
        ("Financial Dataset", ["profit", "expense", "balance", "asset", "liability", "cash", "ledger"]),
        ("HR Dataset",        ["employee", "salary", "department", "hire", "attrition", "tenure"]),
        ("Marketing Dataset", ["campaign", "ctr", "impression", "click", "conversion", "channel"]),
        ("Customer Dataset",  ["customer", "churn", "segment", "ltv", "subscription", "satisfaction"]),
        ("Job Market Dataset",["job", "title", "experience", "remote", "company", "role"]),
    ]
    best, score = "Generic Dataset", 0
    for label, kws in rules:
        s = sum(1 for k in kws if k in text)
        if s > score:
            best, score = label, s
    return best if score >= 2 else "Generic Dataset"


def detect_column_roles(df: pd.DataFrame) -> dict:
    """Return numeric, categorical, and date columns."""
    numeric = df.select_dtypes(include="number").columns.tolist()
    date_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    for col in df.columns:
        if col in date_cols or col in numeric:
            continue
        lc = str(col).lower()
        if any(t in lc for t in ("date", "time", "year", "month", "day")):
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().mean() > 0.7:
                    date_cols.append(col)
            except Exception:  # noqa: BLE001
                pass
    categorical = [c for c in df.columns if c not in numeric and c not in date_cols]
    return {"numeric": numeric, "categorical": categorical, "date": date_cols}
