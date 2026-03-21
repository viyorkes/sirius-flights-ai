class SiriusBaseException(Exception):
    """Base exception for all Sirius Flights AI exceptions."""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class FlightSearchError(SiriusBaseException):
    """Raised when flight search fails."""
    pass


class FlightNotFoundError(SiriusBaseException):
    """Raised when no flights are found for the given criteria."""
    pass


class APIRateLimitError(SiriusBaseException):
    """Raised when RapidAPI rate limit is exceeded."""
    pass


class APIConnectionError(SiriusBaseException):
    """Raised when connection to RapidAPI fails."""
    pass


class InvalidSearchParametersError(SiriusBaseException):
    """Raised when search parameters are invalid."""
    pass


class RAGError(SiriusBaseException):
    """Raised when RAG pipeline fails."""
    pass


class AgentError(SiriusBaseException):
    """Raised when the LangChain agent fails."""
    pass