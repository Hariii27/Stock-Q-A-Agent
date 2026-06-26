import os
import streamlit as st

try:
    GROQ_API_KEY   = st.secrets["GROQ_API_KEY"]
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
except Exception:
    GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
    TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

SUPERVISOR_MODEL  = "meta-llama/llana-4-scout-17b-16e-instrcut"
DATA_MODEL        = "meta-llama/llama-4-scout-17b-16e-instruct"
NEWS_MODEL        = "llama-3.3-70b-versatile"
ANALYST_MODEL     = "qwen/qwen-32b"

SCREENER_DOMAIN     = "screener.in"
NSE_DOMAIN          = "nseindia.com"
MONEYCONTROL_DOMAIN = "moneycontrol.com"
ET_DOMAIN           = "economictimes.indiatimes.com"
TAVILY_MAX_RESULTS  = 2

MAX_RETRIES = 2
MAX_TOKENS  = 500
