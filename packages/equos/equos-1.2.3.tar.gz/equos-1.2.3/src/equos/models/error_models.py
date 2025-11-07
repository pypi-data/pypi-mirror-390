class EquosException(Exception):
    """Base class for all Equos exceptions."""

    def __init__(self, message: str):
        super().__init__(message)
        self.name = "EquosException"
