import typing
from types import NoneType

from typing_extensions import override

from adsdatahub._helpers import (
    GenericResponseBody,
)
from adsdatahub.exceptions import (
    AdsDataHubMockDataTypeError,
    AdsDataHubMockStoreDataEmptyError,
    AdsDataHubMockStoreKeyError,
)
from adsdatahub.restapi.http.client import HttpRequestKwargs
from adsdatahub.restapi.schemas._model import Model
from adsdatahub.types import TimeoutTypes, URLTypes

from .client import Client


class StoreKey(typing.NamedTuple):
    method: str
    url: URLTypes


_StoreData = list[tuple[StoreKey, Model | None | Exception]]


class MockClient(Client):
    _store: _StoreData

    __slots__ = ("_store",)

    @property
    def store(self) -> _StoreData:
        if not hasattr(self, "_store"):
            self._store = []

        return self._store

    @property
    @override
    def timeout(self) -> TimeoutTypes:
        return 0

    @timeout.setter
    @override
    def timeout(self, value: TimeoutTypes) -> None:
        pass

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
        if len(self.store) == 0:
            raise AdsDataHubMockStoreDataEmptyError()
        expected_key = StoreKey(method, url)
        key, response = self.store.pop(0)

        if key != expected_key:
            raise AdsDataHubMockStoreKeyError(key, expected_key)

        if isinstance(response, Exception):
            raise response

        if response_body_type is None:
            if response is not None:
                raise AdsDataHubMockDataTypeError(response.__class__, NoneType)

        elif not isinstance(response, response_body_type):
            raise AdsDataHubMockDataTypeError(response.__class__, response_body_type)

        else:
            return response

    def inject_response(
        self,
        method: str,
        url: URLTypes,
        response: Model | None | Exception,
    ) -> "MockClient":
        self.store.append((StoreKey(method, url), response))

        return self
