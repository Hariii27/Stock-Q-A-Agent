import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from graph.graph_builder import graph

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Stock Q&A Agent", page_icon="📈", layout="wide")

st.title("📈 Stock Market Q&A Agent")
st.caption("Powered by LangGraph · Groq · Tavily | Data: screener.in · News: moneycontrol.com")
st.divider()

# ── Session State ─────────────────────────────────────────────────────────────
if "chat_history"   not in st.session_state: st.session_state.chat_history   = []
if "processing"     not in st.session_state: st.session_state.processing     = False
if "interrupt_data" not in st.session_state: st.session_state.interrupt_data = None
if "thread_id"      not in st.session_state: st.session_state.thread_id      = "stock-qa-" + str(uuid.uuid4())

# ── Always available config ───────────────────────────────────────────────────
thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🤖 Agent Pipeline")
    st.markdown("""
| Agent | Model |
|-------|-------|
| 🧠 Supervisor | llama-4-scout-17b |
| 📊 Data Aggregator | llama-4-scout-17b |
| 📰 News Sentiment | llama-3.3-70b |
| 🔍 Investment Analyst | qwen3-32b |
    """)
    st.divider()
    st.header("💡 Sample Questions")
    samples = [
        "What is the PE ratio of Infosys?",
        "What is the recent news for Reliance Industries?",
        "Give me a complete analysis of TCS.",
        "What is the debt situation of Adani Enterprises?",
        "How is HDFC Bank performing vs peers?",
    ]
    for q in samples:
        if st.button(q, use_container_width=True):
            st.session_state.prefill_query = q
    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history   = []
        st.session_state.interrupt_data = None
        st.session_state.thread_id      = "stock-qa-" + str(uuid.uuid4())
        st.rerun()

# ── Chat History ──────────────────────────────────────────────────────────────
for role, content, agents in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)
        if role == "assistant" and agents:
            with st.expander("🔍 Agents Triggered", expanded=False):
                icons = {
                    "supervisor":         "🧠 Supervisor (llama-4-scout-17b)",
                    "data_aggregator":    "📊 Data Aggregator → screener.in",
                    "news_sentiment":     "📰 News Sentiment → moneycontrol.com",
                    "investment_analyst": "🔍 Investment Analyst (qwen3-32b)",
                }
                for a in agents:
                    st.markdown(f"✅ {icons.get(a, a)}")

# ── Interrupt Handler ─────────────────────────────────────────────────────────
if st.session_state.interrupt_data:
    idata = st.session_state.interrupt_data
    st.warning(f"⚠️ {idata['question']}")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes", use_container_width=True):
            st.session_state.interrupt_data = None
            source = idata.get("source", "")
            resume_state = {}
            if source == "data_aggregator":
                resume_state = {"use_nse_fallback": True}
            elif source == "news_sentiment":
                resume_state = {"use_et_fallback": True}

            with st.spinner("🔄 Searching fallback source..."):
                try:
                    agents_triggered = []
                    final_answer = ""
                    for event in graph.stream(resume_state, config=thread_config, stream_mode="updates"):
                        for node_name, node_output in event.items():
                            for a in node_output.get("agents_called", []):
                                if a not in agents_triggered:
                                    agents_triggered.append(a)
                            if node_output.get("final_answer"):
                                final_answer = node_output["final_answer"]
                    if final_answer:
                        st.session_state.chat_history.append(("assistant", final_answer, agents_triggered))
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            st.rerun()

    with col2:
        if st.button("❌ No", use_container_width=True):
            st.session_state.interrupt_data = None
            with st.spinner("🔄 Continuing..."):
                try:
                    agents_triggered = []
                    final_answer = ""
                    for event in graph.stream(None, config=thread_config, stream_mode="updates"):
                        for node_name, node_output in event.items():
                            for a in node_output.get("agents_called", []):
                                if a not in agents_triggered:
                                    agents_triggered.append(a)
                            if node_output.get("final_answer"):
                                final_answer = node_output["final_answer"]
                    if final_answer:
                        st.session_state.chat_history.append(("assistant", final_answer, agents_triggered))
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            st.rerun()

# ── Chat Input ────────────────────────────────────────────────────────────────
prefill    = st.session_state.pop("prefill_query", "")
user_input = st.chat_input("Ask about any stock...")
query      = prefill or user_input

# ── Process Query ─────────────────────────────────────────────────────────────
if query and not st.session_state.processing and not st.session_state.interrupt_data:
    st.session_state.processing = True

    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.chat_history.append(("user", query, []))

    with st.chat_message("assistant"):
        status_ph = st.empty()
        answer_ph = st.empty()

        with st.spinner("🤔 Agents working..."):
            try:
                initial_state = {
                    "messages":          [HumanMessage(content=query)],
                    "next":              "",
                    "retry_count":       0,
                    "user_query":        query,
                    "query_type":        "complex",
                    "company_context":   "",
                    "data_output":       "",
                    "news_output":       "",
                    "final_answer":      "",
                    "agents_called":     [],
                    "use_nse_fallback":  False,
                    "use_et_fallback":   False,
                }

                agent_display = {
                    "supervisor":         "🧠 Supervisor analyzing query...",
                    "data_aggregator":    "📊 Fetching data from screener.in...",
                    "news_sentiment":     "📰 Fetching news from moneycontrol.com...",
                    "investment_analyst": "🔍 Generating investment insights...",
                }

                agents_triggered = []
                final_answer     = ""
                interrupted      = False

                for event in graph.stream(initial_state, config=thread_config, stream_mode="updates"):
                    if "__interrupt__" in event:
                        st.session_state.interrupt_data = event["__interrupt__"][0].value
                        interrupted = True
                        break

                    for node_name, node_output in event.items():
                        if node_name in agent_display:
                            status_ph.info(agent_display[node_name])
                        for a in node_output.get("agents_called", []):
                            if a not in agents_triggered:
                                agents_triggered.append(a)
                        if node_output.get("final_answer"):
                            final_answer = node_output["final_answer"]

                status_ph.empty()

                if not interrupted:
                    if not final_answer:
                        final_answer = "⚠️ Unable to generate analysis. Please try with a specific stock name."
                    answer_ph.markdown(final_answer)

                    if agents_triggered:
                        with st.expander("🔍 Agents Triggered", expanded=False):
                            icons = {
                                "supervisor":         "🧠 Supervisor (llama-4-scout-17b)",
                                "data_aggregator":    "📊 Data Aggregator → screener.in",
                                "news_sentiment":     "📰 News Sentiment → moneycontrol.com",
                                "investment_analyst": "🔍 Investment Analyst (qwen3-32b)",
                            }
                            for a in agents_triggered:
                                st.markdown(f"✅ {icons.get(a, a)}")

                    st.session_state.chat_history.append(("assistant", final_answer, agents_triggered))

            except Exception as e:
                err = f"❌ An error occurred: {str(e)}\n\nPlease check your API keys and try again."
                answer_ph.error(err)
                st.session_state.chat_history.append(("assistant", err, []))

    st.session_state.processing = False
    st.rerun()
