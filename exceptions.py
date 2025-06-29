# exceptions.py

class DivisionByZeroError(Exception):
    """
    Custom exception raised for division by zero operations.
    """
    def __init__(self, message="Division by zero is not allowed."):
        """
        Constructor for DivisionByZeroError.

        Args:
            message (str, optional): The error message.
                                     Defaults to "Division by zero is not allowed.".
        """
        self.message = message
        super().__init__(self.message)