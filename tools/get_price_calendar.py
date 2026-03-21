from clients.flights_client import FlightsClient
from exceptions import FlightNotFoundError, InvalidSearchParametersError

client = FlightsClient()


def get_price_calendar(
    departure_id: str,
    arrival_id: str,
    year_month: str,
    currency: str = "USD"
) -> dict:
    """
    Returns a price calendar for a given month.
    Helps user find the cheapest days to fly.
    Ex: year_month = "2026-05"
    """

    if not all([departure_id, arrival_id, year_month]):
        raise InvalidSearchParametersError(
            message="departure_id, arrival_id and year_month are required",
            details={}
        )

    data = client.get_price_calendar(
        departure_id=departure_id,
        arrival_id=arrival_id,
        year_month=year_month,
        currency=currency
    )

    calendar_data = data.get("data", {})

    if not calendar_data:
        raise FlightNotFoundError(
            message=f"No price calendar found for {departure_id} to {arrival_id}",
            details={
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "year_month": year_month
            }
        )

    # Extract days with prices
    days = calendar_data.get("days", [])

    if not days:
        raise FlightNotFoundError(
            message=f"No prices available for {year_month}",
            details={"year_month": year_month}
        )

    # Normalize days
    normalized = []
    for day in days:
        if day.get("price"):
            normalized.append({
                "date": day.get("date"),
                "price": day.get("price"),
                "currency": currency
            })

    if not normalized:
        raise FlightNotFoundError(
            message="No prices found in calendar",
            details={}
        )

    # Sort by price to find best days
    by_price = sorted(normalized, key=lambda x: x["price"])
    prices = [d["price"] for d in normalized]

    return {
        "found": True,
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "year_month": year_month,
        "currency": currency,
        "summary": {
            "cheapest_price": min(prices),
            "most_expensive_price": max(prices),
            "average_price": round(sum(prices) / len(prices), 2),
            "total_days_available": len(normalized)
        },
        "cheapest_days": by_price[:5],
        "most_expensive_days": by_price[-5:],
        "full_calendar": normalized
    }