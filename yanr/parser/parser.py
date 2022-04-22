import json
from pathlib import Path


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

    def save(self, data) -> None:
        """Save information to storage

        Args: 
            data: list of dicts of habr articles

        Returns: None
        """
        storage_path = Path(self.storage)
        if storage_path.suffix == ".json":
            with open(storage_path, "w", encoding="utf-8") as fw:
                json.dump(data, fw, indent=2, ensure_ascii=True)
        else:
            raise NotImplementedError("Not implemented storage data in database")
