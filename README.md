
# 📈 Stock Market Q&A Agent

A multi-agent AI system for Indian stock market analysis. Ask any question about a stock and get accurate, structured insights powered by real-time data from **screener.in** and **moneycontrol.com**.

---

## 🏗️ Architecture

```
User Query
    ↓
🧠 Supervisor Agent (llama-4-scout-17b)
    ├── Fetches quick company overview via Tavily
    ├── Classifies query as Simple or Complex
    └── Routes to correct agent(s)
         │
         ├── Simple Query (single metric)
         │       ↓
         │   📊 Data Aggregator     OR    📰 News Sentiment
         │   (llama-4-scout-17b)         (llama-3.3-70b)
         │   screener.in                  moneycontrol.com
         │       │                              │
         │       └──── If empty ────────────────┘
         │             ⚠️ Interrupt → Ask User
         │             Yes → NSE India / Economic Times
         │             No  → Continue with available data
         │
         └── Complex Query (full analysis)
                 ↓
         📊 Data Aggregator → 📰 News Sentiment
                 ↓
         🔍 Investment Analyst (qwen3-32b)
                 ↓
         Sufficient? YES → Final Answer → User
                     NO  → Retry (max 1x) → Supervisor
```

---

## 🤖 Agent Details

| Agent | Model | Provider | Data Source | Role |
|-------|-------|----------|-------------|------|
| 🧠 Supervisor | `meta-llama/llama-4-scout-17b-16e-instruct` | Groq | Tavily (overview) | Routes queries, classifies intent |
| 📊 Data Aggregator | `meta-llama/llama-4-scout-17b-16e-instruct` | Groq | screener.in → NSE India | Fetches PE ratio, financials, ratios, shareholding |
| 📰 News Sentiment | `llama-3.3-70b-versatile` | Groq | moneycontrol.com → Economic Times | Fetches news, sentiment, announcements |
| 🔍 Investment Analyst | `qwen/qwen3-32b` | Groq | — | Analyzes data, generates concise insights |

---

## 🔄 Smart Routing Logic

| Question Type | Agents Triggered |
|---|---|
| PE ratio, financials, balance sheet | Supervisor → Data Aggregator → Analyst |
| News, policy, announcements | Supervisor → News Sentiment → Analyst |
| Complete analysis | Supervisor → Data Aggregator → News Sentiment → Analyst |
| Data not found on primary source | ⚠️ Interrupt → User confirms fallback → Resume |

---

## 🔁 Fallback Flow (Human-in-the-Loop)

```
screener.in returns empty
    ↓
⚠️ "No results on Screener.in. Search NSE India instead?"
    ├── Yes → searches nseindia.com → continues
    └── No  → proceeds with available data

moneycontrol.com returns empty
    ↓
⚠️ "No results on Moneycontrol. Search Economic Times instead?"
    ├── Yes → searches economictimes.indiatimes.com → continues
    └── No  → proceeds with available data
```

---

## 📁 Project Structure

```
stock-qa-agent/
│
├── app.py                          # Streamlit frontend with interrupt handling
├── requirements.txt
├── README.md
│
├── config/
│   ├── __init__.py
│   └── settings.py                 # API keys, model names, constants
│
├── graph/
│   ├── __init__.py
│   ├── state.py                    # AgentState with all fields
│   ├── graph_builder.py            # LangGraph graph + MemorySaver checkpointer
│   └── nodes/
│       ├── __init__.py
│       ├── supervisor.py           # Routing + company overview
│       ├── data_aggregator.py      # screener.in + NSE fallback + interrupt
│       ├── news_sentiment.py       # moneycontrol.com + ET fallback + interrupt
│       └── investment_analyst.py   # Analysis + simple/complex handling
│
├── tools/
│   ├── __init__.py
│   ├── screener_tool.py            # Tavily → screener.in + nseindia.com
│   └── moneycontrol_tool.py        # Tavily → moneycontrol.com + ET
│
└── .streamlit/
    └── secrets.toml                # API keys (never commit to GitHub)
```

---

## 🚀 Setup Guide

### Option 1 — Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/stock-qa-agent.git
cd stock-qa-agent
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add API keys to `.streamlit/secrets.toml`**
```toml
GROQ_API_KEY   = "gsk_your_key_here"
TAVILY_API_KEY = "tvly_your_key_here"
```

**4. Run**
```bash
streamlit run app.py
```

---

