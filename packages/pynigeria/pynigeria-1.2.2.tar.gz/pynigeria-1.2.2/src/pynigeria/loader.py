from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from pynigeria.exceptions import DataIntegrityError, DataLoadError
from pynigeria.models import State


class DataLoader:
    """
    Handles loading and validation of data.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        """
        Initialize the data loader.

        Args:
            data_dir: Directory containing data files. Defaults to package data.
        """

        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir

    def load_json(self, filename: str) -> list[dict[str, Any]]:
        """
        Load and parse a JSON data file.

        Args:
            filename: Name of the JSON file to load

        Returns:
            Parsed JSON data as list of dictionaries

        Raises:
            DataLoadError: If file cannot be read or parsed
        """

        file_path = self.data_dir / filename

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as e:
            raise DataLoadError(f"Data file not found: {filename}") from e

        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON in {filename}: {e}") from e

        except Exception as e:
            raise DataLoadError(f"Error loading {filename}: {e}") from e

        if not isinstance(data, list):
            raise DataLoadError(
                f"Expected list in {filename}, got {type(data).__name__}"
            )

        return data

    def load_states(self) -> list[State]:
        """Load and validate state data.

        Returns:
            List of validated State objects

        Raises:
            DataLoadError: If data cannot be loaded
            DataIntegrityError: If validation fails
        """

        data = self.load_json("states.json")
        states = []

        try:
            for item in data:
                states.append(State(**item))
        except ValidationError as e:
            raise DataIntegrityError(f"Invalid state data:\n{e.errors()}") from e

        # Validate unique codes
        codes = [s.code for s in states]
        if len(codes) != len(set(codes)):
            raise DataIntegrityError("Duplicate state codes found")

        return states

