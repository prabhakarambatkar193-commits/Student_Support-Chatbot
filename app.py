"""
Student Support Chatbot — app.py
Powered by Google Gemini AI or OpenAI  |  Built with Streamlit
"""

from __future__ import annotations

import os
import re
import uuid
from datetime import datetime
from typing import Optional

import streamlit as st

# ---------------------------------------------------------------------------
# PAGE CONFIG  (must be the very first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Support Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://aistudio.google.com/app/apikey",
        "Report a bug": None,
        "About": "Student Support Chatbot powered by Google Gemini AI or OpenAI.",
    },
)

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are Shri, a friendly and knowledgeable Student Support Assistant.
Your purpose is to help students succeed academically.

You help with:
- Clear explanations of academic concepts (all subjects and grade levels)
- Step-by-step problem solving in Math, Science, Programming, etc.
- Essay structure, grammar, and writing advice
- Study strategies, time management, and exam preparation tips
- Historical events, literature analysis, geography, economics
- Motivating and encouraging students who feel stuck

Response guidelines:
- Be encouraging, patient, and supportive at all times
- Use plain language; introduce technical terms with explanations
- Use numbered steps for procedures, bullet points for lists
- Keep answers focused — thorough but not overwhelming
- When a concept has multiple parts, address each part clearly
- End with a brief motivational note when a student seems frustrated
- If a question is ambiguous, ask one clarifying question
"""

# ── Gemini models (current stable versions)
GEMINI_MODELS = {
    "Gemini 3.5 Flash (Fast ⚡)": "gemini-3.5-flash",
    "Gemini 3.5 Flash Lite (Ultra Fast ⚡)": "gemini-3.5-flash-lite",
    "Gemini 3.8 Flash (Powerful 🧠)": "gemini-3.8-flash",
}
DEFAULT_GEMINI_LABEL = "Gemini 3.5 Flash (Fast ⚡)"

# ── OpenAI models (current stable)
OPENAI_MODELS = {
    "GPT-4o Mini (Fast ⚡)": "gpt-4o-mini",
    "GPT-4o (Powerful 🧠)": "gpt-4o",
}
DEFAULT_OPENAI_LABEL = "GPT-4o Mini (Fast ⚡)"

# ── AI provider options shown in the sidebar
AI_PROVIDERS = ["Google Gemini", "OpenAI"]

SUGGESTED_QUESTIONS = [
    "📚 Explain photosynthesis simply",
    "🧮 Solve quadratic equations step-by-step",
    "📝 How do I write a good essay?",
    "🧠 Best study techniques for exams",
    "💡 What is Newton's second law?",
    "🌍 What caused World War I?",
    "🐍 Explain Python loops with examples",
    "📐 What is the Pythagorean theorem?",
    "⚗️ Difference between acids and bases",
    "📖 How to analyse a poem",
    "💰 How does the stock market work?",
    "🔢 Explain fractions and percentages",
]

MAX_HISTORY_SESSIONS = 20
MAX_MESSAGES_PER_SESSION = 100


# ---------------------------------------------------------------------------
# CSS  (design unchanged from previous version)
# ---------------------------------------------------------------------------
def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        .app-header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border-radius: 14px; padding: 1.6rem 2rem; margin-bottom: 1.2rem;
            color: white; text-align: center;
            box-shadow: 0 6px 24px rgba(79, 70, 229, 0.32);
        }
        .app-header h1 { font-size: 2rem; font-weight: 700; margin: 0; letter-spacing: -0.4px; }
        .app-header p  { font-size: 0.97rem; margin: 0.4rem 0 0; opacity: 0.88; }

        .welcome-card {
            background: linear-gradient(135deg, #eef2ff 0%, #faf5ff 100%);
            border: 1px solid #c7d2fe; border-radius: 12px;
            padding: 1.2rem 1.5rem; margin-bottom: 1.2rem;
        }
        .welcome-card h3 { color: #4338ca; margin: 0 0 0.35rem; font-size: 1.05rem; }
        .welcome-card p  { color: #374151; margin: 0; font-size: 0.9rem; line-height: 1.65; }

        [data-testid="stChatMessage"] { border-radius: 10px; padding: 0.1rem 0; }

        .chip-label { color: #4338ca; font-weight: 600; font-size: 0.88rem; margin: 0.8rem 0 0.4rem; }

        .session-item {
            background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
            padding: 0.5rem 0.75rem; margin-bottom: 0.35rem; cursor: pointer;
            font-size: 0.82rem; color: #374151; transition: background 0.15s;
        }
        .session-item:hover  { background: #eef2ff; border-color: #a5b4fc; }
        .session-item.active { background: #eef2ff; border-color: #6366f1; color: #4338ca; font-weight: 600; }

        .stat-row { display: flex; gap: 0.6rem; margin-bottom: 0.4rem; }
        .stat-card {
            flex: 1; background: white; border: 1px solid #e2e8f0;
            border-radius: 10px; padding: 0.7rem; text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        }
        .stat-n { font-size: 1.45rem; font-weight: 700; color: #4f46e5; }
        .stat-l { font-size: 0.72rem; color: #6b7280; margin-top: 0.1rem; }

        .info-box {
            background: #f8fafc; border: 1px solid #e2e8f0;
            border-radius: 10px; padding: 0.9rem 1rem; margin-bottom: 0.8rem;
        }
        .info-box h4 { color: #4338ca; margin: 0 0 0.4rem; font-size: 0.9rem; }
        .info-box p, .info-box li { color: #374151; font-size: 0.82rem; line-height: 1.65; margin: 0; }
        .info-box ul { padding-left: 1.1rem; margin: 0; }

        .dot-green { display:inline-block; width:8px; height:8px; border-radius:50%; background:#22c55e; margin-right:5px; }
        .dot-red   { display:inline-block; width:8px; height:8px; border-radius:50%; background:#ef4444; margin-right:5px; }
        .dot-blue  { display:inline-block; width:8px; height:8px; border-radius:50%; background:#3b82f6; margin-right:5px; }

        /* provider badge */
        .badge {
            display:inline-block; padding:0.15rem 0.55rem; border-radius:999px;
            font-size:0.72rem; font-weight:600; margin-left:6px;
        }
        .badge-gemini { background:#eef2ff; color:#4338ca; }
        .badge-openai { background:#f0fdf4; color:#166534; }

        .app-footer {
            text-align: center; color: #9ca3af; font-size: 0.78rem;
            margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #f3f4f6;
        }

        #MainMenu, footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# SESSION-STATE HELPERS
# ---------------------------------------------------------------------------
def _init_state() -> None:
    defaults: dict = {
        # connection
        "provider": "Google Gemini",       # "Google Gemini" | "OpenAI"
        "api_key_valid": False,
        "gemini_client": None,             # google.generativeai.GenerativeModel
        "openai_client": None,             # openai.OpenAI
        "gemini_model_label": DEFAULT_GEMINI_LABEL,
        "openai_model_label": DEFAULT_OPENAI_LABEL,
        "_auto_connect_attempted": False,
        "manual_disconnect": False,
        # chat
        "current_session_id": None,
        "current_messages": [],
        "current_session_name": "New Chat",
        "sessions": [],
        "total_questions": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    if st.session_state.get("gemini_model_label") not in GEMINI_MODELS:
        st.session_state.gemini_model_label = DEFAULT_GEMINI_LABEL
    if st.session_state.get("openai_model_label") not in OPENAI_MODELS:
        st.session_state.openai_model_label = DEFAULT_OPENAI_LABEL

    if st.session_state.current_session_id is None:
        _new_session()


def _new_session() -> None:
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.current_messages = []
    st.session_state.current_session_name = f"Chat {len(st.session_state.sessions) + 1}"


def _save_current_session() -> None:
    sid  = st.session_state.current_session_id
    msgs = st.session_state.current_messages
    if not msgs:
        return

    name = st.session_state.current_session_name
    if (name.startswith("Chat ") or name == "New Chat") and msgs:
        first_user = next((m["content"] for m in msgs if m["role"] == "user"), "")
        if first_user:
            clean = re.sub(r"^[\U00010000-\U0010ffff\u2600-\u26FF\u2700-\u27BF]+\s*", "", first_user)
            name = (clean[:37] + "…") if len(clean) > 40 else clean
            st.session_state.current_session_name = name

    existing = next((s for s in st.session_state.sessions if s["id"] == sid), None)
    if existing:
        existing["name"] = name
        existing["messages"] = list(msgs)
    else:
        st.session_state.sessions.insert(
            0,
            {
                "id": sid,
                "name": name,
                "messages": list(msgs),
                "created_at": datetime.now().strftime("%b %d, %H:%M"),
            },
        )
        st.session_state.sessions = st.session_state.sessions[:MAX_HISTORY_SESSIONS]


def _load_session(session_id: str) -> None:
    sess = next((s for s in st.session_state.sessions if s["id"] == session_id), None)
    if sess:
        st.session_state.current_session_id = sess["id"]
        st.session_state.current_messages   = list(sess["messages"])
        st.session_state.current_session_name = sess["name"]


# ---------------------------------------------------------------------------
# SECRET KEY HELPERS
# ---------------------------------------------------------------------------
def _is_placeholder(key: str) -> bool:
    k = key.strip().strip("\"'")
    return not k or k.upper().startswith("YOUR_") or "your_" in k.lower() or len(k) < 20


def _get_secret(secret_name: str) -> str:
    key = ""
    try:
        key = st.secrets.get(secret_name, "") or st.secrets.get(secret_name.lower(), "")
    except Exception:
        pass

    if not key:
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=".env", override=False)
        except ImportError:
            pass
        key = os.environ.get(secret_name, "")

    return "" if _is_placeholder(str(key)) else str(key).strip().strip("\"'")


# ---------------------------------------------------------------------------
# ERROR CLASSIFICATION
# ---------------------------------------------------------------------------
def _classify_gemini_error(exc: Exception) -> str:
    try:
        from google.api_core import exceptions as gapi
        from google.generativeai.types import generation_types

        if isinstance(exc, gapi.InvalidArgument):
            msg = str(exc)
            if "API_KEY_INVALID" in msg or "api key" in msg.lower():
                return (
                    "❌ **Invalid API Key** — Google rejected the key (HTTP 400). "
                    "Get a valid key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)."
                )
            return f"⚠️ **Invalid Request (HTTP 400)** — {msg}"
        if isinstance(exc, gapi.Unauthenticated):
            return "❌ **Authentication Failed** — The Gemini API key is missing or malformed (HTTP 401)."
        if isinstance(exc, gapi.PermissionDenied):
            return (
                "🔒 **Permission Denied** — This key cannot access the selected Gemini model (HTTP 403). "
                "Try switching to **Gemini 1.5 Flash**."
            )
        if isinstance(exc, gapi.ResourceExhausted):
            return "⚠️ **Quota Exceeded** — Gemini rate limit hit (HTTP 429). Wait a minute and retry."
        if isinstance(exc, gapi.NotFound):
            return (
                "🔍 **Model Not Found** — The selected Gemini model is unavailable on your account (HTTP 404). "
                "Try switching to **Gemini 3.5 Flash**."
            )
        if isinstance(exc, (gapi.ServiceUnavailable, gapi.DeadlineExceeded)):
            return "🌐 **Service Unavailable** — Google's servers are temporarily unreachable. Try again shortly."
        if isinstance(exc, generation_types.BlockedPromptException):
            return "🛡️ **Prompt Blocked** — Blocked by Google's safety filters. Please rephrase."
        if isinstance(exc, generation_types.StopCandidateException):
            return "🛡️ **Response Stopped** — Interrupted by a safety filter. Please rephrase."
    except ImportError:
        pass

    msg = str(exc).lower()
    if "finish_reason" in msg or "safety_ratings" in msg or "recitation" in msg:
        return "🛡️ **Content Filtered** — Response blocked by safety filters. Please rephrase."
    if "api_key" in msg or "api key" in msg:
        return "❌ **Invalid API Key** — Google rejected the key. Check aistudio.google.com."
    if "quota" in msg or "429" in msg or "resource_exhausted" in msg:
        return "⚠️ **Quota Exceeded** — Gemini rate limit hit. Wait a minute and retry."
    if "permission" in msg or "403" in msg:
        return "🔒 **Permission Denied** — This key cannot access the selected model. Switch to Flash."
    if any(w in msg for w in ("connect", "timeout", "network", "ssl", "connection", "unreachable")):
        return "🌐 **Network Error** — Could not reach Google's servers. Check your internet connection."
    return f"⚠️ **Gemini Error ({type(exc).__name__})** — {str(exc)}"


def _classify_openai_error(exc: Exception) -> str:
    try:
        import openai as oai
        if isinstance(exc, oai.AuthenticationError):
            return (
                "❌ **Invalid API Key** — OpenAI rejected the key (HTTP 401). "
                "Check it at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)."
            )
        if isinstance(exc, oai.PermissionDeniedError):
            return (
                "🔒 **Permission Denied** — This key cannot access the selected OpenAI model (HTTP 403). "
                "Try switching to **GPT-4o Mini**."
            )
        if isinstance(exc, oai.RateLimitError):
            return "⚠️ **Rate Limit / Quota Exceeded** — OpenAI rate limit hit (HTTP 429). Wait and retry."
        if isinstance(exc, oai.NotFoundError):
            return (
                "🔍 **Model Not Found** — The selected OpenAI model is unavailable on your account (HTTP 404). "
                "Switch to **GPT-4o Mini**."
            )
        if isinstance(exc, oai.APIConnectionError):
            return "🌐 **Connection Error** — Could not reach OpenAI's servers. Check your internet connection."
        if isinstance(exc, oai.APITimeoutError):
            return "⏱️ **Request Timed Out** — OpenAI took too long to respond. Please try again."
        if isinstance(exc, oai.APIStatusError):
            return f"⚠️ **OpenAI API Error (HTTP {exc.status_code})** — {exc.message[:120]}"
    except ImportError:
        pass

    msg = str(exc).lower()
    if "401" in msg or "invalid" in msg or "incorrect api key" in msg:
        return "❌ **Invalid API Key** — OpenAI rejected the key. Check platform.openai.com."
    if "429" in msg or "rate limit" in msg or "quota" in msg:
        return "⚠️ **Rate Limit / Quota Exceeded** — OpenAI rate limit hit. Wait and retry."
    if "403" in msg or "permission" in msg:
        return "🔒 **Permission Denied** — This key cannot access the selected model. Switch to Mini."
    if any(w in msg for w in ("connect", "timeout", "network", "ssl", "connection")):
        return "🌐 **Network Error** — Could not reach OpenAI's servers. Check your internet connection."
    return f"⚠️ **OpenAI Error ({type(exc).__name__})** — {str(exc)}"


# ---------------------------------------------------------------------------
# GEMINI INTEGRATION
# ---------------------------------------------------------------------------
def _connect_gemini(api_key: str, model_label: str) -> tuple[bool, str]:
    import google.generativeai as genai

    api_key = api_key.strip().strip("\"'")
    if not api_key:
        return False, "❌ **No API Key** — Please enter your Gemini API key."
    if len(api_key) < 20:
        return False, "❌ **Key Too Short** — This doesn't look like a valid Gemini API key."

    try:
        genai.configure(api_key=api_key)

        # Attempt requested model first, then auto-fallback across Gemini models if needed
        candidate_labels = [model_label] + [l for l in GEMINI_MODELS if l != model_label]
        last_exc = None
        connected_model = None
        connected_label = model_label

        for lbl in candidate_labels:
            try:
                m_name = GEMINI_MODELS[lbl]
                candidate_model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=SYSTEM_PROMPT,
                )
                test_response = candidate_model.generate_content("Hi", request_options={"timeout": 15})
                try:
                    _ = test_response.text
                except Exception:
                    pass
                connected_model = candidate_model
                connected_label = lbl
                break
            except Exception as e:
                last_exc = e
                continue

        if not connected_model:
            raise last_exc or RuntimeError("Unable to connect to any Gemini model.")

        st.session_state.gemini_client      = connected_model
        st.session_state.api_key_valid      = True
        st.session_state.provider           = "Google Gemini"
        st.session_state.gemini_model_label = connected_label
        return True, "Connected"

    except Exception as exc:
        st.session_state.api_key_valid = False
        st.session_state.gemini_client = None
        return False, _classify_gemini_error(exc)


def _rebuild_gemini_model(model_label: str) -> None:
    import google.generativeai as genai
    if not (st.session_state.api_key_valid and st.session_state.provider == "Google Gemini"):
        return
    if st.session_state.gemini_model_label == model_label:
        return
    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_MODELS[model_label],
            system_instruction=SYSTEM_PROMPT,
        )
        st.session_state.gemini_client      = model
        st.session_state.gemini_model_label = model_label
    except Exception as exc:
        st.error(_classify_gemini_error(exc))


def _get_gemini_history() -> list[dict]:
    """
    Build a strictly alternating (user -> model -> user -> model) history
    from prior messages, excluding the pending prompt and any error responses.
    Gemini's start_chat requires history to end in a 'model' turn (or be empty)
    so that send_message can append the 'user' turn cleanly.
    """
    history: list[dict] = []
    # Take prior messages excluding the current pending prompt
    prior_messages = st.session_state.current_messages[:-1]
    expected_role = "user"

    for m in prior_messages:
        # Exclude turns marked as errors
        if m.get("is_error"):
            continue
        turn_role = "user" if m["role"] == "user" else "model"
        if turn_role == expected_role:
            history.append({"role": turn_role, "parts": [m["content"]]})
            expected_role = "model" if turn_role == "user" else "user"

    # History must end on a 'model' turn (or be empty)
    if history and history[-1]["role"] != "model":
        history.pop()

    return history


def _chat_gemini(prompt: str) -> str:
    model = st.session_state.gemini_client
    if not model:
        raise RuntimeError("Gemini model client is not initialized. Please connect in the sidebar.")
    history = _get_gemini_history()
    chat_session = model.start_chat(history=history)
    return chat_session.send_message(prompt).text


# ---------------------------------------------------------------------------
# OPENAI INTEGRATION
# ---------------------------------------------------------------------------
def _connect_openai(api_key: str, model_label: str) -> tuple[bool, str]:
    try:
        import openai as oai
    except ImportError:
        return False, (
            "📦 **OpenAI package not installed** — run `pip install openai==1.35.0` "
            "then restart the app."
        )

    api_key = api_key.strip().strip("\"'")
    if not api_key:
        return False, "❌ **No API Key** — Please enter your OpenAI API key."
    if not api_key.startswith("sk-"):
        return False, "❌ **Invalid Key Format** — OpenAI keys start with `sk-`."

    try:
        client = oai.OpenAI(api_key=api_key)
        model_name = OPENAI_MODELS[model_label]
        client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
        )
        st.session_state.openai_client      = client
        st.session_state.api_key_valid      = True
        st.session_state.provider           = "OpenAI"
        st.session_state.openai_model_label = model_label
        return True, "Connected"

    except Exception as exc:
        st.session_state.api_key_valid = False
        st.session_state.openai_client = None
        return False, _classify_openai_error(exc)


def _chat_openai(prompt: str) -> str:
    import openai as oai
    client     = st.session_state.openai_client
    if not client:
        raise RuntimeError("OpenAI client is not initialized. Please connect in the sidebar.")
    model_name = OPENAI_MODELS[st.session_state.openai_model_label]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Append prior messages excluding the current pending prompt and errors
    for m in st.session_state.current_messages[:-1]:
        if not m.get("is_error"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(model=model_name, messages=messages)
    return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# UNIFIED CHAT DISPATCHER
# ---------------------------------------------------------------------------
def _chat(prompt: str) -> str:
    if st.session_state.provider == "OpenAI":
        return _chat_openai(prompt)
    return _chat_gemini(prompt)


def _classify_error(exc: Exception) -> str:
    if st.session_state.provider == "OpenAI":
        return _classify_openai_error(exc)
    return _classify_gemini_error(exc)


# ---------------------------------------------------------------------------
# UI HELPERS
# ---------------------------------------------------------------------------
def _render_suggestion_chips(location: str) -> Optional[str]:
    st.markdown('<p class="chip-label">💡 Try asking…</p>', unsafe_allow_html=True)
    clicked: Optional[str] = None
    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 3]:
            if st.button(q, key=f"chip_{location}_{i}", use_container_width=True):
                clicked = q
    return clicked


def _send_message(prompt: str) -> None:
    prompt = prompt.strip()
    if not prompt:
        return
    if len(st.session_state.current_messages) >= MAX_MESSAGES_PER_SESSION:
        st.warning("This chat has reached its maximum length. Please start a new chat.")
        return

    st.session_state.current_messages.append({"role": "user", "content": prompt})
    st.session_state.total_questions += 1

    is_error = False
    with st.spinner("Shri is thinking…"):
        try:
            reply = _chat(prompt)
        except Exception as exc:
            reply = _classify_error(exc)
            is_error = True

    st.session_state.current_messages.append({
        "role": "assistant",
        "content": reply,
        "is_error": is_error,
    })
    _save_current_session()



# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
def _provider_badge(provider: str) -> str:
    if provider == "OpenAI":
        return '<span class="badge badge-openai">OpenAI</span>'
    return '<span class="badge badge-gemini">Gemini</span>'


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🎓 Shri")
        st.caption("Your AI Study Companion")
        st.divider()

        st.markdown("#### 🤖 AI Provider")
        chosen_provider = st.radio(
            "AI Provider",
            options=AI_PROVIDERS,
            index=AI_PROVIDERS.index(st.session_state.provider),
            horizontal=True,
            label_visibility="collapsed",
        )
        if chosen_provider != st.session_state.provider:
            st.session_state.provider       = chosen_provider
            st.session_state.api_key_valid  = False
            st.session_state.gemini_client  = None
            st.session_state.openai_client  = None
            st.session_state["_auto_connect_attempted"] = False
            st.session_state["manual_disconnect"]       = False
            st.rerun()

        st.divider()

        provider = st.session_state.provider
        st.markdown(f"#### 🔑 {provider} API Key")

        auto_key = "_auto_connect_attempted"
        if (
            not st.session_state.api_key_valid
            and not st.session_state.get(auto_key)
            and not st.session_state.get("manual_disconnect", False)
        ):
            st.session_state[auto_key] = True
            if provider == "Google Gemini":
                secret = _get_secret("GEMINI_API_KEY")
                if secret:
                    ok, _ = _connect_gemini(secret, st.session_state.gemini_model_label)
                    if ok:
                        st.success("✅ Gemini connected via secrets / .env")
            else:
                secret = _get_secret("OPENAI_API_KEY")
                if secret:
                    ok, _ = _connect_openai(secret, st.session_state.openai_model_label)
                    if ok:
                        st.success("✅ OpenAI connected via secrets / .env")

        if not st.session_state.api_key_valid:
            if provider == "Google Gemini":
                placeholder = "AIza…"
                help_url    = "https://aistudio.google.com/app/apikey"
                help_text   = "Free key → aistudio.google.com"
            else:
                placeholder = "sk-…"
                help_url    = "https://platform.openai.com/api-keys"
                help_text   = "Key → platform.openai.com/api-keys"

            key_input = st.text_input(
                f"{provider} API Key",
                type="password",
                placeholder=placeholder,
                help=help_text,
                label_visibility="collapsed",
            )
            st.caption(f"🔗 [Get your key]({help_url})")

            col_connect, col_test = st.columns(2)

            with col_connect:
                if st.button("Connect 🔗", use_container_width=True, type="primary"):
                    k = key_input.strip().strip("\"'")
                    if k:
                        st.session_state["manual_disconnect"] = False
                        with st.spinner("Connecting…"):
                            if provider == "Google Gemini":
                                ok, msg = _connect_gemini(k, st.session_state.gemini_model_label)
                            else:
                                ok, msg = _connect_openai(k, st.session_state.openai_model_label)
                        if ok:
                            st.success("✅ Connected!")
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please enter your API key.")

            with col_test:
                if st.button("Test 🧪", use_container_width=True):
                    k = key_input.strip().strip("\"'")
                    if k:
                        with st.spinner("Testing…"):
                            if provider == "Google Gemini":
                                ok, msg = _connect_gemini(k, st.session_state.gemini_model_label)
                                st.session_state.api_key_valid = False
                                st.session_state.gemini_client = None
                            else:
                                ok, msg = _connect_openai(k, st.session_state.openai_model_label)
                                st.session_state.api_key_valid = False
                                st.session_state.openai_client = None
                        if ok:
                            st.success("✅ Key is valid! Click **Connect** to start chatting.")
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please enter your API key.")

        else:
            badge = _provider_badge(provider)
            st.markdown(
                f'<span class="dot-green"></span> **Connected** {badge}',
                unsafe_allow_html=True,
            )
            if st.button("Disconnect 🔌", use_container_width=True):
                st.session_state.api_key_valid       = False
                st.session_state.gemini_client       = None
                st.session_state.openai_client       = None
                st.session_state[auto_key]           = True
                st.session_state["manual_disconnect"] = True
                st.rerun()

        st.divider()

        if st.session_state.api_key_valid:
            st.markdown("#### 🔧 Model")
            if provider == "Google Gemini":
                chosen = st.selectbox(
                    "Gemini model",
                    options=list(GEMINI_MODELS.keys()),
                    index=list(GEMINI_MODELS.keys()).index(st.session_state.gemini_model_label),
                    label_visibility="collapsed",
                )
                if chosen != st.session_state.gemini_model_label:
                    _rebuild_gemini_model(chosen)
                    st.rerun()
            else:
                chosen = st.selectbox(
                    "OpenAI model",
                    options=list(OPENAI_MODELS.keys()),
                    index=list(OPENAI_MODELS.keys()).index(st.session_state.openai_model_label),
                    label_visibility="collapsed",
                )
                if chosen != st.session_state.openai_model_label:
                    st.session_state.openai_model_label = chosen
                    st.rerun()
            st.divider()

        st.markdown("#### 💬 Chats")
        col_new, col_clear = st.columns(2)
        with col_new:
            if st.button("＋ New Chat", use_container_width=True):
                _save_current_session()
                _new_session()
                st.rerun()
        with col_clear:
            if st.button("🗑 Clear", use_container_width=True):
                st.session_state.sessions = [
                    s for s in st.session_state.sessions
                    if s["id"] != st.session_state.current_session_id
                ]
                _new_session()
                st.rerun()

        if st.session_state.sessions:
            st.markdown("**Recent chats**")
            for sess in st.session_state.sessions[:10]:
                is_active = sess["id"] == st.session_state.current_session_id
                label = ("▶ " if is_active else "") + sess["name"]
                if st.button(
                    label,
                    key=f"sess_{sess['id']}",
                    use_container_width=True,
                    help=f"Started {sess['created_at']}",
                ):
                    if not is_active:
                        _save_current_session()
                        _load_session(sess["id"])
                        st.rerun()

        st.divider()

        exchanges = len(st.session_state.current_messages) // 2
        st.markdown(
            f"""
            <div class="stat-row">
              <div class="stat-card">
                <div class="stat-n">{exchanges}</div>
                <div class="stat-l">Exchanges</div>
              </div>
              <div class="stat-card">
                <div class="stat-n">{st.session_state.total_questions}</div>
                <div class="stat-l">Questions</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        with st.expander("📖 Subjects covered"):
            st.markdown(
                "Mathematics · Physics · Chemistry · Biology · Computer Science · "
                "History · Geography · Literature · Economics · Languages · Art"
            )
        with st.expander("ℹ️ About Shri"):
            st.markdown(
                "Shri is your AI-powered study companion. She explains concepts, "
                "solves problems step-by-step, and helps you build better study habits — "
                "powered by Google Gemini or OpenAI."
            )


