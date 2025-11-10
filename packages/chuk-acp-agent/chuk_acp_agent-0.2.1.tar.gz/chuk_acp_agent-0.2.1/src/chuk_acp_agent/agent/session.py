"""
Session memory - key-value storage scoped to session lifecycle.
"""

from typing import Any


class SessionMemory:
    """
    Simple key-value storage for session-scoped data.

    Data is stored in memory and cleared when session ends.
    """

    def __init__(self) -> None:
        """Initialize empty memory store."""
        self._store: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """
        Store a value.

        Args:
            key: Storage key
            value: Value to store (must be JSON-serializable for persistence)
        """
        self._store[key] = value

    def get(self, key: str, default: Any | None = None) -> Any:
        """
        Retrieve a value.

        Args:
            key: Storage key
            default: Default value if key not found

        Returns:
            Stored value or default
        """
        return self._store.get(key, default)

    def delete(self, key: str) -> None:
        """
        Delete a value.

        Args:
            key: Storage key
        """
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all stored values."""
        self._store.clear()

    def keys(self) -> list[str]:
        """
        Get all keys.

        Returns:
            List of all storage keys
        """
        return list(self._store.keys())

    def has(self, key: str) -> bool:
        """
        Check if key exists.

        Args:
            key: Storage key

        Returns:
            True if key exists
        """
        return key in self._store
