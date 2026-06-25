import os
import streamlit as st

try:
    GROQ_API_KEY   = st.secrets["GROQ_API_KEY"]
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
except Exception:
    GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
    TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

SUPERVISOR_MODEL  = "qwen/qwen3-32b"
DATA_MODEL        = "llama-3.1-8b-instant"
NEWS_MODEL        = "llama-3.3-70b-versatile"
ANALYST_MODEL     = "llama-3.3-70b-versatile"

SCREENER_DOMAIN     = "screener.in"
MONEYCONTROL_DOMAIN = "moneycontrol.com"
TAVILY_MAX_RESULTS  = 5

MAX_RETRIES = 2