# ---------------------------------------------------------------------------
# MAIN CONTENT
# ---------------------------------------------------------------------------
def render_main() -> None:
    st.markdown(
        """
        <div class="app-header">
            <h1>🎓 Student Support Chatbot</h1>
            <p>Ask Shri anything — Maths, Science, History, Essays, Programming and more</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    messages  = st.session_state.current_messages
    api_ready = st.session_state.api_key_valid
    provider  = st.session_state.provider

    if not messages:
        st.markdown(
            """
            <div class="welcome-card">
                <h3>👋 Hi! I'm Shri, your AI Study Companion</h3>
                <p>
                  I can explain any academic concept, walk you through problems step-by-step,
                  help with essays, and share study tips.
                  Connect your API key in the sidebar, then pick a suggestion or type your question.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not api_ready:
            st.info(
                "🔑 **Choose an AI provider and connect your API key in the sidebar** to start chatting.\n\n"
                "- **Google Gemini** — free key at [Google AI Studio](https://aistudio.google.com/app/apikey)\n"
                "- **OpenAI** — key at [OpenAI API Keys](https://platform.openai.com/api-keys)"
            )

        chip_clicked = _render_suggestion_chips("main")
        if chip_clicked:
            if api_ready:
                _send_message(chip_clicked)
                st.rerun()
            else:
                st.warning("🔑 Connect your API key in the sidebar first.")

        st.divider()

    for msg in messages:
        role = msg["role"]
        with st.chat_message(role, avatar="🧑‍🎓" if role == "user" else "🎓"):
            st.markdown(msg["content"])

    if messages and api_ready:
        with st.expander("💡 Need inspiration? See suggested questions"):
            chip_clicked = _render_suggestion_chips("chat")
            if chip_clicked:
                _send_message(chip_clicked)
                st.rerun()

    st.markdown("")
    if api_ready:
        user_input = st.chat_input(
            f"Ask Shri a question… ({provider})",
            key="chat_input",
        )
        if user_input:
            _send_message(user_input)
            st.rerun()
    else:
        st.chat_input("Connect your API key to start chatting…", disabled=True)

    active_provider = f"Google Gemini AI" if provider == "Google Gemini" else "OpenAI"
    st.markdown(
        f"<div class='app-footer'>"
        f"🎓 Student Support Chatbot &nbsp;·&nbsp; Powered by {active_provider} "
        f"&nbsp;·&nbsp; Built with Streamlit"
        f"</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
def main() -> None:
    inject_css()
    _init_state()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()