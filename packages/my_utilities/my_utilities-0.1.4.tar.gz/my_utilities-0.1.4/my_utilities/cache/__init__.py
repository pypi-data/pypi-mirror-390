import warnings
from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, List, Optional


class CacheEngine(ABC):  # pragma: no cover
    """
    Module with abstract class for cache engines
    """

    _logger = Logger(__name__)

    @abstractmethod
    def set(
        self, key: Any, value: Any, ttl: Optional[int] = None, **kwargs: dict[str, Any]
    ) -> bool:
        """
        Set data to cache
        """
        raise NotImplementedError

    @abstractmethod
    def update_ttl(self, key: Any, ttl: int, **kwargs: dict[str, Any]) -> bool:
        """
        Update ttl for concrete key
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, key: Any, **kwargs: dict[str, Any]) -> Optional[Any]:
        """
        Get data from cache
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: Any, **kwargs: dict[str, Any]) -> bool:
        """
        Delete data from cache
        """
        raise NotImplementedError

    @abstractmethod
    def reset_cache(self, **kwargs: dict[str, Any]) -> bool:
        """
        Reset all keys
        """
        raise NotImplementedError

    @abstractmethod
    def _connect(self) -> None:
        """
        Connect to storage
        """
        raise NotImplementedError

    @abstractmethod
    def _disconnect(self) -> None:
        """
        disconnect from storage
        """
        raise NotImplementedError

    def _set_logger(self, logger: Logger) -> None:  # pragma: no cover
        """
        save logger
        """
        if not isinstance(logger, Logger):  # pragma: no cover
            warnings.warn(
                "Logger is not installed because the wrong type."
                " Uses the default logger",
                ResourceWarning,
            )
            return
        self._logger = logger

    @abstractmethod
    def keys(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def lpush(self, key: str, value: Any) -> int:
        raise NotImplementedError

    @abstractmethod
    def lpos(self, key: str, value: Any) -> int:
        raise NotImplementedError

    @abstractmethod
    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def lrem(self, key: str, val: Any, count: int = 0) -> int:
        raise NotImplementedError
