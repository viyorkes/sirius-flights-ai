from clients.flights_client import FlightsClient
from exceptions import FlightNotFoundError, InvalidSearchParametersError

client = FlightsClient()


def compare_flights(
    departure_id: str,
    arrival_id: str,
    departure_date: str,
    adults: int = 1,
    currency: str = "USD"
) -> dict:
    """
    Compares available flights between two airports.
    Returns a side-by-side comparison with best options highlighted.
    """

    if not all([departure_id, arrival_id, departure_date]):
        raise InvalidSearchParametersError(
            message="departure_id, arrival_id and departure_date are required",
            details={}
        )

    data = client.search_one_way(
        departure_id=departure_id,
        arrival_id=arrival_id,
        departure_date=departure_date,
        adults=adults,
        currency=currency
    )

    flights = data.get("data", {})
    top_flights = flights.get("topFlights", [])
    other_flights = flights.get("otherFlights", [])
    all_flights = top_flights + other_flights

    if not all_flights:
        raise FlightNotFoundError(
            message=f"No flights found to compare from {departure_id} to {arrival_id}",
            details={
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "departure_date": departure_date
            }
        )

    # Normalize flights for comparison
    normalized = []
    for flight in all_flights[:10]:
        normalized.append({
            "price": flight.get("price"),
            "currency": currency,
            "airlines": flight.get("airlineNames", []),
            "departure_time": flight.get("departureTime"),
            "arrival_time": flight.get("arrivalTime"),
            "duration_minutes": flight.get("duration"),
            "stops": flight.get("stops", 0),
            "segments_count": len(flight.get("segments", [])),
            "detail_token": flight.get("detailToken")
        })

    # Sort by price
    by_price = sorted(normalized, key=lambda x: x["price"] or 9999)

    # Sort by duration
    by_duration = sorted(normalized, key=lambda x: x["duration_minutes"] or 9999)

    # Sort by stops
    by_stops = sorted(normalized, key=lambda x: x["stops"] or 0)

    prices = [f["price"] for f in normalized if f["price"]]
    durations = [f["duration_minutes"] for f in normalized if f["duration_minutes"]]

    return {
        "found": True,
        "total_options": len(all_flights),
        "summary": {
            "cheapest_price": min(prices) if prices else None,
            "most_expensive_price": max(prices) if prices else None,
            "fastest_duration_minutes": min(durations) if durations else None,
            "slowest_duration_minutes": max(durations) if durations else None,
            "price_difference": max(prices) - min(prices) if prices else None
        },
        "best_price": by_price[:3],
        "fastest": by_duration[:3],
        "fewest_stops": by_stops[:3],
        "all_options": normalized
    }
