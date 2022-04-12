class Parser:
    def __init__(self, storage: str = 'data.json') -> None:
        """Base class for parsers

        Args:
            storage (str): url to database or path to file

        Returns: None
        """
        self.storage = storage

    def __call__(self) -> None:
        """Parse source and save data to storage

        Returns: None
        """
        pass
