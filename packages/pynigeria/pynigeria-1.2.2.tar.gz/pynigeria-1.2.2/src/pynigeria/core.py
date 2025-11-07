from __future__ import annotations

from pathlib import Path
from typing import cast

from pynigeria.exceptions import NotFoundError
from pynigeria.loader import DataLoader
from pynigeria.models import State


class Nigeria:
    """
    Main entry point for accessing Nigerian geographic data.

    Example:
    ```python
    nigeria = Nigeria()
    state = nigeria.get_state("Lagos")
    print(state.capital)
    > 'Ikeja'
    ```
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        """
        Initialize the Nigeria data interface.

        Args:
            data_dir: Optional custom data directory. Defaults to package data.
        """

        self._loader = DataLoader(data_dir)

        # Lazy-loaded data
        self._states: list[State] | None = None

        # Lazy-loaded indices
        self._state_by_code: dict[str, State] | None = None
        self._state_by_name: dict[str, State] | None = None

    # ========================================================================
    # Data Access (with lazy loading)
    # ========================================================================
    def states(self) -> list[State]:
        """
        Get all Nigerian states.

        Returns:
            List of all states. Data is loaded and cached on first call.
        """

        if self._states is None:
            self._states = self._loader.load_states()
            self._build_state_indices()
        return self._states

    # ========================================================================
    # Query Methods - States
    # ========================================================================
    def get_state_details(
        self, name: str | None = None, code: str | None = None
    ) -> State:
        """
        Get state details by name or ISO code.

        Args:
            name: State name (e.g., "Lagos", "Kano")
            code: ISO 3166-2 state code (e.g., "NG-LA" for Lagos)

        Returns:
            The matching State object

        Raises:
            NotFoundError: If state is not found
        """

        if name is not None:
            return self.get_state(name)
        elif code is not None:
            return self.get_state_by_code(code)
        else:
            raise ValueError("Either name or code must be provided")

    def get_state(self, name: str) -> State:
        """
        Get a state by its name (case-insensitive).

        Args:
            name: State name (e.g., "Lagos", "Kano")

        Returns:
            The matching State object

        Raises:
            NotFoundError: If state is not found
        """

        if self._state_by_name is None:
            self.states()  # Load data and build indices

            # Change type annotation to remove None val
            self._state_by_name = cast(dict[str, State], self._state_by_name)

        name_key = name.lower().strip()
        if name_key not in self._state_by_name:
            raise NotFoundError(f"State not found: {name}")

        return self._state_by_name[name_key]

    def get_state_by_code(self, code: str) -> State:
        """
        Get a state by its ISO code.

        Args:
            code: ISO 3166-2 state code (e.g., "NG-LA" for Lagos)

        Returns:
            The matching State object

        Raises:
            NotFoundError: If state code is not found
        """

        if self._state_by_code is None:
            self.states()  # Load data and build indices

            # Change type annotation to remove None val
            self._state_by_code = cast(dict[str, State], self._state_by_code)

        code_upper = code.upper().strip()
        if code_upper not in self._state_by_code:
            raise NotFoundError(f"State code not found: {code}")

        return self._state_by_code[code_upper]

    def state_search(self, query: str) -> list[State]:
        """
        Search for states by partial name match (case-insensitive).

        Args:
            query: Partial state name to search for

        Returns:
            List of matching State objects
        """

        if self._state_by_name is None:
            # Build state indices
            self.states()

            # Change type annotation to remove None val
            self._state_by_name = cast(dict[str, State], self._state_by_name)

        query_lower = query.lower().strip()

        if not query_lower:
            return []  # early return for empty query

        if query_lower in self._state_by_name:  # exact match
            return [self._state_by_name[query_lower]]

        # Partial match
        return [s for name, s in self._state_by_name.items() if query_lower in name]

    def _build_state_indices(self) -> None:
        """Build lookup indices for states."""
        if self._states is None:
            return

        self._state_by_code = {s.code.upper(): s for s in self._states}
        self._state_by_name = {s.name.lower(): s for s in self._states}
