import requests
from config import get_settings
from exceptions import (
    FlightSearchError,
    FlightNotFoundError,
    APIRateLimitError,
    APIConnectionError,
    InvalidSearchParametersError
)

settings = get_settings()


class FlightsClient:


    def __init__(self):
        self.base_url = settings.rapidapi_base_url
        self.headers = {
            "x-rapidapi-host": settings.rapidapi_host,
            "x-rapidapi-key": settings.rapidapi_key,
            "Content-Type": "application/json"
        }

    def _request(self, endpoint: str, params: dict) -> dict:

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)

            if response.status_code == 429:
                raise APIRateLimitError(
                    message="RapidAPI rate limit exceeded",
                    details={"endpoint": endpoint}
                )

            if response.status_code in (401, 403):
                raise APIConnectionError(
                    message="Invalid or expired RapidAPI key",
                    details={"status_code": response.status_code}
                )

            if response.status_code != 200:
                raise FlightSearchError(
                    message=f"API returned unexpected status",
                    details={"status_code": response.status_code, "endpoint": endpoint}
                )

            data = response.json()

            if not data.get("status"):
                raise FlightSearchError(
                    message=data.get("message", "Unknown API error"),
                    details={"endpoint": endpoint, "params": params}
                )

            return data

        except requests.exceptions.Timeout:
            raise APIConnectionError(
                message="RapidAPI request timed out",
                details={"endpoint": endpoint, "timeout": 15}
            )

        except requests.exceptions.ConnectionError:
            raise APIConnectionError(
                message="Failed to connect to RapidAPI",
                details={"endpoint": endpoint}
            )

    def search_one_way(
        self,
        departure_id: str,
        arrival_id: str,
        departure_date: str,
        adults: int = 1,
        currency: str = "USD"
    ) -> dict:
        if not all([departure_id, arrival_id, departure_date]):
            raise InvalidSearchParametersError(
                message="departure_id, arrival_id and departure_date are required",
                details={"departure_id": departure_id, "arrival_id": arrival_id}
            )

        return self._request(
            endpoint="/google/flights/search-one-way",
            params={
                "departureId": departure_id,
                "arrivalId": arrival_id,
                "departureDate": departure_date,
                "adults": adults,
                "currency": currency
            }
        )

    def search_roundtrip(
        self,
        departure_id: str,
        arrival_id: str,
        departure_date: str,
        return_date: str,
        adults: int = 1,
        currency: str = "USD"
    ) -> dict:
        if not all([departure_id, arrival_id, departure_date, return_date]):
            raise InvalidSearchParametersError(
                message="All parameters are required for roundtrip search",
                details={}
            )

        return self._request(
            endpoint="/google/flights/search-roundtrip",
            params={
                "departureId": departure_id,
                "arrivalId": arrival_id,
                "departureDate": departure_date,
                "returnDate": return_date,
                "adults": adults,
                "currency": currency
            }
        )

    def get_price_calendar(
        self,
        departure_id: str,
        arrival_id: str,
        year_month: str,
        currency: str = "USD"
    ) -> dict:
        return self._request(
            endpoint="/google/price-calendar/for-one-way",
            params={
                "departureId": departure_id,
                "arrivalId": arrival_id,
                "yearMonth": year_month,
                "currency": currency
            }
        )

    def autocomplete_airport(self, query: str) -> dict:
        return self._request(
            endpoint="/google/auto-complete",
            params={"query": query}
        )