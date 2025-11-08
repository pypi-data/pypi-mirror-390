from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar("T")


@dataclass(frozen=True)
class ScalarPoint(Generic[T]):
    timestamp: float
    value: T


@dataclass(frozen=True)
class StringPoint:
    timestamp: float
    value: str


@dataclass(frozen=True)
class InstantSeries(Generic[T]):
    metric: dict[str, str]
    value: ScalarPoint[T]


@dataclass(frozen=True)
class InstantVector(Generic[T]):
    series: list[InstantSeries[T]]


@dataclass(frozen=True)
class RangeSeries(Generic[T]):
    metric: dict[str, str]
    values: list[ScalarPoint[T]]


@dataclass(frozen=True)
class Matrix(Generic[T]):
    series: list[RangeSeries[T]]
