from typing import Union, TypeVar, Generic

from .annotation import (
    SuccessResponse, ErrorResponse,
    ScalarInstantVector, ScalarRangeVector,
    ScalarPointData,
    VectorData, MatrixData, ScalarData, StringData,
)
from .model import (
    ScalarPoint, StringPoint,
    InstantSeries, RangeSeries,
    InstantVector, Matrix,
)
from .converter import Converter

T = TypeVar("T")
ValueType = TypeVar("ValueType")
ResponseType = TypeVar("ResponseType")
ResultType = TypeVar("ResultType")

QueryResponse = Union[
    SuccessResponse[ScalarData],
    SuccessResponse[StringData],
    SuccessResponse[VectorData],
    ErrorResponse,
]
type QueryResult[T] = Union[
    ScalarPoint[T], StringPoint, InstantVector[T],
]
QueryRangeResponse = Union[
    SuccessResponse[MatrixData],
    ErrorResponse,
]
QueryRangeResult = Matrix


class PrometheusError(Exception):
    pass


class ParseError(Exception):
    pass


class BaseParser(Generic[T]):
    def parse_value(self, value: str) -> T:
        raise NotImplementedError

    def parse_query_response(self, resp: QueryResponse) -> QueryResult[T]:
        if resp["status"] == "error":
            self.parse_error(resp)

        assert resp["status"] == "success", resp

        data = resp["data"]

        if data["resultType"] == "string":
            return self.parse_string(data)

        if data["resultType"] == "scalar":
            return self.parse_scalar(data)

        if data["resultType"] == "vector":
            return self.parse_vector(data)

        raise ParseError(f'unknown result type: {data["resultType"]}')

    def parse_error(self, resp: ErrorResponse) -> None:
        raise PrometheusError(
            f'error {resp["errorType"]}: {resp["error"]}'
        )

    def parse_instant_series(
        self, data: ScalarInstantVector,
    ) -> InstantSeries[T]:
        return InstantSeries(
            metric=data["metric"],
            value=self.parse_scalar_point(data["value"]),
        )

    def parse_range_series(self, data: ScalarRangeVector) -> RangeSeries[T]:
        return RangeSeries(
            metric=data["metric"],
            values=[self.parse_scalar_point(i) for i in data["values"]]
        )

    def parse_query_range_response(
        self, resp: QueryRangeResponse,
    ) -> QueryRangeResult[T]:
        if resp["status"] == "error":
            self.parse_error(resp)

        assert resp["status"] == "success", resp

        data = resp["data"]
        assert data["resultType"] == "matrix", resp

        return self.parse_matrix(data)

    def parse_vector(self, data: VectorData) -> InstantVector[T]:
        return InstantVector(series=[
            self.parse_instant_series(i) for i in data["result"]
        ])

    def parse_matrix(self, data: MatrixData) -> Matrix[T]:
        return Matrix(series=[
            self.parse_range_series(i) for i in data["result"]
        ])

    def parse_scalar(self, data: ScalarData) -> ScalarPoint[T]:
        return self.parse_scalar_point(data["result"])

    def parse_scalar_point(self, data: ScalarPointData) -> ScalarPoint[T]:
        t, v = data
        return ScalarPoint(t, self.parse_value(v))

    def parse_string(self, data: StringData) -> StringPoint:
        return StringPoint(*data["result"])

    def parse_query_value_response(self, resp: QueryResponse) -> T:
        if resp["status"] == "error":
            self.parse_error(resp)

        assert resp["status"] == "success", resp

        data = resp["data"]

        if data["resultType"] == "string":
            return self.parse_value(data["result"][1])

        if data["resultType"] == "scalar":
            return self.parse_value(data["result"][1])

        if data["resultType"] == "vector":
            series_count = len(data["result"])
            if series_count != 1:
                raise ParseError(f"series count incorrect: {series_count}")

            return self.parse_value(data["result"][0]["value"][1])

        raise ParseError(f'unknown result type: {data["resultType"]}')


def make_parser(
    value_converter: Converter[ValueType],
) -> BaseParser[ValueType]:
    class Parser(BaseParser[ValueType]):
        def parse_value(self, value: str) -> ValueType:
            return value_converter(value)

    return Parser()
