"""Data cleaning utilities."""
from __future__ import annotations
import pandas as pd
import numpy as np


def fill_missing(df: pd.DataFrame, columns: list[str], strategy: str) -> pd.DataFrame:
    out = df.copy()
    for c in columns:
        if c not in out.columns:
            continue
        s = out[c]
        if strategy == "mean" and pd.api.types.is_numeric_dtype(s):
            out[c] = s.fillna(s.mean())
        elif strategy == "median" and pd.api.types.is_numeric_dtype(s):
            out[c] = s.fillna(s.median())
        elif strategy == "mode":
            m = s.mode(dropna=True)
            if not m.empty:
                out[c] = s.fillna(m.iloc[0])
        elif strategy == "zero" and pd.api.types.is_numeric_dtype(s):
            out[c] = s.fillna(0)
        elif strategy == "unknown":
            out[c] = s.fillna("Unknown")
    return out


def drop_missing(df: pd.DataFrame, columns: list[str], axis: str = "rows") -> pd.DataFrame:
    if axis == "rows":
        return df.dropna(subset=columns or None)
    return df.drop(columns=columns, errors="ignore")


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def convert_dtype(df: pd.DataFrame, columns: list[str], target: str) -> pd.DataFrame:
    out = df.copy()
    for c in columns:
        if c not in out.columns:
            continue
        try:
            if target == "numeric":
                out[c] = pd.to_numeric(out[c], errors="coerce")
            elif target == "datetime":
                out[c] = pd.to_datetime(out[c], errors="coerce")
            elif target == "string":
                out[c] = out[c].astype(str)
        except Exception:  # noqa: BLE001
            pass
    return out


def detect_outliers_iqr(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rows = []
    for c in columns:
        if c not in df.columns or not pd.api.types.is_numeric_dtype(df[c]):
            continue
        s = df[c].dropna()
        if s.empty:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        out = ((df[c] < lo) | (df[c] > hi)).sum()
        rows.append({
            "Column": c,
            "Q1": round(float(q1), 3),
            "Q3": round(float(q3), 3),
            "IQR": round(float(iqr), 3),
            "Lower Bound": round(float(lo), 3),
            "Upper Bound": round(float(hi), 3),
            "Outliers": int(out),
            "Outlier %": round(float(out) / len(df) * 100, 2),
        })
    return pd.DataFrame(rows)
