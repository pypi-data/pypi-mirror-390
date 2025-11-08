from typing import TypeVar, TypedDict, NotRequired, Generic, Literal

DataType = TypeVar("DataType")


class BaseResponse(TypedDict):
    warnings: NotRequired[list[str]]
    infos: NotRequired[list[str]]


class SuccessResponse(BaseResponse, Generic[DataType]):
    status: Literal["success"]
    data: DataType


class ErrorResponse(BaseResponse):
    status: Literal["error"]
    errorType: str
    error: str


# 0: int: boundary_rule
# 1: str: left_boundary
# 2: str: right_boundary
# 3: str: count_in_bucket
BucketValue = tuple[int, str, str, str]


class HistogramValue(TypedDict):
    count: str
    sum: str
    buckets: list[BucketValue]


ScalarPointData = tuple[float, str]
StringPointData = tuple[float, str]
HistogramPointData = tuple[float, HistogramValue]


class BaseVector(TypedDict):
    metric: dict[str, str]


class ScalarInstantVector(BaseVector):
    value: ScalarPointData


class HistogramInstantVector(BaseVector):
    histogram: HistogramPointData


class ScalarRangeVector(BaseVector):
    values: list[ScalarPointData]


class HistogramRangeVector(BaseVector):
    histograms: list[HistogramPointData]


class VectorData(TypedDict):
    resultType: Literal["vector"]
    result: list[ScalarInstantVector]


class MatrixData(TypedDict):
    resultType: Literal["matrix"]
    result: list[ScalarRangeVector]


class ScalarData(TypedDict):
    resultType: Literal["scalar"]
    result: ScalarPointData


class StringData(TypedDict):
    resultType: Literal["string"]
    result: StringPointData
