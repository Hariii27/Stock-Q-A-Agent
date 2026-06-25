import streamlit as st

GROQ_API_KEY   = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

# ── Model Names (all hosted on Groq) ─────────────────────────────────────────
SUPERVISOR_MODEL  = "qwen/qwen3-32b"               # Portfolio Management Supervisor
DATA_MODEL        = "llama-3.1-8b-instant"        # Data Aggregator Agent
NEWS_MODEL        = "llama-3.3-70b-versatile"     # News Sentiment Agent
ANALYST_MODEL     = "llama-3.3-70b-versatile"     # Investment Analysis Agent

# ── Tavily Search Config ──────────────────────────────────────────────────────
SCREENER_DOMAIN     = "screener.in"
MONEYCONTROL_DOMAIN = "moneycontrol.com"
TAVILY_MAX_RESULTS  = 5

# ── Graph Config ──────────────────────────────────────────────────────────────
MAX_RETRIES = 2   # Max re-runs before analyst returns best-effort answer
