from __future__ import annotations
from collections import OrderedDict
from collections.abc import Callable
from threading import Timer
from typing import Any


class TTLDict:
    """
    TTLDict(default_ttl=300)

    A dictionary-like container with time-to-live (TTL)
     functionality for its keys. The keys in this
     dictionary automatically expire and get removed after
     a specified duration.


    :param default_ttl: The default time-to-live for keys in seconds.
    :type default_ttl: int
    :param _dict:  The main dictionary to store key-value pairs.
    :type _dict: OrderedDict
    :param _timers: A dictionary to store Timer objects for each key.
    :type _timers: dict
    """

    def __init__(
        self,
        default_ttl: int = 300,
        function_on_expired: Callable[[Any], None] | None = None,
    ) -> None:  # pragma: no cover
        """
        init ttl dict

        :param default_ttl: The default time-to-live for keys in seconds.
        :type default_ttl: int
        :param function_on_expired: the function that will be used when the key expires
        :type function_on_expired: Callable[[Any], None] | None
        """
        self._default_ttl = default_ttl
        self._dict = OrderedDict()  # type: ignore
        self._timers = {}  # type: ignore
        self._on_expired = function_on_expired

    def __setitem__(
        self,
        key: Any,
        value: Any,
    ) -> None:
        self._dict[key] = value
        self._set_ttl(key, self._default_ttl)

    def _set_ttl(self, key: Any, ttl: int) -> None:
        """
        Set ttl for key

        :param key: The key for which the TTL (Time To Live) is being set.
        :type key: Any
        :param ttl: The time in seconds after which the key should expire.
        :type ttl: int
        :rtype: None

        """
        if key in self._timers:
            self._timers[key].cancel()
        self._timers[key] = Timer(ttl, self._expire, args=[key])
        self._timers[key].start()

    def extend_ttl(self, key: Any) -> None:
        """
        Attempts to extend the time-to-live (TTL) value for the specified key.

        If the key exists in the internal dictionary, it resets its TTL to the default
         TTL value. If the key does not exist, a KeyError is raised.


        :param key: The key for which the TTL is to be extended.
        :type key: Any
        :raises KeyError: If the key is not found in the internal dictionary.
        :rtype: None

        """
        if key not in self._dict:
            raise KeyError(f"Key {key} not found")
        self._set_ttl(key, self._default_ttl)

    def __getitem__(self, key: Any) -> Any:
        return self._dict[key]

    def __delitem__(self, key: Any) -> None:
        self._cleanup(key, is_expire_cleanup=False)
        del self._dict[key]
        self._timers[key].cancel()
        del self._timers[key]

    def __contains__(self, key: Any) -> bool:
        return key in self._dict

    def _expire(self, key: Any) -> None:
        """
        a method for the timer that will be called when the timer expires

        :param key: The key of the item to expire from the dictionary.
        :type key: Any
        """
        self._cleanup(key, is_expire_cleanup=True)
        del self._dict[key]
        del self._timers[key]

    def _cleanup(self, key: Any, is_expire_cleanup: bool = False) -> None:
        """
        method for cleaning the key

        :param key: The key used to identify the item to be cleaned up.
        :type key: Any
        """
        if is_expire_cleanup and self._on_expired is not None:
            self._on_expired(key)

    def items(self) -> tuple[list[Any], list[Any]]:
        """
        Returns all items in the dictionary.

        :returns: A view object that displays a list of a dictionary's
        :rtype: tuple[list[Any], list[Any]]
        """
        return self._dict.items()  # type: ignore

    def values(self) -> Any:
        """
        Gets the values from the internal dictionary.

        :returns: An object containing all the values in the dictionary.
        :rtype: list[Any]
        """
        return self._dict.values()

    def keys(self) -> Any:
        """
        Returns the keys of the internal dictionary.

        :returns: A view object that displays a list of all the keys.
        :rtype: list[Any]
        """
        return self._dict.keys()

    def __iter__(self) -> Any:
        for i in self._dict.keys():  # noqa:UP028
            yield i

    def __str__(self) -> str:
        return str(dict(self._dict.items()))

    def get(self, key: Any, default: Any = None) -> Any:
        return self._dict.get(key, default)

    def clear(self) -> None:
        self._dict.clear()
        for item in self._timers.values():
            item.cancel()

    def pop(self, key: Any, default: Any | None = None) -> Any | None:
        if key in self._dict:
            self._timers[key].cancel()
            del self._timers[key]
        return self._dict.pop(key=key, default=default)

    def setdefault(self, key: Any, default: Any | None = None) -> Any | None:
        """Insert key with a value of default if key is not in the dictionary.

        Return the value for key if key is in the dictionary, else default.
        """
        if key in self._dict:
            return self._dict[key]
        self._dict[key] = default
        return default

    def __len__(self) -> int:
        return len(self._dict)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TTLDict):
            return dict.__eq__(self._dict, other._dict)
        elif isinstance(other, dict):
            return dict.__eq__(self._dict, other)
        raise TypeError(f"Can't compare TTLDict and {type(other)}")

    def update(self, new_data: TTLDict | dict[Any, Any]) -> None:
        if isinstance(new_data, TTLDict):
            self._dict.update(new_data._dict)
        elif isinstance(new_data, dict):
            self._dict.update(new_data)
        else:
            raise TypeError("Can't update ttl dict")
