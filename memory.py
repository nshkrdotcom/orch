class Memory:
    """
    Manages the calculator's memory storage.
    """

    def __init__(self):
        """
        Initializes the Memory object.
        Sets _stored_value to None, indicating no value is currently in memory.
        """
        self._stored_value: float | None = None

    def store(self, value: float) -> None:
        """
        Stores a value in memory.

        Args:
            value: The floating-point number to store.
        """
        self._stored_value = value

    def recall(self) -> float:
        """
        Retrieves the value stored in memory.

        Returns:
            The value currently stored in memory.

        Raises:
            ValueError: If memory is empty (no value has been stored yet).
        """
        if self._stored_value is None:
            raise ValueError("Memory is empty. Store a value first.")
        return self._stored_value

    def clear(self) -> None:
        """
        Clears the memory.
        Sets the stored value back to None.
        """
        self._stored_value = None