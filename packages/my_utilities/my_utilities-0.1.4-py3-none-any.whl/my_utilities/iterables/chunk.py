"""
Module with functions for generate chunks
"""

# pylint: disable=inconsistent-return-statements
from collections.abc import Generator
from typing import Any

from .split import _validate_type


def chunks(
    iterable: list[Any] | tuple[Any, ...], size_chunk: int
) -> Generator[list[Any] | tuple[Any, ...], None, None]:
    """
    Method for splitting into many parts with len size_chunk generator

    :param iterable: object to split
    :type iterable: Union[List[Any], Tuple[Any, ...]]
    :param size_chunk: size_chunk
    :type size_chunk: int
    :return: generator of split iterable object len generator equal cnt variable
    :rtype: Generator
    :raises TypeError: if incorrect type of `iterable` or `size_chunk` variables
    :raises ValueError: if `size_chunk` variable is not in a valid value
    """
    if not isinstance(size_chunk, int):
        raise TypeError("Incorrect type `size_chunk`")
    if size_chunk < 1:
        raise ValueError("Chunk size must be >= 1")
    _validate_type(iterable=iterable)
    for i in range(0, len(iterable), size_chunk):
        yield iterable[i : i + size_chunk]
