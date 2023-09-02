class AlreadyExistingId(Exception):
    message: str

    def __init__(self, message):
        self.message = message


class BookingError(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message
