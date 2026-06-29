"""Data Analyst Assistant — conversational, context-aware, Groq-powered."""
from __future__ import annotations
import os
import json
import pandas as pd

from .analytics import strong_correlations, trend_analysis
from .insights import generate_insights
from .loader import detect_column_roles, classify_dataset


def build_context(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {"error": "no dataset"}
    roles = detect_column_roles(df)
    nums, cats, dates = roles["numeric"], roles["categorical"], roles["date"]
    stats = {}
    for c in nums[:10]:
        s = df[c].dropna()
        if s.empty:
            continue
        stats[c] = {
            "mean": round(float(s.mean()), 3),
            "median": round(float(s.median()), 3),
            "min": round(float(s.min()), 3),
            "max": round(float(s.max()), 3),
            "std": round(float(s.std()), 3) if len(s) > 1 else 0.0,
            "sum": round(float(s.sum()), 3),
        }
    top_cats = {}
    for c in cats[:5]:
        vc = df[c].value_counts(dropna=False).head(5)
        top_cats[c] = {str(k): int(v) for k, v in vc.items()}
    corrs = strong_correlations(df, threshold=0.5)[:6]
    trends = {}
    if dates and nums:
        for d in dates[:1]:
            for n in nums[:2]:
                t = trend_analysis(df, d, n)
                if t:
                    trends[f"{n}__by__{d}"] = t
    return {
        "kind": classify_dataset(df),
        "rows": int(len(df)),
        "columns": [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns],
        "numeric_stats": stats,
        "top_categories": top_cats,
        "strong_correlations": corrs,
        "trends": trends,
        "missing_total": int(df.isna().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
    }


def build_system_prompt(df: pd.DataFrame) -> str:
    context = build_context(df)
    return f"""You are DataLens AI, a friendly and expert data analyst assistant.

DATASET CONTEXT:
```json
{json.dumps(context, default=str)[:6000]}
```

PERSONALITY:
- Be warm, conversational, and friendly like a helpful colleague
- Respond naturally to greetings (hi, hello, thanks, etc.)
- Use casual language mixed with professional insight
- Use emojis occasionally to feel human (such as chart, trend, bulb, checkmark emojis)
- Keep answers concise but insightful

RESPONSE FORMAT:
- Use markdown: **bold** for column names and key numbers
- Use bullet points for lists of findings
- End data answers with one suggested follow-up question in italics like: *Want me to dig deeper into X?*
- For greetings or small talk, just respond naturally without a follow-up question

RULES:
- Never reveal the raw JSON context to the user
- If asked something unrelated to data, briefly answer then redirect to the dataset
- If you do not have enough context to answer precisely, say so honestly
- Always ground data answers in the context above, never invent numbers
"""


def stream_ai_answer(question: str, df: pd.DataFrame, history: list[dict]):
    """Generator that yields text chunks from Groq streaming."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        yield rule_based_answer(question, df)
        return

    try:
        from groq import Groq
    except ImportError:
        yield rule_based_answer(question, df)
        return

    messages = [{"role": "system", "content": build_system_prompt(df)}]
    for entry in history[-10:]:
        role = "user" if entry["role"] == "user" else "assistant"
        messages.append({"role": role, "content": entry["msg"]})
    messages.append({"role": "user", "content": question})

    try:
        client = Groq(api_key=api_key)
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=800,
            temperature=0.5,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta
    except Exception:
        yield rule_based_answer(question, df)


def ai_answer(question: str, df: pd.DataFrame, history: list[dict] | None = None) -> str:
    return "".join(stream_ai_answer(question, df, history or []))


def suggest_followups(answer: str) -> list[str]:
    if "correlation" in answer.lower():
        return ["Show me the outliers", "What is the trend over time?", "Who are the top performers?"]
    if "trend" in answer.lower() or "growth" in answer.lower():
        return ["What causes this trend?", "Show me correlations", "Who are the top performers?"]
    if "outlier" in answer.lower():
        return ["What are the key insights?", "Show me correlations", "How clean is my data?"]
    if "missing" in answer.lower() or "duplicate" in answer.lower():
        return ["What are the key insights?", "Which category performs best?", "Show me the trends"]
    return ["What are the key insights?", "Show me strong correlations", "Which category performs best?"]


def rule_based_answer(question: str, df: pd.DataFrame) -> str:
    q = (question or "").lower().strip()
    if not q:
        return "Please ask me something about your dataset! 😊"
    if df is None or df.empty:
        return "No dataset loaded yet. Please upload data first! 📤"

    greetings = ["hi", "hello", "hey", "howdy", "sup"]
    thanks = ["thank", "thanks", "thank you", "cheers", "great", "awesome", "nice", "cool"]
    if any(q == g or q.startswith(g + " ") for g in greetings):
        return "Hey there! 👋 I am DataLens AI, your data analyst assistant. Ask me anything about your dataset — insights, trends, correlations, outliers, you name it! 📊"
    if any(t in q for t in thanks):
        return "Happy to help! 😊 Got more questions about your data? I am here!"

    roles = detect_column_roles(df)
    nums, cats, dates = roles["numeric"], roles["categorical"], roles["date"]

    if any(k in q for k in ["overview", "summary", "describe", "about this"]):
        return (
            f"This looks like a **{classify_dataset(df)}** with **{len(df):,} rows** and **{df.shape[1]} columns**. 📋\n\n"
            f"- 🔢 **{len(nums)}** numeric columns\n"
            f"- 🏷️ **{len(cats)}** categorical columns\n"
            f"- 📅 **{len(dates)}** date columns\n\n"
            f"*Want me to surface the key insights?*"
        )

    if "missing" in q or "null" in q:
        miss = df.isna().sum().sort_values(ascending=False)
        miss = miss[miss > 0].head(5)
        if miss.empty:
            return "✅ No missing values — your dataset is clean!"
        lines = "\n".join(f"- **{c}**: {int(v)} missing ({v/len(df)*100:.1f}%)" for c, v in miss.items())
        return f"Columns with missing values:\n\n{lines}\n\n*Want me to suggest cleaning strategies?*"

    if "duplicate" in q:
        d = int(df.duplicated().sum())
        if d == 0:
            return "✅ No duplicate rows found!"
        return f"Found **{d}** duplicate rows ({d/len(df)*100:.2f}%). *Want to know which columns cause this?*"

    if any(k in q for k in ["correlation", "correlate", "related", "relationship"]):
        sc = strong_correlations(df, threshold=0.5)[:6]
        if not sc:
            return "No strong correlations (|r| >= 0.5) found between numeric columns."
        lines = "\n".join(f"- **{c['a']}** and **{c['b']}**: r = {c['corr']}" for c in sc)
        return f"Strongest correlations:\n\n{lines}\n\n*Want me to explain what any of these mean?*"

    if any(k in q for k in ["trend", "growth", "over time", "decline"]):
        if not (dates and nums):
            return "I need at least one date and one numeric column for trend analysis. 📅"
        t = trend_analysis(df, dates[0], nums[0])
        if not t:
            return "Not enough data points to derive a trend."
        emoji = "📈" if t["direction"] == "Growth" else ("📉" if t["direction"] == "Decline" else "➡️")
        return (
            f"{emoji} **{nums[0]}** over **{dates[0]}**: **{t['direction']}** "
            f"({t['growth_pct']:+.2f}% first vs second half).\n\n"
            f"*Want to dig into what is driving this?*"
        )

    if any(k in q for k in ["best", "top", "highest", "max", "winner"]):
        if nums and cats:
            num, cat = nums[0], cats[0]
            g = df.groupby(cat, dropna=False)[num].sum().sort_values(ascending=False).head(5)
            lines = "\n".join(f"- **{k}**: {v:,.2f}" for k, v in g.items())
            return f"🏆 Top **{cat}** by **{num}**:\n\n{lines}\n\n*Want to compare against the average?*"

    if any(k in q for k in ["worst", "bottom", "lowest", "min"]):
        if nums and cats:
            num, cat = nums[0], cats[0]
            g = df.groupby(cat, dropna=False)[num].sum().sort_values(ascending=True).head(5)
            lines = "\n".join(f"- **{k}**: {v:,.2f}" for k, v in g.items())
            return f"📉 Bottom **{cat}** by **{num}**:\n\n{lines}"

    if any(k in q for k in ["outlier", "anomaly", "anomalies"]):
        lines = []
        for c in nums[:3]:
            s = df[c].dropna()
            if len(s) < 10:
                continue
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            out = ((df[c] < q1 - 1.5*iqr) | (df[c] > q3 + 1.5*iqr)).sum()
            lines.append(f"- **{c}**: {int(out)} outliers ({out/len(df)*100:.2f}%)")
        if not lines:
            return "✅ No significant outliers found!"
        return "🔍 Outliers (IQR method):\n\n" + "\n".join(lines) + "\n\n*Want advice on handling these?*"

    if any(k in q for k in ["insight", "key", "important", "findings", "tell me"]):
        ins = generate_insights(df, 6)
        lines = "\n".join(f"- {i}" for i in ins)
        return f"💡 **Key insights:**\n\n{lines}\n\n*Which would you like to explore further?*"

    for c in df.columns:
        if str(c).lower() in q:
            s = df[c]
            if pd.api.types.is_numeric_dtype(s):
                return (
                    f"📊 **{c}** stats:\n\n"
                    f"- Mean: **{s.mean():,.2f}**\n"
                    f"- Median: **{s.median():,.2f}**\n"
                    f"- Min: **{s.min():,.2f}** · Max: **{s.max():,.2f}**\n"
                    f"- Missing: **{int(s.isna().sum())}**\n\n"
                    f"*Want to see the distribution or outliers for this column?*"
                )
            vc = s.value_counts(dropna=False).head(5)
            lines = "\n".join(f"- **{k}**: {v}" for k, v in vc.items())
            return f"🏷️ Top values in **{c}**:\n\n{lines}"

    return (
        "Hmm, I am not sure about that one — could you rephrase? 🤔\n\n"
        "I can help with: **insights**, **trends**, **correlations**, **outliers**, "
        "**missing values**, **top/bottom performers**, or stats on any specific column!"
    )
