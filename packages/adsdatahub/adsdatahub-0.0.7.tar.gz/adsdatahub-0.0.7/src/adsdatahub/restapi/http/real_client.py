import typing

import httpx
from httpx._types import (
    HeaderTypes,
    URLTypes,
)
from typing_extensions import override

from adsdatahub._helpers import (
    GenericResponseBody,
    parse_response_body,
    validate_status_code,
)
from adsdatahub.restapi.http.client import Client, HttpRequestKwargs
from adsdatahub.types import TimeoutTypes


class RealClient(Client):
    def __init__(
        self, headers: typing.Optional[HeaderTypes] = None, timeout: TimeoutTypes = None
    ):
        self._client = httpx.Client(headers=headers, timeout=timeout)

    @property
    @override
    def timeout(self) -> TimeoutTypes:
        return self._client.timeout

    @timeout.setter
    @override
    def timeout(self, value: TimeoutTypes) -> None:
        self._client.timeout = value

    @typing.overload
    def request(
        self,
        method: str,
        url: URLTypes,
        response_body_type: type[GenericResponseBody],
        **kwargs: typing.Unpack[HttpRequestKwargs],
    ) -> GenericResponseBody: ...

    @typing.overload
    def request(
        self,
        method: str,
        url: URLTypes,
        response_body_type: None = None,
        **kwargs: typing.Unpack[HttpRequestKwargs],
    ) -> None: ...

    @override
    def request(
        self,
        method: str,
        url: URLTypes,
        response_body_type: typing.Optional[type[GenericResponseBody]] = None,
        **kwargs: typing.Unpack[HttpRequestKwargs],
    ) -> typing.Optional[GenericResponseBody]:
        response = self._client.request(method, url, **kwargs)

        if response_body_type is None:
            validate_status_code(response)

        else:
            return parse_response_body(
                response_body_type,
                response,
            )
