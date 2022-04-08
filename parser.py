class Parser:
    def __init__(self, storage='data.json'):
        """Base class for parsers

        Args:
            storage (str): url to database or path to file
        """
        self.storage = storage

    def __call__(self):
        """Parse source and save data to storage

        Returns: None
        """
        pass
