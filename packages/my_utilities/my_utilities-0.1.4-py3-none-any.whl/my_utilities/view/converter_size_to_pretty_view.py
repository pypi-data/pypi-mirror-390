"""
Module with function for convert bytes size to correct size in kb/mb/gb
"""

# pylint: disable=super-with-arguments
from __future__ import annotations

from enum import StrEnum
import math
from numbers import Number
from typing import Any

from pydantic import BaseModel, Field


class SystemTypes(StrEnum):
    """
    Enum of available conversion systems
    """

    SI = "si_name"
    IEC = "iec_name"
    VERBOSE = "verbose_name"
    ALTERNATIVE = "alternative_name"
    TRADITIONAL = "traditional_name"


class SystemValue(BaseModel):
    """
    Class for storing information about different weights
    """

    pow: int = Field(
        ...,
        description="the power to which you need to raise the bytes "
        "for the correct calculation",
    )
    traditional_name: str = Field(..., description="Traditional name for this type")
    alternative_name: str | tuple[str, str] = Field(
        ..., description="Alternative name for this type"
    )
    verbose_name: tuple[str, str] = Field(
        ..., description="Full name without abbreviations"
    )
    iec_name: str = Field(..., description="IEC system name")
    si_name: str = Field(None, description="Si system name")

    value_base: int = Field(
        None, description="The number of bytes in one unit of this type"
    )
    value_si: int = Field(
        None, description="The number of bytes in one unit of this type in system si"
    )

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.value_base = 1024**self.pow
        self.value_si = 1000**self.pow
        if not self.si_name:
            self.si_name = self.traditional_name

    def get_size_suffix(
        self, system: str = "traditional"
    ) -> str | tuple[str, str] | None:
        """
        method return str title for chose type
        :param system: title system for view
         allowed: [si, iec, verbose, alternative, traditional]
        :type system: str
        :return: names for chose system
        :rtype: str | tuple[str, str]
        :raise ValueError: if there is no selected system
        """
        system = system.upper()
        try:
            name_key = SystemTypes[system].value
            return self.__getattribute__(name_key)  # type: ignore
        except KeyError:
            raise ValueError(
                f"Incorrect name system."
                f" Allowed names: {[i.name for i in SystemTypes]}"
            ) from BaseException

    def get_amount(
        self,
        bytes_value: int,
        round_to: int = 2,
        is_si: bool = False,
    ) -> float:
        """
        Method get size of bytes value in system

        :param bytes_value:  bytes to convert
        :type bytes_value: int
        :param round_to: decimal point rounding precision
        :type round_to:  int
        :param is_si: is to 'si' system convert
        :type is_si: bool
        :return:
        """
        if is_si:
            val = self.value_si
        else:
            val = self.value_base
        return round(bytes_value / val, round_to)

    def get_normalized_size(
        self,
        bytes_value: int,
        system: str | None = "traditional",
        round_to: int | None = 2,
    ) -> str:
        """
        Method convert bytes value in chose system
        :param bytes_value: bytes value to convert
        :type bytes_value: int
        :param system: system to which to convert
        :type system: str
        :param round_to:
        :type round_to: decimal point rounding precision
        :return: converted value
        :rtype: str
        :raise ValueError: if incorrect system name
        """
        system = system.upper()
        is_si = system == "SI"
        amount = self.get_amount(
            bytes_value=bytes_value, round_to=round_to, is_si=is_si
        )
        suffix_names = self.get_size_suffix(system=system)

        if isinstance(suffix_names, tuple):
            singular, multiple = suffix_names
            if amount == 1.0:
                suffix_amount = singular
            else:
                suffix_amount = multiple
        else:
            suffix_amount = suffix_names
        frac, whole = math.modf(amount)
        if frac == 0.0:
            amount = int(whole)
        return f"{amount}{suffix_amount}"

    def __lt__(self, other: Number | SystemValue) -> bool:
        if isinstance(other, SystemValue):
            result = self.value_base < other.value_base
        elif isinstance(other, Number):
            result = self.value_base < other  # type: ignore
        else:
            raise TypeError("incorrect value to compare")
        return result

    def __le__(self, other: Number | SystemValue) -> bool:
        return self < other or self == other

    def __gt__(self, other: Number | SystemValue) -> bool:
        result: bool = False
        if isinstance(other, SystemValue):
            result = self.value_base > other.value_base
        elif isinstance(other, Number):
            result = self.value_base > other  # type: ignore
        else:
            raise TypeError("incorrect value type to compare")
        return result

    def __eq__(self, other: Number | SystemValue) -> bool:  # type: ignore
        result: bool = False
        if isinstance(other, SystemValue):
            result = super().__eq__(other)
        elif isinstance(other, Number):
            result = self.value_base == other
        else:
            raise TypeError("incorrect value type to compare")
        return result

    def __ge__(self, other: Number | SystemValue) -> bool:
        return self > other or self == other


