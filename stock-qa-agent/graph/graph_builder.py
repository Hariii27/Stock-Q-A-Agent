from typing import Literal
from langgraph.graph import StateGraph, START, END
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import AgentState
from graph.nodes.supervisor import supervisor_node
from graph.nodes.data_aggregator import data_aggregator_node
from graph.nodes.news_sentiment import news_sentiment_node
from graph.nodes.investment_analyst import investment_analyst_node
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import Literal
from langgraph.graph import StateGraph, START, END
# rest of your code...


# ── Routing: supervisor → workers ─────────────────────────────────────────────
def route_from_supervisor(state: AgentState) -> Literal[
    "data_aggregator", "news_sentiment", "data_then_news", "investment_analyst", "__end__"
]:
    decision = state.get("next", "FINISH")
    mapping = {
        "data_aggregator":    "data_aggregator",
        "news_sentiment":     "news_sentiment",
        "both":               "data_then_news",   # fan-out via sequential path
        "investment_analyst": "investment_analyst",
    }
    return mapping.get(decision, END)


# ── Routing: after single data_aggregator run ─────────────────────────────────
def route_from_supervisor(state: AgentState) -> Literal[
    "data_aggregator", "news_sentiment", "data_then_news", "investment_analyst", "__end__"
]:
    decision = state.get("next", "FINISH")
    mapping = {
        "data_aggregator":    "data_aggregator",
        "news_sentiment":     "news_sentiment",
        "both":               "data_then_news",
        "investment_analyst": "investment_analyst",
    }
    return mapping.get(decision, END)


# ── Routing: after data_aggregator ────────────────────────────────────────────
def route_after_data(state: AgentState) -> Literal["investment_analyst", "news_sentiment"]:
    if state.get("next") == "both" and not state.get("news_output"):
        return "news_sentiment"
    return "investment_analyst"


# ── Routing: analyst → retry or end ──────────────────────────────────────────
def route_from_analyst(state: AgentState) -> Literal["supervisor", "__end__"]:
    if state.get("next") == "retry":
        return "supervisor"
    return END


# ── Graph Assembly ────────────────────────────────────────────────────────────
def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("supervisor",         supervisor_node)
    builder.add_node("data_aggregator",    data_aggregator_node)
    builder.add_node("news_sentiment",     news_sentiment_node)
    builder.add_node("investment_analyst", investment_analyst_node)

    builder.add_edge(START, "supervisor")

    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "data_aggregator":    "data_aggregator",
            "news_sentiment":     "news_sentiment",
            "data_then_news":     "data_aggregator",
            "investment_analyst": "investment_analyst",
            END:                  END,
        },
    )

    builder.add_conditional_edges(
        "data_aggregator",
        route_after_data,
        {
            "news_sentiment":     "news_sentiment",
            "investment_analyst": "investment_analyst",
        },
    )

    builder.add_edge("news_sentiment", "investment_analyst")

    builder.add_conditional_edges(
        "investment_analyst",
        route_from_analyst,
        {
            "supervisor": "supervisor",
            END:          END,
        },
    )

    # ── MemorySaver enables interrupt/resume ──────────────────────────────────
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


graph = build_graph()
