import os
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from graph.state import AgentState
from tools.moneycontrol_tool import get_moneycontrol_tool
from config.settings import GROQ_API_KEY, NEWS_MODEL
from langchain_core.messages import HumanMessage

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# ── LLM ──────────────────────────────────────────────────────────────────────
news_llm = ChatGroq(
    model=NEWS_MODEL,
    temperature=0,
    api_key=GROQ_API_KEY,
)

# ── System Prompt ─────────────────────────────────────────────────────────────
NEWS_SENTIMENT_PROMPT = """You are a News Sentiment Agent.
Your responsibility is to gather and summarize recent news related to a company, stock, sector, or market event.
Use the moneycontrol_search tool to collect information from moneycontrol.com.

Tasks:
1. Collect recent news articles (last 30–90 days preferred)
2. Identify important corporate events (earnings, mergers, leadership changes, regulatory news)
3. Determine whether the overall news tone is Positive, Negative, or Neutral
4. Detect recurring themes (e.g., debt concerns, growth momentum, sector headwinds)
5. Summarize the potential impact on the company's stock

Output Format:
- Recent Headlines (with dates if available)
- Key Events
- Sentiment: [Positive / Negative / Neutral / Mixed]
- Recurring Themes
- Potential Impact Summary

Rules:
- Do not provide investment advice.
- Do not speculate without factual basis.
- Distinguish facts from opinions.
- Mention publication dates when available.
- Ignore unverified rumors.
- Always mention the data source as moneycontrol.com
"""

# ── Agent ─────────────────────────────────────────────────────────────────────
news_agent = create_react_agent(
    model=news_llm,
    tools=[get_moneycontrol_tool()],
    prompt=NEWS_SENTIMENT_PROMPT,
)

# ── Node Function ─────────────────────────────────────────────────────────────
def news_sentiment_node(state: AgentState) -> dict:
    """
    Runs the News Sentiment agent.
    Searches moneycontrol.com for recent news and market sentiment about the queried stock.
    """
    print("  [news_sentiment] fetching news from moneycontrol.com...")

    
enhanced_messages = state["messages"] + [
    HumanMessage(content=(
        f"Search for: '{state.get('user_query', '')} India stock news latest 2025 moneycontrol'"
    ))
]
result = news_agent.invoke({"messages": enhanced_messages})
    last_message = result["messages"][-1]

    agent_message = AIMessage(
        content=last_message.content,
        name="news_sentiment"
    )

    agents_called = state.get("agents_called", [])
    if "news_sentiment" not in agents_called:
        agents_called = agents_called + ["news_sentiment"]

    print("  [news_sentiment] [v] news fetched.")

    return {
        "messages": [agent_message],
        "news_output": last_message.content,
        "agents_called": agents_called,
    }
