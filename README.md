# 🎓 Student Support Chatbot

An AI-powered academic assistant built with **Python**, **Streamlit**, and **Google Gemini** or **OpenAI**.  
Ask Shri anything — Maths, Science, History, Programming, Essays, and more.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-1.5-orange?logo=google&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Feature | Details |
|---|---|
| 🤖 AI models | Google Gemini 3.5 (Flash / Lite / 3.8) or OpenAI (GPT-4o Mini / GPT-4o) — switchable in sidebar |
| 💬 Multi-turn chat | Strict alternating conversation history sent on every request |
| 🗂 Named sessions | New Chat, browse and restore past sessions with auto-naming |
| 💡 Suggestions | 12 academic starter questions as clickable chips |
| 🔑 Secure key | Password-masked input, .env, or Streamlit secrets — never hardcoded |
| ⚡ Loading indicator | Spinner while the AI generates the response |
| 🛡 Error handling | Friendly messages for bad keys, quota limits, network errors, safety blocks |
| 📱 Mobile-friendly | Wide layout with responsive sidebar |

---

## 🗂 Project Structure

```
student-support-chatbot/
├── app.py                   ← entire application (single file)
├── requirements.txt         ← pinned dependencies
├── .gitignore               ← excludes secrets, venv, OS files
├── README.md                ← this file
└── .streamlit/
    └── secrets.toml         ← local API key (git-ignored, never committed)
```

---

## 🚀 Local Setup (Windows)

### Prerequisites
- Python 3.11 or newer — [python.org](https://www.python.org/downloads/)
- A free Gemini API key — [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### Step 1 — Clone or download

```powershell
git clone https://github.com/YOUR_USERNAME/student-support-chatbot.git
cd "student-support-chatbot"
```

### Step 2 — Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If you see a script execution error, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Step 3 — Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4 — Add your API key

Open `.streamlit/secrets.toml` and replace the placeholder:

```toml
GEMINI_API_KEY = "AIzaSy_your_actual_key_here"
```

**Or skip this step** — you can paste the key in the sidebar when the app starts.

### Step 5 — Run the app

```powershell
streamlit run app.py
```

The browser opens automatically at `http://localhost:8501`.

---

## 🔑 Obtaining a Gemini API Key

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with a Google account
3. Click **Create API Key** → select a Google Cloud project (or create one)
4. Copy the key (starts with `AIza…`)
5. Paste it into `.streamlit/secrets.toml` **or** directly in the sidebar

> The free tier includes generous usage. No credit card required.

---

## ✅ Testing the Chatbot

1. Start the app (`streamlit run app.py`)
2. Connect your API key in the sidebar
3. Type a question in the chat input, e.g. _"Explain the Pythagorean theorem"_
4. Verify a real AI response appears (not a placeholder)
5. Send a follow-up like _"Give me an example"_ — it should remember context
6. Click **＋ New Chat** → start a second conversation → switch back to the first in the sidebar
7. Click **🗑 Clear** → confirm the chat empties
8. Test a suggestion chip — it should auto-send the question
9. Enter a wrong API key → confirm a helpful error message appears (not a stack trace)

---

## ☁️ Deploying to Streamlit Community Cloud

> ⚠️ Deploy only **after** pushing to GitHub **without** the secrets file.

### 1 — Push to GitHub

```powershell
git init
git add app.py requirements.txt .gitignore README.md
# Do NOT add .streamlit/secrets.toml
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/student-support-chatbot.git
git push -u origin main
```

### 2 — Create the app on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in
2. Click **New app**
3. Select your repository and set **Main file path** to `app.py`
4. Click **Advanced settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "AIzaSy_your_actual_key_here"
   ```
5. Click **Deploy**

The live URL is available within ~60 seconds.

---

## ⚙️ Configuration Reference

| Setting | Location | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | `.streamlit/secrets.toml` (local) or Streamlit Cloud Secrets | Authenticates with Google AI |
| Model choice | Sidebar → Model selector | Switch between Flash and Pro |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit 1.35 + custom CSS |
| AI backends | Google Gemini 3.5 (Flash / Lite) & OpenAI GPT-4o (Mini / Full) |
| SDKs | `google-generativeai` 0.8.x & `openai` 1.35.x |
| Language | Python 3.9+ |
| Deployment | Streamlit Community Cloud |

---

## ⚠️ Known Limitations

- **No persistent storage** — sessions live only in the browser tab's memory; refreshing the page resets them. Add SQLite if you need cross-session persistence.
- **Rate limits** — the free Gemini tier has per-minute limits; heavy use may trigger quota errors.
- **Gemini 1.5 Pro** may not be available on all free-tier API keys; fall back to Flash if you get a 403.

---

## 📝 License

MIT — free to use, modify, and distribute.
