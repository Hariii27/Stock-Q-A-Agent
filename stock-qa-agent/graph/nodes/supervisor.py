import os
from typing import Literal
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from graph.state import AgentState
from config.settings import GROQ_API_KEY, SUPERVISOR_MODEL

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# ── Routing Schema ────────────────────────────────────────────────────────────
class RouteDecision(BaseModel):
    """Supervisor's routing decision."""
    next: Literal["data_aggregator", "news_sentiment", "both", "investment_analyst", "FINISH"]
    reasoning: str

# ── LLM ──────────────────────────────────────────────────────────────────────
supervisor_llm = ChatGroq(
    model=SUPERVISOR_MODEL,
    temperature=0,
    api_key=GROQ_API_KEY,
).with_structured_output(RouteDecision)

# ── System Prompt ─────────────────────────────────────────────────────────────
SUPERVISOR_PROMPT = """You are a Portfolio Management Supervisor Agent.
Your responsibility is to understand the user's stock market question and decide which worker agent(s) should be called.

Available Agents:
1. data_aggregator  - Fundamental data, financials, ratios, peer comparison, shareholding, historical stock data
2. news_sentiment   - Recent news, corporate announcements, market sentiment, macro events affecting stocks
3. investment_analyst - Final analysis (only after workers have run)

Rules:
1. Analyze the user's intent first.
2. If the question is about company fundamentals → return 'data_aggregator'
3. If the question is about recent events or market sentiment → return 'news_sentiment'
4. If both fundamentals and recent events are required → return 'both'
5. If both workers have already run → return 'investment_analyst'
6. If investment_analyst has already responded → return 'FINISH'
7. Never fabricate financial data or news.
8. If information is insufficient, route to the appropriate worker.
"""

# ── Node Function ─────────────────────────────────────────────────────────────
def supervisor_node(state: AgentState) -> dict:
    """
    Reads conversation state and decides which agent runs next.
    Routes to: data_aggregator | news_sentiment | both | investment_analyst | FINISH
    """
    print("  [supervisor] analyzing user query...")

    messages = [SystemMessage(content=SUPERVISOR_PROMPT)] + state["messages"]

    decision: RouteDecision = supervisor_llm.invoke(messages)

    print(f"  [supervisor] -> routing to: {decision.next} | reason: {decision.reasoning}")

    # Track supervisor in agents_called
    agents_called = state.get("agents_called", [])
    if "supervisor" not in agents_called:
        agents_called = agents_called + ["supervisor"]

    return {
        "next": decision.next,
        "agents_called": agents_called,
    }
