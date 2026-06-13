# 💬 Personal Utility Toolkit — MCP Web Client

A web-based chat client built with **FastAPI** that connects to the [Personal Utility Toolkit MCP Server](https://github.com/SANDEEP-KR-MAHTO/personal-toolkit-mcp-server) and uses **Groq (Llama 3.3 70B)** as the LLM — completely free!

🌐 **Live Demo:** [personal-toolkit-mcp-client-production.up.railway.app](https://personal-toolkit-mcp-client-production.up.railway.app)

---

## ✨ Features

- 🤖 Powered by **Groq** (free, fast Llama 3.3 70B)
- 🔧 Connected to **Remote MCP Server** on Railway
- 💬 Multi-turn conversation with memory
- ⚡ Clickable suggestion chips to get started fast
- 🎨 Clean dark UI with animated thinking indicator
- 🗑️ Clear conversation button

---

## 🛠️ Tools Available

Via the MCP Server, the client can:

| Category | Tools |
|----------|-------|
| 📝 Text | Word count, reverse, uppercase, lowercase, vowels, character frequency, extract emails, password generator |
| 🔢 Math | Calculator, unit converter, prime checker |
| ✅ Todo | Add, list, complete, delete, clear todos |

---

## 🚀 Quick Start (Run Locally)

### 1. Clone the repo
```bash
git clone https://github.com/SANDEEP-KR-MAHTO/personal-toolkit-mcp-client.git
cd personal-toolkit-mcp-client
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

### 3. Set up `.env`
Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_groq_api_key_here
MCP_SERVER_URL=https://web-production-2f9c2.up.railway.app/mcp
```

> Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 4. Run
```bash
python client.py
```

### 5. Open in browser
```
http://localhost:7860
```

---

## ☁️ Deploy on Railway

### 1. Fork this repo on GitHub

### 2. Go to [railway.app](https://railway.app)
- **New Project** → **GitHub Repository** → Select your fork → **Deploy**

### 3. Add environment variables
Go to your service → **Variables** tab → add:
```
GROQ_API_KEY     = your_groq_api_key_here
MCP_SERVER_URL   = https://web-production-2f9c2.up.railway.app/mcp
```

### 4. Generate domain
- Go to **Settings → Networking → Generate Domain**
- Your app will be live at `https://your-app.up.railway.app`

---

## 🏗️ Project Structure

```
├── client.py            ← FastAPI backend + Groq + MCP logic
├── templates/
│   └── index.html       ← Chat UI
├── railway.json         ← Railway deployment config
├── .env                 ← API keys (never push to GitHub)
├── .gitignore
└── requirements.txt
```

---

## 🔄 How It Works

```
User types message
       ↓
FastAPI backend receives it
       ↓
Groq LLM decides which tool to use
       ↓
Client calls tool on Remote MCP Server (Railway)
       ↓
MCP Server executes tool & returns result
       ↓
Groq generates final response
       ↓
Response shown in chat UI
```

---

## 🛠️ Built With

- [FastAPI](https://fastapi.tiangolo.com) — Web framework
- [Groq](https://console.groq.com) — Free LLM API (Llama 3.3 70B)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — MCP client
- [Railway](https://railway.app) — Deployment platform
- [Personal Toolkit MCP Server](https://github.com/SANDEEP-KR-MAHTO/personal-toolkit-mcp-server) — Tools backend
