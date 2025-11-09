class PushoverExceptionResponse(Exception):
    """A custom exception for invalid Pushover API responses"""

    status_code: int
    message: str

    def __init__(self, status_code: int, message: str):
        """initializes the custom exception

        Args:
            status_code (int): HTTP status code of the response
            message (str): Errormessage
        """
        super().__init__(message)
        self.status_code = status_code
        self.message = message

    def __repr__(self) -> str:
        return f"{self.status_code}: {self.message}"
