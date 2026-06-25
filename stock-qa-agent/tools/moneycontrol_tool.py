import os
from langchain_community.tools.tavily_search import TavilySearchResults
from config.settings import TAVILY_API_KEY, TAVILY_MAX_RESULTS

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

def get_moneycontrol_tool():
    return TavilySearchResults(
        max_results=5,
        include_domains=["moneycontrol.com", "economictimes.indiatimes.com", "livemint.com", "businessstandard.com"],
        name="moneycontrol_search",
        description=(
            "Search for recent news, corporate announcements, market sentiment, "
            "analyst views and macro events affecting Indian stocks. "
            "Example: 'MCX India latest news 2025 moneycontrol'"
        ),
    )
