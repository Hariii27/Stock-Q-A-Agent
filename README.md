# 📈 Stock Market Q&A Agent

A multi-agent AI system for stock market analysis built with **LangGraph**, **Groq**, **Tavily**, and **Streamlit**.

---

## 🏗️ Architecture

```
User Query
    ↓
🧠 Supervisor Agent (Qwen 32B)
    ├── Routes to Data Aggregator, News Sentiment, or both
    ↓
📊 Data Aggregator Agent          📰 News Sentiment Agent
(Llama 3.1 8B + Tavily)          (Llama 3.3 70B + Tavily)
→ screener.in                     → moneycontrol.com
    └──────────────┬───────────────┘
                   ↓
        🔍 Investment Analyst Agent (Deepseek R1-Distill)
                   ↓
        [Data sufficient?]
        YES → Final Answer → User
        NO  → Retry (max 2x) → Supervisor
```

---

## 🤖 Agent Details

| Agent | Model | Provider | Data Source | Role |
|-------|-------|----------|-------------|------|
| 🧠 Supervisor | `qwen-qwq-32b` | Groq | — | Routes queries to appropriate workers |
| 📊 Data Aggregator | `llama-3.1-8b-instant` | Groq | screener.in | Fetches fundamentals, financials, ratios |
| 📰 News Sentiment | `llama-3.3-70b-versatile` | Groq | moneycontrol.com | Fetches news, sentiment, announcements |
| 🔍 Investment Analyst | `deepseek-r1-distill-llama-70b` | Groq | — | Analyzes data, generates insights |

---

## 📁 Project Structure

```
stock-qa-agent/
│
├── app.py                          # Streamlit frontend
├── requirements.txt
├── README.md
│
├── config/
│   ├── __init__.py
│   └── settings.py                 # API keys, model names, constants
│
├── graph/
│   ├── __init__.py
│   ├── state.py                    # AgentState definition
│   ├── graph_builder.py            # LangGraph graph assembly
│   └── nodes/
│       ├── __init__.py
│       ├── supervisor.py           # Qwen 32B supervisor
│       ├── data_aggregator.py      # Llama 3.1 8B + screener.in
│       ├── news_sentiment.py       # Llama 3.3 70B + moneycontrol.com
│       └── investment_analyst.py   # Deepseek R1-Distill analyzer
│
├── tools/
│   ├── __init__.py
│   ├── screener_tool.py            # Tavily configured for screener.in
│   └── moneycontrol_tool.py        # Tavily configured for moneycontrol.com
│
└── .streamlit/
    └── secrets.toml                # API keys (DO NOT commit to GitHub)
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/stock-qa-agent.git
cd stock-qa-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up API Keys

Get your API keys:
- **Groq**: https://console.groq.com/keys (Free tier available)
- **Tavily**: https://app.tavily.com (Free tier: 1000 searches/month)

Add them to `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY   = "gsk_your_key_here"
TAVILY_API_KEY = "tvly_your_key_here"
```

### 4. Run the App

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## ☁️ Streamlit Cloud Deployment

1. Push the project to a **public GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Go to **Settings → Secrets** and add:

```toml
GROQ_API_KEY   = "gsk_your_key_here"
TAVILY_API_KEY = "tvly_your_key_here"
```

6. Click **Deploy** ✅

> ⚠️ **Important**: Never commit `secrets.toml` to GitHub. Add `.streamlit/secrets.toml` to your `.gitignore`.

---

## 💬 Example Questions

- `"What is the PE ratio and revenue growth of Infosys?"`
- `"What is the recent news and market sentiment for Reliance Industries?"`
- `"Give me a complete analysis of TCS including fundamentals and recent news."`
- `"What is the debt situation and promoter holding of Adani Enterprises?"`
- `"How is HDFC Bank performing compared to its peers?"`

---

## 🔄 Agent Routing Logic

| Question Type | Agents Triggered |
|---|---|
| Fundamentals only | Supervisor → Data Aggregator → Analyst |
| News/Sentiment only | Supervisor → News Sentiment → Analyst |
| Complete analysis | Supervisor → Data Aggregator → News Sentiment → Analyst |
| Insufficient data | Analyst → Supervisor → Workers (retry, max 2x) |

---

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It does not provide investment advice. Always consult a SEBI-registered financial advisor before making investment decisions.

---

## 🛠️ Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — Multi-agent orchestration
- **[Groq](https://groq.com)** — Ultra-fast LLM inference
- **[Tavily](https://tavily.com)** — AI-optimized web search
- **[Streamlit](https://streamlit.io)** — Frontend UI
- **screener.in** — Fundamental financial data
- **moneycontrol.com** — News and market sentiment

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
