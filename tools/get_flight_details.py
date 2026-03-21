from clients.flights_client import FlightsClient
from exceptions import FlightNotFoundError, InvalidSearchParametersError

client = FlightsClient()


def get_flight_details(
    detail_token: str,
    currency: str = "USD"
) -> dict:
    """
    Returns detailed information about a specific flight.
    Uses the detailToken returned by search_flights or compare_flights.
    """

    if not detail_token:
        raise InvalidSearchParametersError(
            message="detail_token is required",
            details={}
        )

    data = client._request(
        endpoint="/web/flights/details",
        params={
            "token": detail_token,
            "currency": currency
        }
    )

    itinerary = data.get("data", {}).get("itinerary", {})

    if not itinerary:
        raise FlightNotFoundError(
            message="Flight details not found for given token",
            details={"detail_token": detail_token}
        )

    legs = itinerary.get("legs", [])
    pricing = itinerary.get("pricingOptions", [])

    return {
        "found": True,
        "itinerary_id": itinerary.get("id"),
        "legs": [
            {
                "origin": leg.get("origin", {}).get("displayCode"),
                "destination": leg.get("destination", {}).get("displayCode"),
                "departure": leg.get("departure"),
                "arrival": leg.get("arrival"),
                "duration_minutes": leg.get("duration"),
                "stops": leg.get("stopCount"),
                "segments": [
                    {
                        "from": s.get("origin", {}).get("displayCode"),
                        "to": s.get("destination", {}).get("displayCode"),
                        "flight_number": s.get("flightNumber"),
                        "airline": s.get("marketingCarrier", {}).get("name"),
                        "aircraft": None,
                        "departure": s.get("departure"),
                        "arrival": s.get("arrival"),
                        "duration_minutes": s.get("duration")
                    }
                    for s in leg.get("segments", [])
                ]
            }
            for leg in legs
        ],
        "pricing": [
            {
                "agent": p.get("agents", [{}])[0].get("name") if p.get("agents") else None,
                "total_price": p.get("totalPrice"),
                "booking_url": p.get("agents", [{}])[0].get("url") if p.get("agents") else None
            }
            for p in pricing[:3]
        ]
    }