from langchain.tools import StructuredTool
from tools.search_flights import search_flights
from tools.compare_flights import compare_flights
from tools.get_price_calendar import get_price_calendar
from tools.recommend_flights import recommend_flights


def get_tools() -> list:
    """
    Returns all available tools for the LangChain agent.
    To add a new tool: create the function and register it here.
    """

    return [
        StructuredTool.from_function(
            func=search_flights,
            name="search_flights",
            description="""Search for available flights between two airports.
            Use when user wants to find flights.
            Input: departure_id (IATA code ex: GRU), arrival_id (IATA code ex: JFK),
            departure_date (YYYY-MM-DD), adults (int), currency (USD),
            trip_type (one_way or roundtrip), return_date (YYYY-MM-DD, only for roundtrip)."""
        ),

        StructuredTool.from_function(
            func=compare_flights,
            name="compare_flights",
            description="""Compare available flights between two airports side by side.
            Use when user wants to compare options or decide between flights.
            Returns cheapest, fastest and fewest stops options.
            Input: departure_id, arrival_id, departure_date, adults, currency."""
        ),

        StructuredTool.from_function(
            func=get_price_calendar,
            name="get_price_calendar",
            description="""Get price calendar for a full month.
            Use when user wants to find the cheapest days to fly in a month.
            Input: departure_id, arrival_id, year_month (YYYY-MM format ex: 2026-05), currency."""
        ),

        StructuredTool.from_function(
            func=recommend_flights,
            name="recommend_flights",
            description="""Recommend best flights based on user preferences.
            Use when user describes preferences like budget, max stops or preferred airlines.
            Input: departure_id, arrival_id, departure_date, budget (float),
            max_stops (int), preferred_airlines (list), adults, currency."""
        ),
    ]