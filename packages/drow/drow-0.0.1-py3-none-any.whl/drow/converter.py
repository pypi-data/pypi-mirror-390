from decimal import Decimal
from typing import TypeVar
from collections.abc import Callable

T = TypeVar("T")
Converter = Callable[[str], T]


def no_op(value: T) -> T:
    return value


def convert_to_float(value: str) -> float:
    return float(value)


def convert_to_decimal(value: str) -> Decimal:
    return Decimal(value)
