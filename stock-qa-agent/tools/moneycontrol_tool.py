import os
from langchain_community.tools.tavily_search import TavilySearchResults
from config.settings import TAVILY_API_KEY, MONEYCONTROL_DOMAIN, TAVILY_MAX_RESULTS

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY


def get_moneycontrol_tool():
    """
    Returns a Tavily search tool restricted to moneycontrol.com.
    Used by the News Sentiment Agent to fetch recent news and market sentiment.
    """
    return TavilySearchResults(
        max_results=TAVILY_MAX_RESULTS,
        include_domains=[MONEYCONTROL_DOMAIN],
        name="moneycontrol_search",
        description=(
            "Search moneycontrol.com for recent news, corporate announcements, "
            "market sentiment, analyst views, and macro events affecting a stock "
            "or sector. Input should be the company name or stock ticker."
        ),
    )
