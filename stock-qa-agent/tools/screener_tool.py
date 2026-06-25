import os
from langchain_community.tools.tavily_search import TavilySearchResults
from config.settings import TAVILY_API_KEY, SCREENER_DOMAIN, TAVILY_MAX_RESULTS

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY


def get_screener_tool():
    """
    Returns a Tavily search tool restricted to screener.in.
    Used by the Data Aggregator Agent to fetch fundamental financial data.
    """
    return TavilySearchResults(
        max_results=TAVILY_MAX_RESULTS,
        include_domains=[SCREENER_DOMAIN],
        name="screener_search",
        description=(
            "Search screener.in for company fundamental data including financials, "
            "ratios, balance sheet, profit & loss, cash flow, shareholding pattern, "
            "and peer comparison. Input should be the company name or NSE/BSE ticker."
        ),
    )
