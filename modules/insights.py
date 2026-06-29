"""Smart insight generation — human-readable findings."""
from __future__ import annotations
import pandas as pd
import numpy as np
from .analytics import strong_correlations, trend_analysis
from .loader import detect_column_roles


def _fmt(n: float) -> str:
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.2f}K"
    if abs(n) >= 1:
        return f"{n:,.2f}"
    return f"{n:.3f}"


def generate_insights(df: pd.DataFrame, max_insights: int = 10) -> list[str]:
    """Return a list of human-readable insight strings."""
    insights: list[str] = []
    if df is None or df.empty:
        return ["Dataset is empty."]

    roles = detect_column_roles(df)
    nums, cats, dates = roles["numeric"], roles["categorical"], roles["date"]

    insights.append(
        f"Dataset contains **{len(df):,} rows** and **{df.shape[1]} columns** "
        f"({len(nums)} numeric, {len(cats)} categorical, {len(dates)} date)."
    )

    miss = df.isna().sum().sum()
    if miss:
        pct = miss / (df.shape[0] * df.shape[1]) * 100
        worst = df.isna().sum().sort_values(ascending=False).head(1)
        if not worst.empty and worst.iloc[0] > 0:
            insights.append(
                f"There are **{int(miss):,} missing values** ({pct:.2f}% of cells). "
                f"Column **{worst.index[0]}** has the most ({int(worst.iloc[0])} missing)."
            )

    for cat in cats[:2]:
        s = df[cat].dropna()
        if s.empty or s.nunique() < 2 or s.nunique() > 200:
            continue
        top = s.value_counts(normalize=True).head(1)
        if not top.empty:
            insights.append(
                f"Category **{top.index[0]}** in column **{cat}** dominates with "
                f"**{top.iloc[0]*100:.1f}%** of records."
            )

    if nums and cats:
        num = nums[0]
        for cat in cats[:1]:
            if df[cat].nunique() < 2 or df[cat].nunique() > 50:
                continue
            grouped = df.groupby(cat, dropna=False)[num].sum().sort_values(ascending=False)
            if grouped.empty:
                continue
            total = grouped.sum()
            best = grouped.head(1)
            worst = grouped.tail(1)
            if total:
                insights.append(
                    f"**{best.index[0]}** contributes **{best.iloc[0]/total*100:.1f}%** "
                    f"of total **{num}** ({_fmt(float(best.iloc[0]))})."
                )
            if len(grouped) > 1 and total:
                insights.append(
                    f"**{worst.index[0]}** has the lowest **{num}** "
                    f"at {_fmt(float(worst.iloc[0]))} ({worst.iloc[0]/total*100:.1f}% of total)."
                )

    for c in strong_correlations(df, threshold=0.6)[:3]:
        direction = "positive" if c["corr"] > 0 else "negative"
        insights.append(
            f"Strong {direction} correlation between **{c['a']}** and **{c['b']}** "
            f"(r = {c['corr']})."
        )

    if dates and nums:
        t = trend_analysis(df, dates[0], nums[0])
        if t:
            sign = "+" if t["growth_pct"] >= 0 else ""
            insights.append(
                f"**{nums[0]}** shows a **{t['direction'].lower()}** trend over **{dates[0]}** "
                f"({sign}{t['growth_pct']}% between first and second halves)."
            )

    if nums:
        c = nums[0]
        s = df[c].dropna()
        if len(s) > 10:
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            out = ((df[c] < q1 - 1.5*iqr) | (df[c] > q3 + 1.5*iqr)).sum()
            if out:
                insights.append(
                    f"Column **{c}** contains **{int(out)}** statistical outliers "
                    f"(IQR rule), which is **{out/len(df)*100:.2f}%** of the data."
                )

    if nums and cats:
        num, cat = nums[0], cats[0]
        if df[cat].nunique() < 50:
            avg = df[num].mean()
            grp = df.groupby(cat, dropna=False)[num].mean()
            above = grp[grp > avg].sort_values(ascending=False)
            if not above.empty and avg:
                top = above.head(1)
                pct = (top.iloc[0] - avg) / abs(avg) * 100
                insights.append(
                    f"**{top.index[0]}** has **{num}** that is **{pct:.1f}% higher** "
                    f"than the overall average."
                )

    return insights[:max_insights] if len(insights) >= max_insights else insights
