from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """
    Shared state for the Stock Q&A multi-agent graph.
    """
    next             : str
    retry_count      : int
    user_query       : str
    query_type       : str        # simple or complex
    company_context  : str        # brief overview from supervisor
    data_output      : str
    news_output      : str
    final_answer     : str
    agents_called    : list[str]
    use_nse_fallback : bool       # flag for NSE interrupt resume
    use_et_fallback  : bool       # flag for ET interrupt resume
