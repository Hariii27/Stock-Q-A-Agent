import os
from langchain_community.tools.tavily_search import TavilySearchResults
from config.settings import TAVILY_API_KEY, TAVILY_MAX_RESULTS

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

def get_screener_tool():
    return TavilySearchResults(
        max_results=5,
        include_domains=["screener.in", "moneycontrol.com", "nseindia.com", "bseindia.com", "tickertape.in"],
        name="screener_search",
        description=(
            "Search for company fundamental data including PE ratio, financials, "
            "ratios, balance sheet, profit and loss, cash flow, shareholding pattern, "
            "and peer comparison. Input should be company name with NSE ticker. "
            "Example: 'MCX India PE ratio financials screener'"
        ),
    )
