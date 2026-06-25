import streamlit as st
from langchain_core.messages import HumanMessage
from graph.graph_builder import graph

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Q&A Agent",
    page_icon="📈",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📈 Stock Market Q&A Agent")
st.caption(
    "Powered by LangGraph · Groq · Tavily | "
    "Data: screener.in · News: moneycontrol.com"
)
st.divider()

# ── Session State Initialization ──────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []   # list of (role, content, agents_called)

if "processing" not in st.session_state:
    st.session_state.processing = False

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🤖 Agent Pipeline")
    st.markdown("""
    | Agent | Model | Source |
    |-------|-------|--------|
    | 🧠 Supervisor | qwen/qwen3-32b | Routes queries |
    | 📊 Data Aggregator | llama-3.1-8b-instant | screener.in |
    | 📰 News Sentiment | meta-llama/llama-prompt-guard-2-22m | moneycontrol.com |
    | 🔍 Investment Analyst | openai/gpt-oss-120b | Analyzes data |
    """)
    st.divider()
    st.header("💡 Sample Questions")
    sample_questions = [
        "What is the PE ratio and revenue growth of Infosys?",
        "What is the recent news and market sentiment for Reliance Industries?",
        "Give me a complete analysis of TCS including fundamentals and news.",
        "What is the debt situation and promoter holding of Adani Enterprises?",
        "How is HDFC Bank performing compared to its peers?",
    ]
    for q in sample_questions:
        if st.button(q, use_container_width=True):
            st.session_state.prefill_query = q

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ── Chat History Display ──────────────────────────────────────────────────────
for role, content, agents in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)
        if role == "assistant" and agents:
            with st.expander("🔍 Agents Triggered", expanded=False):
                agent_icons = {
                    "supervisor":          "🧠 Supervisor (qwen/qwen3-32b)",
                    "data_aggregator":     "📊 Data Aggregator (llama-3.1-8b-instant → screener.in)",
                    "news_sentiment":      "📰 News Sentiment (meta-llama/llama-prompt-guard-2-22m → moneycontrol.com)",
                    "investment_analyst":  "🔍 Investment Analyst (openai/gpt-oss-120b)",
                }
                for a in agents:
                    st.markdown(f"✅ {agent_icons.get(a, a)}")

# ── Chat Input ────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill_query", "")
user_input = st.chat_input(
    "Ask about any stock — e.g. 'Analyse HDFC Bank fundamentals and recent news'",
    key="chat_input",
)

# Use prefill if sidebar button was clicked
query = prefill or user_input

# ── Process Query ─────────────────────────────────────────────────────────────
if query and not st.session_state.processing:
    st.session_state.processing = True

    # Show user message
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.chat_history.append(("user", query, []))

    # Run the agent graph
    with st.chat_message("assistant"):
        # Live agent status display
        status_placeholder = st.empty()
        answer_placeholder = st.empty()

        with st.spinner("🤔 Agents are working..."):
            try:
                # Build initial state
                initial_state = {
                    "messages":     [HumanMessage(content=query)],
                    "next":         "",
                    "retry_count":  0,
                    "user_query":   query,
                    "data_output":  "",
                    "news_output":  "",
                    "final_answer": "",
                    "agents_called": [],
                }

                # Stream graph execution with status updates
                agents_triggered = []
                final_answer = ""

                for event in graph.stream(initial_state, stream_mode="updates"):
                    for node_name, node_output in event.items():
                        # Update live status
                        agent_display = {
                            "supervisor":         "🧠 Supervisor analyzing your query...",
                            "data_aggregator":    "📊 Fetching fundamental data from screener.in...",
                            "news_sentiment":     "📰 Gathering news from moneycontrol.com...",
                            "investment_analyst": "🔍 Investment Analyst generating insights...",
                        }
                        if node_name in agent_display:
                            status_placeholder.info(agent_display[node_name])

                        # Track agents called
                        called = node_output.get("agents_called", [])
                        for a in called:
                            if a not in agents_triggered:
                                agents_triggered.append(a)

                        # Capture final answer
                        if node_output.get("final_answer"):
                            final_answer = node_output["final_answer"]

                status_placeholder.empty()

                if not final_answer:
                    final_answer = "⚠️ Unable to generate a complete analysis. Please try rephrasing your question with a specific stock name."

                answer_placeholder.markdown(final_answer)

                # Show agents triggered
                if agents_triggered:
                    with st.expander("🔍 Agents Triggered", expanded=False):
                        agent_icons = {
                            "supervisor":         "🧠 Supervisor (qwen/qwen3-32b)",
                            "data_aggregator":    "📊 Data Aggregator (llama-3.1-8b-instant → screener.in)",
                            "news_sentiment":     "📰 News Sentiment (meta-llama/llama-prompt-guard-2-22m → moneycontrol.com)",
                            "investment_analyst": "🔍 Investment Analyst (openai/gpt-oss-120b)",
                        }
                        for a in agents_triggered:
                            st.markdown(f"✅ {agent_icons.get(a, a)}")

                st.session_state.chat_history.append(
                    ("assistant", final_answer, agents_triggered)
                )

            except Exception as e:
                error_msg = f"❌ An error occurred: {str(e)}\n\nPlease check your API keys and try again."
                answer_placeholder.error(error_msg)
                st.session_state.chat_history.append(("assistant", error_msg, []))

    st.session_state.processing = False
    st.rerun()
