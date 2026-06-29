"""Data profiling module."""
from __future__ import annotations
import pandas as pd
import numpy as np


def basic_metrics(df: pd.DataFrame) -> dict:
    missing_total = int(df.isna().sum().sum())
    cells = int(df.shape[0] * df.shape[1]) or 1
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing": missing_total,
        "missing_pct": round(missing_total / cells * 100, 2),
        "duplicates": int(df.duplicated().sum()),
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 3),
    }


def column_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n = len(df) or 1
    for col in df.columns:
        s = df[col]
        rows.append({
            "Column": str(col),
            "Type": str(s.dtype),
            "Missing": int(s.isna().sum()),
            "Missing %": round(s.isna().sum() / n * 100, 2),
            "Unique": int(s.nunique(dropna=True)),
            "Sample": str(s.dropna().head(1).tolist()[:1])[1:-1][:60] if s.notna().any() else "",
        })
    return pd.DataFrame(rows)


def dtype_distribution(df: pd.DataFrame) -> pd.DataFrame:
    counts = df.dtypes.astype(str).value_counts().reset_index()
    counts.columns = ["dtype", "count"]
    return counts


def health_score(df: pd.DataFrame) -> tuple[int, dict]:
    """Score 0..100 from missing %, duplicate %, consistency."""
    if df is None or df.empty:
        return 0, {"missing": 0, "duplicates": 0, "consistency": 0}
    n = len(df)
    missing_pct = df.isna().sum().sum() / (df.shape[0] * df.shape[1] or 1)
    dup_pct = df.duplicated().sum() / (n or 1)
    mixed = 0
    for c in df.columns:
        if df[c].dtype == "object":
            try:
                types = set(type(v).__name__ for v in df[c].dropna().head(200))
                if len(types) > 1:
                    mixed += 1
            except Exception:  # noqa: BLE001
                pass
    consistency_pct = mixed / (df.shape[1] or 1)
    miss_score = max(0, 100 - missing_pct * 200)
    dup_score = max(0, 100 - dup_pct * 200)
    cons_score = max(0, 100 - consistency_pct * 100)
    overall = int(round(0.5 * miss_score + 0.3 * dup_score + 0.2 * cons_score))
    return max(0, min(100, overall)), {
        "missing": round(miss_score, 1),
        "duplicates": round(dup_score, 1),
        "consistency": round(cons_score, 1),
    }


def missing_heatmap_data(df: pd.DataFrame, max_rows: int = 500) -> np.ndarray:
    sample = df.head(max_rows) if len(df) > max_rows else df
    return sample.isna().astype(int).to_numpy()
