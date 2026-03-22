TOOLS_SCHEMA = [
    {
        "name": "search_flights",
        "description": "Search for available flights between two airports. Use when user wants to find flights.",
        "input_schema": {
            "type": "object",
            "properties": {
                "departure_id": {
                    "type": "string",
                    "description": "IATA airport code for departure. Ex: GRU, JFK, LHR"
                },
                "arrival_id": {
                    "type": "string",
                    "description": "IATA airport code for arrival. Ex: JFK, GRU, CDG"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date in YYYY-MM-DD format. Ex: 2026-06-01"
                },
                "adults": {
                    "type": "integer",
                    "description": "Number of adult passengers",
                    "default": 1
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code. Ex: USD, BRL, EUR",
                    "default": "USD"
                },
                "trip_type": {
                    "type": "string",
                    "description": "Type of trip: one_way or roundtrip",
                    "enum": ["one_way", "roundtrip"],
                    "default": "one_way"
                },
                "return_date": {
                    "type": "string",
                    "description": "Return date in YYYY-MM-DD format. Required for roundtrip."
                }
            },
            "required": ["departure_id", "arrival_id", "departure_date"]
        }
    },
    {
        "name": "compare_flights",
        "description": "Compare available flights side by side. Use when user wants to decide between options.",
        "input_schema": {
            "type": "object",
            "properties": {
                "departure_id": {
                    "type": "string",
                    "description": "IATA airport code for departure"
                },
                "arrival_id": {
                    "type": "string",
                    "description": "IATA airport code for arrival"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date in YYYY-MM-DD format"
                },
                "adults": {
                    "type": "integer",
                    "description": "Number of adult passengers",
                    "default": 1
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code",
                    "default": "USD"
                }
            },
            "required": ["departure_id", "arrival_id", "departure_date"]
        }
    },
    {
        "name": "get_price_calendar",
        "description": "Get price calendar for a full month. Use when user wants cheapest days to fly.",
        "input_schema": {
            "type": "object",
            "properties": {
                "departure_id": {
                    "type": "string",
                    "description": "IATA airport code for departure"
                },
                "arrival_id": {
                    "type": "string",
                    "description": "IATA airport code for arrival"
                },
                "year_month": {
                    "type": "string",
                    "description": "Year and month in YYYY-MM format. Ex: 2026-06"
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code",
                    "default": "USD"
                }
            },
            "required": ["departure_id", "arrival_id", "year_month"]
        }
    },
    {
        "name": "recommend_flights",
        "description": "Recommend best flights based on user preferences like budget, stops and airlines.",
        "input_schema": {
            "type": "object",
            "properties": {
                "departure_id": {
                    "type": "string",
                    "description": "IATA airport code for departure"
                },
                "arrival_id": {
                    "type": "string",
                    "description": "IATA airport code for arrival"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date in YYYY-MM-DD format"
                },
                "budget": {
                    "type": "number",
                    "description": "Maximum budget in chosen currency"
                },
                "max_stops": {
                    "type": "integer",
                    "description": "Maximum number of stops. 0 for direct flights only."
                },
                "preferred_airlines": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of preferred airline names. Ex: ['LATAM', 'American']"
                },
                "adults": {
                    "type": "integer",
                    "description": "Number of adult passengers",
                    "default": 1
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code",
                    "default": "USD"
                }
            },
            "required": ["departure_id", "arrival_id", "departure_date"]
        }
    },
    {
        "name": "get_flight_details",
        "description": "Get detailed information and booking URL for a specific flight.",
        "input_schema": {
            "type": "object",
            "properties": {
                "detail_token": {
                    "type": "string",
                    "description": "The detailToken returned by search_flights or compare_flights"
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code",
                    "default": "USD"
                }
            },
            "required": ["detail_token"]
        }
    }
]