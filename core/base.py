import logging
from abc import ABC, abstractmethod
from typing import Any

HECUNIT_API_VERSION: int = 1

class HecUnit(ABC):
    """Base class for all HecUnit units."""

    UNIT_NAME: str = None
    UNIT_TYPE: str = None
    UNIT_API_VERSION: int = HECUNIT_API_VERSION
    UNIT_VERSION: str = "0.0.0"

    DEFAULT_CONFIG: dict = {}
    SECRETS_SCHEMA: dict = {}

    def __init__(self, instance_name: str, config: dict) -> None:
        self.instance_name = instance_name
        self._config = config
        self._logger = logging.getLogger(
            f"hecunit.{self.UNIT_NAME or 'unknown'}.{instance_name}"
        )
        self._ready = False

    @abstractmethod
    async def _setup(self) -> None:
        """Boot connections, resolve secrets, validate config"""


    @abstractmethod
    async def _teardown(self) -> None:
        """Close connections, cleanup resources"""


    def get_config(self, key: str, default: Any = None) -> Any:
        """Get config value by key"""
        return self._config.get(key, default)

    def log(self, msg: str, level: str = "info") -> None:
        getattr(self._logger, level)("[%s] %s", self.instance_name, msg)


    async def close(self) -> None:
        """Explicit teardown. Prefer using `async with hec(...)` instead."""
        await self._teardown()
        self._ready = False

    async def __aenter__(self) -> "HecUnit":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"unit={self.UNIT_NAME!r} "
            f"instance={self.instance_name!r} "
            f"ready={self._ready}>"
        )