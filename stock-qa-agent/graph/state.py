from typing import TypedDict, Annotated
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """
    Shared state for the Stock Q&A multi-agent graph.

    Fields
    ------
    messages      : auto-append message list (inherited from MessagesState)
    next          : supervisor's routing decision
    retry_count   : number of re-run attempts triggered by investment analyst
    user_query    : original user question (preserved for analyst comparison)
    data_output   : raw output from Data Aggregator agent
    news_output   : raw output from News Sentiment agent
    final_answer  : polished answer returned to Streamlit UI
    agents_called : list of agent names invoked in this run (for UI display)
    """
    next          : str
    retry_count   : int
    user_query    : str
    data_output   : str
    news_output   : str
    final_answer  : str
    agents_called : list[str]
