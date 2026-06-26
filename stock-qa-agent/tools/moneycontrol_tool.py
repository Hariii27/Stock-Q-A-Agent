import os
from langchain_community.tools.tavily_search import TavilySearchResults
from config.settings import TAVILY_API_KEY, MONEYCONTROL_DOMAIN, ET_DOMAIN, TAVILY_MAX_RESULTS

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY


def get_moneycontrol_tool():
    """Tavily restricted to moneycontrol.com for news."""
    return TavilySearchResults(
        max_results=TAVILY_MAX_RESULTS,
        include_domains=[MONEYCONTROL_DOMAIN],
        name="moneycontrol_search",
        description=(
            "Search moneycontrol.com for recent news, corporate announcements, "
            "market sentiment, analyst views. "
            "Input: company name + news. Example: 'MCX latest news 2025'"
        ),
    )


def get_et_tool():
    """Tavily restricted to Economic Times as fallback."""
    return TavilySearchResults(
        max_results=TAVILY_MAX_RESULTS,
        include_domains=[ET_DOMAIN],
        name="et_search",
        description=(
            "Search Economic Times for news, policies, market events. "
            "Use as fallback when moneycontrol.com has no results. "
            "Input: company name + news. Example: 'MCX Economic Times news 2025'"
        ),
    )
