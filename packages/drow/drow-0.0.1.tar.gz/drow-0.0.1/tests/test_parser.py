from unittest import TestCase

from drow.annotation import (
    SuccessResponse, ErrorResponse,
    VectorData, MatrixData, ScalarData, StringData,
)
from drow.model import (
    ScalarPoint, StringPoint,
    InstantVector, Matrix,
)
from drow.parser import (
    PrometheusError,
    ParseError,
    make_parser,
)
from drow.converter import no_op

parser = make_parser(no_op)


class TestParser(TestCase):
    def test_success_vector(self) -> None:
        resp: SuccessResponse[VectorData] = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {
                            "job": "foo",
                        },
                        "value": (1435781451.781, "1"),
                    },
                    {
                        "metric": {
                            "job": "bar",
                        },
                        "value": (1435781451.781, "0"),
                    },
                ],
            },
        }
        parsed = parser.parse_query_response(resp)
        assert isinstance(parsed, InstantVector)
        self.assertEqual(len(parsed.series), 2)

        s0 = parsed.series[0]
        self.assertEqual(s0.metric["job"], "foo")
        self.assertEqual(s0.value.value, "1")

        s1 = parsed.series[1]
        self.assertEqual(s1.metric["job"], "bar")
        self.assertEqual(s1.value.value, "0")

    def test_success_matrix(self) -> None:
        resp: SuccessResponse[MatrixData] = {
            "status": "success",
            "data": {
                "resultType": "matrix",
                "result": [
                    {
                        "metric": {
                            "job": "foo",
                        },
                        "values": [
                            (1435781430.781, "1"),
                            (1435781445.781, "2"),
                            (1435781460.781, "3"),
                        ],
                    },
                    {
                        "metric": {
                            "job": "bar",
                        },
                        "values": [
                            (1435781430.781, "2"),
                            (1435781445.781, "1"),
                            (1435781460.781, "0"),
                        ],
                    },
                ],
            },
        }
        parsed = parser.parse_query_range_response(resp)
        assert isinstance(parsed, Matrix)
        self.assertEqual(len(parsed.series), 2)

        s0 = parsed.series[0]
        self.assertEqual(s0.metric["job"], "foo")
        self.assertEqual(s0.values[0].value, "1")
        self.assertEqual(s0.values[1].value, "2")
        self.assertEqual(s0.values[2].value, "3")

        s1 = parsed.series[1]
        self.assertEqual(s1.metric["job"], "bar")
        self.assertEqual(s1.values[0].value, "2")
        self.assertEqual(s1.values[1].value, "1")
        self.assertEqual(s1.values[2].value, "0")

    def test_success_scalar(self) -> None:
        resp: SuccessResponse[ScalarData] = {
            "status": "success",
            "data": {"resultType": "scalar", "result": (1739529069.829, "5")},
        }
        parsed = parser.parse_query_response(resp)
        assert isinstance(parsed, ScalarPoint)
        self.assertEqual(parsed.value, "5")

    def test_success_string(self) -> None:
        resp: SuccessResponse[StringData] = {
            "status": "success",
            "data": {
                "resultType": "string", "result": (1739529105.401, "foo")
            },
        }
        parsed = parser.parse_query_response(resp)
        assert isinstance(parsed, StringPoint)
        self.assertEqual(parsed.value, "foo")

    def test_error(self) -> None:
        resp: ErrorResponse = {
            "status": "error",
            "errorType": "422",
            "error": "error when executing query",
        }

        with self.assertRaises(PrometheusError):
            parser.parse_query_response(resp)

    def test_scalar_value(self) -> None:
        resp: SuccessResponse[ScalarData] = {
            "status": "success",
            "data": {"resultType": "scalar", "result": (1739529069.829, "5")},
        }
        self.assertEqual(parser.parse_query_value_response(resp), "5")

    def test_vector_value(self) -> None:
        resp: SuccessResponse[VectorData] = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {
                            "job": "foo",
                        },
                        "value": (1435781451.781, "6"),
                    },
                ],
            },
        }
        self.assertEqual(parser.parse_query_value_response(resp), "6")

    def test_too_many_series_when_parse_value(self) -> None:
        resp: SuccessResponse[VectorData] = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {
                            "job": "foo",
                        },
                        "value": (1435781451.781, "1"),
                    },
                    {
                        "metric": {
                            "job": "bar",
                        },
                        "value": (1435781451.781, "0"),
                    },
                ],
            },
        }
        with self.assertRaises(ParseError):
            parser.parse_query_value_response(resp)
