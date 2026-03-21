from clients.flights_client import FlightsClient
from exceptions import FlightNotFoundError, InvalidSearchParametersError

client = FlightsClient()


def recommend_flights(
    departure_id: str,
    arrival_id: str,
    departure_date: str,
    budget: float = None,
    max_stops: int = None,
    preferred_airlines: list = None,
    adults: int = 1,
    currency: str = "USD"
) -> dict:
    """
    Recommends best flights based on user preferences.
    Filters by budget, max stops and preferred airlines.
    Used when user describes what they want in natural language.
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
            message=f"No flights found from {departure_id} to {arrival_id}",
            details={
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "departure_date": departure_date
            }
        )

    # Normalize
    normalized = []
    for flight in all_flights:
        normalized.append({
            "price": flight.get("price"),
            "currency": currency,
            "airlines": flight.get("airlineNames", []),
            "airline_code": flight.get("airlineCode"),
            "departure_time": flight.get("departureTime"),
            "arrival_time": flight.get("arrivalTime"),
            "duration_minutes": flight.get("duration"),
            "stops": flight.get("stops", 0),
            "detail_token": flight.get("detailToken"),
            "segments": [
                {
                    "from": s.get("departureAirportCode"),
                    "to": s.get("arrivalAirportCode"),
                    "airline": s.get("airline", {}).get("airlineName"),
                    "flight_number": s.get("airline", {}).get("flightNumber"),
                    "aircraft": s.get("aircraftName"),
                    "departure_time": s.get("departureTime"),
                    "arrival_time": s.get("arrivalTime"),
                    "duration_minutes": s.get("durationMinutes")
                }
                for s in flight.get("segments", [])
            ]
        })

    # Apply filters based on user preferences
    filtered = normalized

    if budget:
        filtered = [f for f in filtered if f["price"] and f["price"] <= budget]

    if max_stops is not None:
        filtered = [f for f in filtered if f["stops"] is not None and f["stops"] <= max_stops]

    if preferred_airlines:
        preferred_lower = [a.lower() for a in preferred_airlines]
        filtered = [
            f for f in filtered
            if any(a.lower() in preferred_lower for a in f["airlines"])
        ]

    if not filtered:
        return {
            "found": False,
            "message": "No flights match your preferences. Try adjusting budget or stops.",
            "suggestions": {
                "cheapest_available": min(normalized, key=lambda x: x["price"] or 9999),
                "fewest_stops": min(normalized, key=lambda x: x["stops"] or 0)
            }
        }

    # Score and rank
    def score(flight):
        price_score = 1 / (flight["price"] or 9999)
        stop_score = 1 / (flight["stops"] + 1)
        duration_score = 1 / (flight["duration_minutes"] or 9999)
        return price_score + stop_score + duration_score

    ranked = sorted(filtered, key=score, reverse=True)

    return {
        "found": True,
        "total_found": len(filtered),
        "filters_applied": {
            "budget": budget,
            "max_stops": max_stops,
            "preferred_airlines": preferred_airlines
        },
        "recommendations": ranked[:5]
    }
