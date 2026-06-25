import os
import re
from typing import Literal
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from graph.state import AgentState
from config.settings import GROQ_API_KEY, ANALYST_MODEL, MAX_RETRIES

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# ── Sufficiency Schema ────────────────────────────────────────────────────────
class AnalysisDecision(BaseModel):
    """Whether the gathered data is sufficient to answer the user's question."""
    is_sufficient: bool
    missing_info: str  # What's missing, if anything

# ── LLMs ─────────────────────────────────────────────────────────────────────
analyst_llm = ChatGroq(
    model=ANALYST_MODEL,
    temperature=0,
    api_key=GROQ_API_KEY,
)

analyst_checker_llm = ChatGroq(
    model=ANALYST_MODEL,
    temperature=0,
    api_key=GROQ_API_KEY,
).with_structured_output(AnalysisDecision)

# ── System Prompt ─────────────────────────────────────────────────────────────
ANALYST_PROMPT = """You are an Investment Analysis Agent in a multi-agent stock market system.

Your responsibility is to analyze structured financial data and news summaries provided by other agents and generate investment insights.

You DO NOT:
- Fetch stock data
- Search for news
- Access external tools
- Hallucinate missing information

You ONLY analyze the information provided to you.

Responsibilities:
1. Fundamental Analysis: Revenue growth, profit growth, margin trends, debt levels, cash generation, return ratios, valuation ratios
2. Comparative Analysis: Compare with peers on growth, profitability, valuation, financial strength
3. News Impact Analysis: Positive factors, negative factors, temporary vs long-term developments
4. Identify Strengths, Weaknesses, and Risks
5. Generate Investment Insights with overall outlook

Important Rules:
- NEVER recommend "Buy", "Sell", "Guaranteed return", or "This stock will go up"
- NEVER predict exact future prices
- NEVER fabricate missing data
- If information is insufficient, state: "Insufficient information available for a complete analysis."
- Distinguish between Facts, Assumptions, and Opinions
- Mention uncertainty whenever conclusions depend on limited information

Output Format:
## Stock Analysis: [Company Name]

### 1. Fundamental Analysis
[Analysis here]

### 2. News & Sentiment Impact
[Analysis here]

### 3. Strengths
[List here]

### 4. Weaknesses
[List here]

### 5. Key Risks
[List here]

### 6. Overall Outlook
[Balanced assessment here]

---
*Disclaimer: This is not financial advice. Please consult a SEBI-registered advisor before making investment decisions.*
"""

SUFFICIENCY_CHECK_PROMPT = """You are checking whether the data gathered by worker agents is sufficient to answer the user's stock market question.

User Question: {user_query}

Data Aggregator Output:
{data_output}

News Sentiment Output:
{news_output}

Evaluate:
- Is there enough financial data to address the user's question?
- Is there relevant news/sentiment data if the question requires it?
- Are there major gaps that would make the analysis misleading?

Return is_sufficient=True only if the data meaningfully addresses the user's question.
Return is_sufficient=False if critical information is missing.
"""

def strip_think_tags(text: str) -> str:
    """Remove Deepseek R1 <think>...</think> reasoning tokens from output."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# ── Node Function ─────────────────────────────────────────────────────────────
def investment_analyst_node(state: AgentState) -> dict:
    """
    Investment Analysis Agent node.
    1. Checks if worker output is sufficient for the user's question.
    2. If sufficient → generates full analysis → sets final_answer.
    3. If insufficient and retries < MAX_RETRIES → increments retry_count, routes back to supervisor.
    4. If retries exhausted → generates best-effort answer with disclaimer.
    """
    print("  [investment_analyst] evaluating data sufficiency...")

    user_query   = state.get("user_query", "")
    data_output  = state.get("data_output", "No fundamental data available.")
    news_output  = state.get("news_output", "No news data available.")
    retry_count  = state.get("retry_count", 0)

    # ── Step 1: Sufficiency Check ─────────────────────────────────────────────
    sufficiency_prompt = SUFFICIENCY_CHECK_PROMPT.format(
        user_query=user_query,
        data_output=data_output,
        news_output=news_output,
    )

    check_result: AnalysisDecision = analyst_checker_llm.invoke([
        HumanMessage(content=sufficiency_prompt)
    ])

    agents_called = state.get("agents_called", [])
    if "investment_analyst" not in agents_called:
        agents_called = agents_called + ["investment_analyst"]

    # ── Step 2: Handle Insufficient Data ─────────────────────────────────────
    if not check_result.is_sufficient and retry_count < MAX_RETRIES:
        print(f"  [investment_analyst] [!] Data insufficient. Retry {retry_count + 1}/{MAX_RETRIES}.")
        print(f"  [investment_analyst] Missing: {check_result.missing_info}")

        retry_message = AIMessage(
            content=(
                f"Data insufficient for a complete analysis. "
                f"Missing: {check_result.missing_info}. "
                f"Re-routing to gather more information. (Attempt {retry_count + 1}/{MAX_RETRIES})"
            ),
            name="investment_analyst",
        )

        return {
            "messages": [retry_message],
            "retry_count": retry_count + 1,
            "next": "retry",
            "agents_called": agents_called,
        }

    # ── Step 3: Generate Full Analysis ───────────────────────────────────────
    print("  [investment_analyst] generating investment analysis...")

    analysis_messages = [
        SystemMessage(content=ANALYST_PROMPT),
        HumanMessage(content=(
            f"User Question: {user_query}\n\n"
            f"=== FINANCIAL DATA (from screener.in) ===\n{data_output}\n\n"
            f"=== NEWS & SENTIMENT (from moneycontrol.com) ===\n{news_output}\n\n"
            f"Please provide a comprehensive analysis based on the above data."
            + ("\n\n[Note: Some data may be incomplete. Provide best-effort analysis with appropriate caveats.]"
               if not check_result.is_sufficient else "")
        )),
    ]

    raw_response = analyst_llm.invoke(analysis_messages)
    clean_response = strip_think_tags(raw_response.content)

    final_message = AIMessage(
        content=clean_response,
        name="investment_analyst",
    )

    print("  [investment_analyst] [v] analysis complete.")

    return {
        "messages": [final_message],
        "final_answer": clean_response,
        "next": "FINISH",
        "agents_called": agents_called,
    }
