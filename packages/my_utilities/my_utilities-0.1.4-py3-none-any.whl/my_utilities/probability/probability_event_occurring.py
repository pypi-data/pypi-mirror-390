"""
The module contains a function that returns whether an event has occurred
 that has a probability of occurrence
"""

from decimal import Decimal
from math import floor
from random import uniform


def is_fate_in_awe(drop_chance: float | int | Decimal) -> bool:
    """
    Method determines whether an event has occurred that
     has a certain chance of falling out
    :param drop_chance: the probability of an event occurring
     value between[0, 1]
    :type drop_chance:  float| int| Decimal
    :return: is got this chance
    :rtype: bool
    :raises ValueError: if the value is not in the allowed range [0, 1]
    :raises TypeError: if incorrect types
    """
    value_to_compare = 1
    if not isinstance(drop_chance, (float, Decimal, int)):
        raise TypeError
    if not 0 <= drop_chance <= 1:
        raise ValueError(
            "Invalid variable value `drop_chance` value must be in between [0, 1]"
        )
    if drop_chance > 0.5:
        # for correct calculation
        value_to_compare = 0
    return floor(uniform(0, 1 / float(drop_chance))) == value_to_compare
