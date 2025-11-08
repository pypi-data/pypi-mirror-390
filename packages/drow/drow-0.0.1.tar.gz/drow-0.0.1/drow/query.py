from urllib.parse import urljoin
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestArg:
    url: str
    params: dict[str, str]


def build_arg_for_query(
    base_url: str, metric: str, time: Optional[float] = None
) -> RequestArg:
    url = urljoin(base_url, "api/v1/query")
    params = {"query": metric}
    if time:
        params["time"] = str(time)

    return RequestArg(url, params)


def build_arg_for_query_range(
    base_url: str, metric: str,
    start: float, end: float,
    step: Optional[float] = None, step_count: int = 60,
) -> RequestArg:
    url = urljoin(base_url, "api/v1/query_range")

    if step is None:
        if start >= end:
            raise ValueError("end must be greater than start")

        step = (end - start) / step_count
        if step < 1:
            step = 1
        else:
            step = int(step)

    params: dict[str, str] = {
        "query": metric,
        "start": str(start),
        "end": str(end),
        "step": str(step),
    }
    return RequestArg(url, params)
