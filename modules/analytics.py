"""Advanced analytics: correlations, outliers, trends, distributions."""
from __future__ import annotations
import pandas as pd
import numpy as np
from scipy import stats


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    nums = df.select_dtypes(include="number")
    if nums.shape[1] < 2:
        return pd.DataFrame()
    return nums.corr(numeric_only=True).round(3)


def strong_correlations(df: pd.DataFrame, threshold: float = 0.5) -> list[dict]:
    corr = correlation_matrix(df)
    out = []
    cols = corr.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            v = corr.iloc[i, j]
            if pd.notna(v) and abs(v) >= threshold:
                out.append({"a": cols[i], "b": cols[j], "corr": round(float(v), 3)})
    return sorted(out, key=lambda x: -abs(x["corr"]))


def outliers_zscore(df: pd.DataFrame, columns: list[str], z: float = 3.0) -> pd.DataFrame:
    rows = []
    for c in columns:
        s = df[c].dropna()
        if len(s) < 3 or s.std() == 0:
            continue
        zs = np.abs((s - s.mean()) / s.std())
        rows.append({
            "Column": c,
            "Mean": round(float(s.mean()), 3),
            "Std": round(float(s.std()), 3),
            f"|z|>{z}": int((zs > z).sum()),
        })
    return pd.DataFrame(rows)


def trend_analysis(df: pd.DataFrame, date_col: str, value_col: str) -> dict:
    d = df[[date_col, value_col]].dropna().copy()
    if d.empty:
        return {}
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d = d.dropna().sort_values(date_col)
    if len(d) < 4:
        return {}
    half = len(d) // 2
    first = d.iloc[:half][value_col].mean()
    last = d.iloc[half:][value_col].mean()
    growth = (last - first) / abs(first) * 100 if first else 0.0
    direction = "Growth" if growth > 2 else ("Decline" if growth < -2 else "Stable")
    d["month"] = d[date_col].dt.month
    monthly = d.groupby("month")[value_col].mean()
    seasonality = monthly.std() / (monthly.mean() or 1)
    return {
        "first_half_mean": round(float(first), 3),
        "second_half_mean": round(float(last), 3),
        "growth_pct": round(float(growth), 2),
        "direction": direction,
        "seasonality_idx": round(float(seasonality), 3),
        "n": int(len(d)),
    }


def distribution_stats(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rows = []
    for c in columns:
        s = df[c].dropna()
        if len(s) < 3:
            continue
        try:
            skew = float(stats.skew(s))
            kurt = float(stats.kurtosis(s))
        except Exception:  # noqa: BLE001
            continue
        shape = "Normal-ish"
        if skew > 1: shape = "Right-skewed"
        elif skew < -1: shape = "Left-skewed"
        rows.append({
            "Column": c,
            "Mean": round(float(s.mean()), 3),
            "Median": round(float(s.median()), 3),
            "Std": round(float(s.std()), 3),
            "Skewness": round(skew, 3),
            "Kurtosis": round(kurt, 3),
            "Shape": shape,
        })
    return pd.DataFrame(rows)
