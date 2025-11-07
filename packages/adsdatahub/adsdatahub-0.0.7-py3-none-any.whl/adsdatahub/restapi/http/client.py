import typing
from abc import ABCMeta, abstractmethod

from httpx._client import UseClientDefault
from httpx._types import (
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestExtensions,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
)

from adsdatahub._helpers import GenericResponseBody


class HttpRequestKwargs(typing.TypedDict):
    content: typing.NotRequired[typing.Optional[RequestContent]]
    data: typing.NotRequired[typing.Optional[RequestData]]
    files: typing.NotRequired[typing.Optional[RequestFiles]]
    json: typing.NotRequired[typing.Optional[typing.Any]]
    params: typing.NotRequired[typing.Optional[QueryParamTypes]]
    headers: typing.NotRequired[typing.Optional[HeaderTypes]]
    cookies: typing.NotRequired[typing.Optional[CookieTypes]]
    auth: typing.NotRequired[typing.Union[AuthTypes, UseClientDefault, None]]
    follow_redirects: typing.NotRequired[typing.Union[bool, UseClientDefault]]
    timeout: typing.NotRequired[typing.Union[TimeoutTypes, UseClientDefault]]
    extensions: typing.NotRequired[typing.Optional[RequestExtensions]]


class Client(metaclass=ABCMeta):
    @property
    @abstractmethod
    def timeout(self) -> TimeoutTypes: ...

    @timeout.setter
    @abstractmethod
    def timeout(self, value: TimeoutTypes) -> None: ...

    @typing.overload
    @abstractmethod
    def request(
        self,
        method: str,
        url: URLTypes,
        response_body_type: type[GenericResponseBody],
        **kwargs: typing.Unpack[HttpRequestKwargs],
    ) -> GenericResponseBody: ...

    @typing.overload
    @abstractmethod
    def request(
        self,
        method: str,
        url: URLTypes,
        response_body_type: None = None,
        **kwargs: typing.Unpack[HttpRequestKwargs],
    ) -> None: ...

    @abstractmethod
    def request(
        self,
        method: str,
        url: URLTypes,
        response_body_type: typing.Optional[type[GenericResponseBody]] = None,
        **kwargs: typing.Unpack[HttpRequestKwargs],
    ) -> typing.Optional[GenericResponseBody]: ...
