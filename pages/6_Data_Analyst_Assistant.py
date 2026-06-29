"""Data Analyst Assistant — live, streaming, conversational."""
from __future__ import annotations
import sys
import os
import time
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import importlib
_ast = importlib.import_module("modules.assistant")
rule_based_answer = _ast.rule_based_answer
stream_ai_answer = _ast.stream_ai_answer
suggest_followups = _ast.suggest_followups

st.set_page_config(page_title="Assistant · DataLens AI", page_icon="🤖", layout="wide")
css = (ROOT / "assets" / "styles.css")
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
/* chat layout */
.chat-wrap { display: flex; flex-direction: column; gap: 16px; padding-bottom: 10px; }

/* bot message row */
.msg-row { display: flex; gap: 12px; align-items: flex-start; width: 100%; }

/* user message row */
.msg-row.user { flex-direction: row-reverse; }

/* avatars */
.avatar {
    width: 38px; height: 38px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0; margin-top: 2px;
}
.avatar.bot  { background: linear-gradient(135deg,#22d3ee,#06b6d4); }
.avatar.user { background: linear-gradient(135deg,#a78bfa,#7c3aed); }

/* bubbles */
.bubble {
    padding: 12px 16px;
    border-radius: 18px;
    font-size: 14px;
    line-height: 1.65;
    word-wrap: break-word;
    word-break: break-word;
}

/* bot bubble — left aligned, takes natural width */
.bubble.bot {
    background: rgba(18,26,51,0.80);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px 18px 18px 18px;
    color: #e6edf3;
    max-width: 75%;
}

/* user bubble — right aligned, min width so short msgs dont squish */
.bubble.user {
    background: linear-gradient(135deg, rgba(167,139,250,0.25), rgba(124,58,237,0.15));
    border: 1px solid rgba(167,139,250,0.35);
    border-radius: 18px 4px 18px 18px;
    color: #e6edf3;
    max-width: 75%;
    min-width: 120px;
    text-align: left;
    white-space: normal;
    word-break: normal;
}

.name-lbl {
    font-size: 10px; color: #475569;
    letter-spacing: .07em; text-transform: uppercase;
    margin-bottom: 4px;
}

/* typing dots */
.typing-dot {
    display: inline-block; width: 7px; height: 7px;
    border-radius: 50%; background: #22d3ee; margin: 0 2px;
    animation: blink 1.2s infinite;
}
.typing-dot:nth-child(2){ animation-delay:.2s; }
.typing-dot:nth-child(3){ animation-delay:.4s; }
@keyframes blink { 0%,80%,100%{opacity:.2} 40%{opacity:1} }

/* follow-up buttons — purple style, different from cyan action buttons */
.fu-btn > div > button {
    background: rgba(167,139,250,0.12) !important;
    border: 1px solid rgba(167,139,250,0.35) !important;
    color: #c4b5fd !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    padding: 5px 14px !important;
    font-weight: 500 !important;
    transition: all .2s !important;
    white-space: nowrap !important;
}
.fu-btn > div > button:hover {
    background: rgba(167,139,250,0.25) !important;
    border-color: rgba(167,139,250,0.6) !important;
    color: #fff !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<span class='dl-tag'>Step 06</span>", unsafe_allow_html=True)
st.title("🤖 Data Analyst Assistant")
st.caption("Ask anything — I respond in real time, grounded in your data.")

# safe df load
df = st.session_state.get("df_clean")
if df is None:
    df = st.session_state.get("df")
if df is None:
    st.warning("No dataset loaded. Go to **Upload Data** first.")
    st.stop()

ai_on = st.session_state.get("ai_enabled", False)
has_key = bool(os.environ.get("GROQ_API_KEY"))
use_ai = ai_on and has_key

# mode badge
if use_ai:
    st.markdown("<div class='dl-pill'><span class='dot'></span> AI mode · Groq llama-3.3-70b · Streaming</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='dl-pill' style='background:rgba(167,139,250,0.10);border-color:rgba(167,139,250,0.35);color:#c4b5fd'><span class='dot' style='background:#c4b5fd;box-shadow:0 0 10px #c4b5fd'></span> Offline mode · rule-based</div>", unsafe_allow_html=True)
    if ai_on and not has_key:
        st.warning("Add GROQ_API_KEY to `.env` and restart Streamlit to enable AI mode.")

# inline AI toggle
with st.expander("Ask AI Live", expanded=False):
    col1, col2 = st.columns([1, 2])
    with col1:
        st.session_state.ai_enabled = st.toggle(
            "Enable AI Mode",
            value=st.session_state.get("ai_enabled", False),
            help="Uses Groq API for smarter responses",
        )
    with col2:
        if st.session_state.ai_enabled and not has_key:
            custom = st.text_input(
                "Groq API Key", value="", type="password",
                placeholder="gsk_...",
                help="Get free key at console.groq.com",
                key="inline-key"
            )
            if custom:
                os.environ["GROQ_API_KEY"] = custom
                st.toast("✅ Key applied!", icon="✅")
                st.rerun()
        elif st.session_state.ai_enabled and has_key:
            st.success("✅ Groq API connected · llama-3.3-70b")

st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)

# init session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- render chat history ----
for entry in st.session_state.chat_history:
    role = entry["role"]
    msg  = entry["msg"]
    if role == "user":
        st.markdown(f"""
        <div class='msg-row user'>
          <div style='display:flex;flex-direction:column;align-items:flex-end'>
            <div class='name-lbl'>You</div>
            <div class='bubble user'>{msg}</div>
          </div>
          <div class='avatar user'>👤</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='msg-row'>
          <div class='avatar bot'>🤖</div>
          <div>
            <div class='name-lbl'>DataLens AI</div>
            <div class='bubble bot'>{msg}</div>
          </div>
        </div>""", unsafe_allow_html=True)

# ---- follow-up suggestions ----
last_bot = next((e["msg"] for e in reversed(st.session_state.chat_history) if e["role"] == "bot"), None)
followups = suggest_followups(last_bot) if last_bot else [
    "What are the key insights?", "Show me strong correlations", "Which category performs best?"
]

if not st.session_state.chat_history:
    st.markdown("##### 👋 Try asking")

fu_cols = st.columns(len(followups))
prompt_clicked = None
for i, (col, fp) in enumerate(zip(fu_cols, followups)):
    with col:
        st.markdown(f"""
        <style>
        div[data-testid="stButton"][key="fu-{i}"] button {{
            background: rgba(167,139,250,0.12) !important;
            border: 1px solid rgba(167,139,250,0.45) !important;
            color: #c4b5fd !important;
            border-radius: 20px !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        if st.button(fp, key=f"fu-{i}", use_container_width=True, type="secondary"):
            prompt_clicked = fp

st.markdown("<div class='dl-div'></div>", unsafe_allow_html=True)

# ---- chat input ----
question = st.chat_input("Ask me anything about your data… (try 'hi' 👋)")
if prompt_clicked and not question:
    question = prompt_clicked

# ---- process question ----
if question:
    # show user bubble immediately
    st.markdown(f"""
    <div class='msg-row user'>
      <div style='display:flex;flex-direction:column;align-items:flex-end'>
        <div class='name-lbl'>You</div>
        <div class='bubble user'>{question}</div>
      </div>
      <div class='avatar user'>👤</div>
    </div>""", unsafe_allow_html=True)

    # typing indicator
    typing_placeholder = st.empty()
    typing_placeholder.markdown("""
    <div class='msg-row'>
      <div class='avatar bot'>🤖</div>
      <div>
        <div class='name-lbl'>DataLens AI</div>
        <div class='bubble bot'>
          <span class='typing-dot'></span>
          <span class='typing-dot'></span>
          <span class='typing-dot'></span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    if use_ai:
        time.sleep(0.3)
        typing_placeholder.empty()
        answer_placeholder = st.empty()
        full_answer = ""
        for chunk in stream_ai_answer(question, df, st.session_state.chat_history):
            full_answer += chunk
            answer_placeholder.markdown(f"""
            <div class='msg-row'>
              <div class='avatar bot'>🤖</div>
              <div>
                <div class='name-lbl'>DataLens AI</div>
                <div class='bubble bot'>{full_answer}▌</div>
              </div>
            </div>""", unsafe_allow_html=True)
        answer_placeholder.markdown(f"""
        <div class='msg-row'>
          <div class='avatar bot'>🤖</div>
          <div>
            <div class='name-lbl'>DataLens AI</div>
            <div class='bubble bot'>{full_answer}</div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        time.sleep(0.4)
        typing_placeholder.empty()
        full_answer = rule_based_answer(question, df)
        st.markdown(f"""
        <div class='msg-row'>
          <div class='avatar bot'>🤖</div>
          <div>
            <div class='name-lbl'>DataLens AI</div>
            <div class='bubble bot'>{full_answer}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.session_state.chat_history.append({"role": "user", "msg": question})
    st.session_state.chat_history.append({"role": "bot", "msg": full_answer})
    if len(st.session_state.chat_history) > 50:
        st.session_state.chat_history = st.session_state.chat_history[-50:]
    st.rerun()

# ---- bottom buttons ----
st.markdown("")
col1, col2 = st.columns([1, 5])
with col1:
    if st.session_state.chat_history:
        if st.button("🗑️ Clear conversation", key="clear-chat"):
            st.session_state.chat_history = []
            st.rerun()
with col2:
    if st.button("📑 Generate Report →", type="primary", key="goto-report"):
        st.switch_page("pages/7_Report_Generator.py")