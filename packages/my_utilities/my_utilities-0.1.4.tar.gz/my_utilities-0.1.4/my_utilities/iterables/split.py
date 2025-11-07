"""
Module with functions for split iterable objects
"""

# pylint: disable=inconsistent-return-statements
from collections.abc import Generator, Iterable
from typing import Any


def _validate_type(iterable: list[Any] | tuple[Any, ...]) -> type | None:
    """
    Validate the type of variable iterable

    :param iterable: Iterable type to variable
    :type iterable: Union[List[Any], Tuple[Any, ...]]
    :return: if correct type variable `iterable` than return type
    :rtype: type | None
    :raise TypeError: if incorrect type `iterable`
    """
    if not isinstance(iterable, (list, tuple)):
        raise TypeError(
            f"Incorrect type variable `iterable`."
            f" Valid types are [list, tuple] and not {type(iterable)}"
        )
    return type(iterable)


def split(
    iterable: list[Any] | tuple[Any, ...], cnt: int
) -> Generator[list[Any] | tuple[Any, ...], None, None]:
    """
    Method for splitting into equal cnt parts generator

    :param iterable: object to split
    :type iterable: Union[List[Any], Tuple[Any, ...]]
    :param cnt: cnt partitions
    :type cnt: int
    :return: generator of split iterable object len generator equal cnt variable
    :rtype: Generator
    :raises TypeError: if incorrect type of `iterable` variable
    """
    _validate_type(iterable=iterable)
    k, j = divmod(len(iterable), cnt)  # type: int, int
    for i in range(cnt):
        yield iterable[i * k + min(i, j) : (i + 1) * k + min(i + 1, j)]


def split_as_iterable(
    iterable: list[Any] | tuple[Any, ...], cnt: int
) -> list[list[Any] | list[tuple[Any, ...]]]:  # type: ignore
    """
    Method for splitting into equal parts

    :param iterable: object to split
    :type iterable: Union[List[Any], Tuple[Any, ...]]
    :param cnt: cnt partitions
    :type cnt: int
    :return: iterable object with partitions
    :rtype: Union[List[Any], Tuple[Any, ...]]
    :raises TypeError: if incorrect type of `iterable` variable
    """
    _current_type = _validate_type(iterable)  # type: type
    return _current_type(split(iterable=iterable, cnt=cnt))  # type: ignore


def split_with_overlap(
    data: list[Any] | tuple[Any, ...], n_parts: int = 10, overlap: int = 0
) -> Generator[list[Any] | tuple[Any, ...], None, None]:
    """
    Split a sequence into several overlapping parts.

    This function divides the input sequence into `n_parts` approximately equal
    chunks, with a specified number of overlapping elements between consecutive parts.
    The overlap ensures smooth transitions between parts, which can be useful for
    signal processing, data batching, or sliding window operations.

    :param data: The input iterable (e.g., list or tuple) to split.
    :type data: list[Any] | tuple[Any, ...]
    :param n_parts: The number of parts to split the data into.
    :type n_parts: int
    :param overlap: The number of elements each part should overlap with the next.
    :type overlap: int
    :return: A generator yielding slices of `data`, each with the specified overlap.
    :rtype: Generator[list[Any], None, None]
    :raises ValueError: If `n_parts` is less than 1 or greater than the length of `data`.
    :raises TypeError: If `data` is not a list or tuple.

    >>> list_ = [i for i in range(100)]
    >>> for i in split_with_overlap(list_, 10,3):
    >>>     print(i)
    >>> # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    >>> # [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    >>> # [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
    >>> # [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42]
    >>> # [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52]
    >>> # [47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62]
    >>> # [57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]
    >>> # [67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82]
    >>> # [77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92]
    >>> # [87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]"""
    length = len(data)
    base_size = length // n_parts

    for i in range(n_parts):
        start = max(0, i * base_size - overlap)
        end = min(length, (i + 1) * base_size + overlap)
        yield data[start:end]