### Option 2 — Google Colab

**Cell 1 — Install**
```python
!pip install langgraph langchain-core langchain-groq langchain-community tavily-python streamlit pydantic pyngrok -q
```

**Cell 2 — Clone**
```python
!git clone https://github.com/yourusername/stock-qa-agent.git /content/stock-qa-agent
%cd /content/stock-qa-agent
```

**Cell 3 — Set API Keys**
```python
import os
os.environ["GROQ_API_KEY"]   = "gsk_your_key_here"
os.environ["TAVILY_API_KEY"] = "tvly_your_key_here"
```

**Cell 4 — Patch settings.py**
```python
settings = """
import os
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
SUPERVISOR_MODEL  = "meta-llama/llama-4-scout-17b-16e-instruct"
DATA_MODEL        = "meta-llama/llama-4-scout-17b-16e-instruct"
NEWS_MODEL        = "llama-3.3-70b-versatile"
ANALYST_MODEL     = "qwen/qwen3-32b"
SCREENER_DOMAIN     = "screener.in"
NSE_DOMAIN          = "nseindia.com"
MONEYCONTROL_DOMAIN = "moneycontrol.com"
ET_DOMAIN           = "economictimes.indiatimes.com"
TAVILY_MAX_RESULTS  = 2
MAX_RETRIES = 1
MAX_TOKENS  = 500
"""
with open("/content/stock-qa-agent/config/settings.py", "w") as f:
    f.write(settings)
print("✅ Done")
```

**Cell 5 — Run**
```python
from pyngrok import ngrok
import subprocess, time
ngrok.kill()
proc = subprocess.Popen(
    ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(4)
print(f"✅ App live at: {ngrok.connect(8501)}")
```

---

### Option 3 — Streamlit Cloud

1. Push repo to GitHub (ensure `.streamlit/secrets.toml` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New App
3. Set **Main file path**: `stock-qa-agent/app.py`
4. Go to **Settings → Secrets** and add:
```toml
GROQ_API_KEY   = "gsk_your_key_here"
TAVILY_API_KEY = "tvly_your_key_here"
```
5. Click **Deploy** ✅

---

### Option 4 — Hugging Face Spaces

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Select **Streamlit** as SDK
3. Go to **Settings → Variables and Secrets** and add:
```
GROQ_API_KEY   = gsk_your_key_here
TAVILY_API_KEY = tvly_your_key_here
```
4. Push your code:
```bash
git remote add hf https://huggingface.co/spaces/yourusername/stock-qa-agent
git push hf main
```
5. App deploys automatically ✅

---

## 🔑 API Keys Required

| Key | Get it from | Used by |
|-----|-------------|---------|
| `GROQ_API_KEY` | [console.groq.com/keys](https://console.groq.com/keys) | All 4 agents (free tier) |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) | Data Aggregator + News Sentiment (1000 free searches/month) |

---

## 💬 Sample Questions

| Question Type | Example |
|---|---|
| Valuation | `"What is the PE ratio of Infosys?"` |
| Financials | `"What is the revenue and profit growth of TCS?"` |
| Debt | `"What is the debt situation of Adani Enterprises?"` |
| News | `"What is the latest news for Reliance Industries?"` |
| Policy | `"How does the new SEBI regulation affect HDFC Bank?"` |
| Full Analysis | `"Give me a complete analysis of Wipro."` |
| Comparison | `"How is ICICI Bank performing compared to its peers?"` |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Multi-agent orchestration + Human-in-the-Loop |
| [Groq](https://groq.com) | Ultra-fast LLM inference (free tier) |
| [Tavily](https://tavily.com) | AI-optimized web search |
| [Streamlit](https://streamlit.io) | Frontend UI |
| screener.in | Fundamental financial data |
| nseindia.com | NSE India fallback data |
| moneycontrol.com | News and market sentiment |
| economictimes.com | Economic Times fallback news |

---

## ⚙️ Configuration

All configurable values are in `config/settings.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `TAVILY_MAX_RESULTS` | `2` | Search results per query (keep low to save tokens) |
| `MAX_RETRIES` | `1` | Max analyst retry attempts |
| `MAX_TOKENS` | `500` | Max tokens per LLM response |

---

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It does not constitute financial advice. Always consult a SEBI-registered financial advisor before making any investment decisions. The creators are not responsible for any financial decisions made based on this tool's output.

---

## 📄 License

MIT License — free to use, modify, and distribute.
