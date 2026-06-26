import os
from langchain_community.tools.tavily_search import TavilySearchResults
from config.settings import TAVILY_API_KEY, SCREENER_DOMAIN, NSE_DOMAIN, TAVILY_MAX_RESULTS

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY


def get_screener_tool():
    """Tavily restricted to screener.in for fundamental data."""
    return TavilySearchResults(
        max_results=TAVILY_MAX_RESULTS,
        include_domains=[SCREENER_DOMAIN],
        name="screener_search",
        description=(
            "Search screener.in for PE ratio, financials, balance sheet, "
            "profit and loss, cash flow, shareholding, peer comparison. "
            "Input: company name + metric. Example: 'MCX PE ratio financials'"
        ),
    )


def get_nse_tool():
    """Tavily restricted to nseindia.com as fallback."""
    return TavilySearchResults(
        max_results=TAVILY_MAX_RESULTS,
        include_domains=[NSE_DOMAIN],
        name="nse_search",
        description=(
            "Search NSE India for stock data, financials, and company information. "
            "Use as fallback when screener.in has no results. "
            "Input: company name + metric. Example: 'MCX NSE financials'"
        ),
    )
