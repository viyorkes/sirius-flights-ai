from clients.flights_client import FlightsClient
from exceptions import FlightNotFoundError

client = FlightsClient()


def search_flights(
    departure_id: str,
    arrival_id: str,
    departure_date: str,
    adults: int = 1,
    currency: str = "USD",
    trip_type: str = "one_way",
    return_date: str = None
) -> dict:
    """
    Searches for available flights between two airports.
    Supports one-way and round-trip searches.
    """

    if trip_type == "roundtrip" and return_date:
        data = client.search_roundtrip(
            departure_id=departure_id,
            arrival_id=arrival_id,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            currency=currency
        )
    else:
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

    # Normalize and return top 5 results
    results = []
    for flight in all_flights[:5]:
        results.append({
            "price": flight.get("price"),
            "currency": currency,
            "airlines": flight.get("airlineNames", []),
            "airline_code": flight.get("airlineCode"),
            "departure_airport": flight.get("departureAirportCode"),
            "arrival_airport": flight.get("arrivalAirportCode"),
            "departure_date": flight.get("departureDate"),
            "departure_time": flight.get("departureTime"),
            "arrival_date": flight.get("arrivalDate"),
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

    return {
        "found": True,
        "total": len(all_flights),
        "showing": len(results),
        "trip_type": trip_type,
        "results": results
    }