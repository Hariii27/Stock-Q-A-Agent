import os
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from graph.state import AgentState
from tools.screener_tool import get_screener_tool
from config.settings import GROQ_API_KEY, DATA_MODEL

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# ── LLM ──────────────────────────────────────────────────────────────────────
data_llm = ChatGroq(
    model=DATA_MODEL,
    temperature=0,
    api_key=GROQ_API_KEY,
)

# ── System Prompt ─────────────────────────────────────────────────────────────
DATA_AGGREGATOR_PROMPT = """You are a Financial Data Aggregator Agent.
Your only responsibility is to retrieve and organize financial information using the screener_search tool.
You do not provide investment recommendations.

Search screener.in for the company and collect information such as:
1. Company Profile & Business Description
2. Current Stock Price & 52-week High/Low
3. Market Capitalization
4. Revenue & Revenue Growth
5. Quarterly Results
6. Profit and Loss Statements
7. Balance Sheet highlights
8. Cash Flow Statement
9. Valuation Ratios (PE, PB, EV/EBITDA)
10. Profitability Ratios (ROE, ROCE, Net Margin)
11. Debt Ratios (Debt-to-Equity, Interest Coverage)
12. Shareholding Pattern (Promoter, FII, DII)
13. Dividend Information
14. Historical Price Data (if available)
15. Peer Comparison

Rules:
- Return only factual data retrieved from screener.in
- Do not predict stock prices.
- Do not recommend buying or selling.
- If data is unavailable, explicitly state it.
- Use structured output with clear headings.
- Always mention the data source as screener.in
"""

# ── Agent ─────────────────────────────────────────────────────────────────────
data_agent = create_react_agent(
    model=data_llm,
    tools=[get_screener_tool()],
    prompt=DATA_AGGREGATOR_PROMPT,
)

# ── Node Function ─────────────────────────────────────────────────────────────
def data_aggregator_node(state: AgentState) -> dict:
    """
    Runs the Data Aggregator agent.
    Searches screener.in for fundamental financial data about the queried stock.
    """
    print("  [data_aggregator] fetching fundamental data from screener.in...")

    result = data_agent.invoke({"messages": state["messages"]})
    last_message = result["messages"][-1]

    agent_message = AIMessage(
        content=last_message.content,
        name="data_aggregator"
    )

    agents_called = state.get("agents_called", [])
    if "data_aggregator" not in agents_called:
        agents_called = agents_called + ["data_aggregator"]

    print("  [data_aggregator] [v] data fetched.")

    return {
        "messages": [agent_message],
        "data_output": last_message.content,
        "agents_called": agents_called,
    }
