from decimal import Decimal
from unittest import TestCase

from drow.annotation import SuccessResponse, VectorData
from drow.model import InstantVector
from drow.parser import make_parser
from drow.converter import convert_to_decimal


class TestConverter(TestCase):
    def test_convert_to_decimal(self) -> None:
        resp: SuccessResponse[VectorData] = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {
                            "job": "foo",
                        },
                        "value": (1435781451.781, "1.23456789"),
                    },
                ],
            },
        }
        parser = make_parser(convert_to_decimal)
        parsed = parser.parse_query_response(resp)
        assert isinstance(parsed, InstantVector)
        value = parsed.series[0].value.value

        assert isinstance(value, Decimal)
        self.assertEqual(value, Decimal("1.23456789"))
