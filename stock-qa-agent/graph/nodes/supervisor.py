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
    next: Literal["data_aggregator", "news_sentiment", "both", "investment_analyst", "FINISH"]
    reasoning: str

    def validated_next(self) -> str:
        return self.next if self.next != "FINISH" else "both"

# ── LLM ──────────────────────────────────────────────────────────────────────
supervisor_llm = ChatGroq(
    model=SUPERVISOR_MODEL,
    temperature=0,
    api_key=GROQ_API_KEY,
).with_structured_output(RouteDecision)

# ── System Prompt ─────────────────────────────────────────────────────────────
SUPERVISOR_PROMPT = (
    "You are a Portfolio Management Supervisor Agent. "
    "Your responsibility is to understand the user's stock market question "
    "and decide which worker agent(s) should be called.\n\n"
    "Available Agents:\n"
    "1. data_aggregator - Fundamental data, financials, ratios, peer comparison, "
    "shareholding, historical stock data, price, market cap, dividends\n"
    "2. news_sentiment - Recent news, corporate announcements, market sentiment, "
    "macro events, analyst views\n"
    "3. investment_analyst - Final analysis only after workers have already run\n\n"
    "Routing Rules:\n"
    "- ANY question about a stock, company, or market → NEVER return FINISH directly\n"
    "- Questions about numbers, financials, price, ratios, performance → data_aggregator\n"
    "- Questions about news, events, sentiment, announcements → news_sentiment\n"
    "- Questions needing complete picture → both\n"
    "- Simple greetings or completely unrelated topics only → FINISH\n"
    "- When in doubt → both\n\n"
    "Examples:\n"
    "- Tell me about Infosys → both\n"
    "- Is TCS a good company? → both\n"
    "- What happened to Zomato recently? → news_sentiment\n"
    "- What is the PE ratio of HDFC? → data_aggregator\n"
    "- Analyse Wipro completely → both\n"
    "- Hello → FINISH"
)

# ── Node Function ─────────────────────────────────────────────────────────────
def supervisor_node(state: AgentState) -> dict:
    print("  [supervisor] analyzing user query...")

    messages = [SystemMessage(content=SUPERVISOR_PROMPT)] + state["messages"]
    decision: RouteDecision = supervisor_llm.invoke(messages)

    print(f"  [supervisor] routing to: {decision.next} | reason: {decision.reasoning}")

    agents_called = state.get("agents_called", [])
    if "supervisor" not in agents_called:
        agents_called = agents_called + ["supervisor"]

    return {
        "next": decision.validated_next(),
        "agents_called": agents_called,
    }
