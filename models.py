from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    currency: Optional[str] = "USD"


class FlightSegment(BaseModel):
    from_airport: str
    to_airport: str
    airline: Optional[str]
    flight_number: Optional[str]
    departure_time: Optional[str]
    arrival_time: Optional[str]
    duration_minutes: Optional[int]


class FlightResult(BaseModel):
    price: Optional[float]
    currency: Optional[str]
    airlines: Optional[List[str]]
    departure_time: Optional[str]
    arrival_time: Optional[str]
    duration_minutes: Optional[int]
    stops: Optional[int]


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    tools_used: List[str]


class StreamEvent(BaseModel):
    event: str
    data: str