LIST_SYSTEMS = [
    SystemValue(
        pow=5,
        traditional_name="P",
        alternative_name="PB",
        verbose_name=(" petabyte", " petabytes"),
        iec_name="Pi",
    ),
    SystemValue(
        pow=4,
        traditional_name="T",
        alternative_name="TB",
        verbose_name=(" terabyte", " terabytes"),
        iec_name="Ti",
    ),
    SystemValue(
        pow=3,
        traditional_name="G",
        alternative_name="GB",
        verbose_name=(" gigabyte", " gigabytes"),
        iec_name="Gi",
    ),
    SystemValue(
        pow=2,
        traditional_name="M",
        alternative_name="MB",
        verbose_name=(" megabyte", " megabytes"),
        iec_name="Mi",
    ),
    SystemValue(
        pow=1,
        traditional_name="K",
        alternative_name="KB",
        verbose_name=(" kilobyte", " kilobytes"),
        iec_name="Ki",
    ),
    SystemValue(
        pow=0,
        traditional_name="B",
        alternative_name=(" byte", " bytes"),
        verbose_name=(" byte", " bytes"),
        iec_name="",
    ),
]


def size(
    bytes_value: int, system: str | None = "traditional", round_to: int = 2
) -> str:
    """
    Method for print size of file from bytes to pretty print
    :param bytes_value: bytes to convert
    :type bytes_value:
    :param system:
    :type system:
    :param round_to: decimal point rounding precision
    :type round_to: int
    :return: converted bytes_value to pretty string
    :rtype: str
    :raise ValueError: if incorrect system name or round_to is less 0
    :raise TypeError: if incorrect type round_to

    :example:
    Using the traditional system, where a factor of 1024 is used::

    >>> size(10)
    '10B'
    >>> size(2000)
    '1.95K'
    >>> size(20000)
    '19.53K'
    >>> size(200000)
    '0.19M'
    >>> size(1000000)
    '0.95M'
    >>> size(2000000)
    '1.91M'
    # use si
    >>> size(10, system="si")
    '10B'
    >>> size(2000, system="si")
    '2K'
    >>> size(20000, system="si")
    '20K'
    >>> size(200000, system="si")
    '0.2M'
    >>> size(1000000, system="si")
    '1M'
    >>> size(2000000, system="si")
    '2M'
    """
    if not isinstance(round_to, int):
        raise TypeError()
    if round_to < 1:
        raise ValueError()
    if not system:
        system = "traditional"
    system = system.upper()
    if system not in [i.name for i in SystemTypes]:
        raise ValueError(
            f"Incorrect system name - `{system}`."
            f" Allowed systems {[i.name for i in SystemTypes]}"
        )
    factor = None  # type: SystemValue|None
    for _factor in LIST_SYSTEMS:  # pragma: no cover
        if bytes_value >= _factor.value_base / 10:
            factor = _factor
            break

    return factor.get_normalized_size(
        bytes_value=bytes_value, system=system, round_to=round_to
    )
