import json
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

import httpx
from typing_extensions import override

from adsdatahub.types import OperationId

if TYPE_CHECKING:
    from adsdatahub.restapi.http.mock_client import StoreKey


class AdsDataHubException(Exception):
    """Base exception for adsdatahub."""

    @property
    @abstractmethod
    def message(self) -> str:
        """Return the exception message."""
        ...

    def __str__(self) -> str:
        return self.message


class AdsDataHubError(AdsDataHubException):
    """Base error for adsdatahub."""


class AdsDataHubResponseError(AdsDataHubError):
    pass


class AdsDataHubResponseStatusCodeError(AdsDataHubResponseError):
    """Response status code error for adsdatahub."""

    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        if response.headers.get("content-type") == "application/json":
            self.response_body = response.json()
        else:
            self.response_body = response.content.decode("utf-8")

    @property
    @override
    def message(self) -> str:
        return f"Response Status Code Error {self.response}: {self.response_body}"


class AdsDataHubUnimplementedError(AdsDataHubResponseStatusCodeError):
    """
    このメソッドがサーバーでサポートされていないため、google.rpc.Code.UNIMPLEMENTED を返した場合のエラー。

    See: https://developers.google.com/ads-data-hub/reference/rest/v1/operations/delete?hl=ja
    """

    def __init__(self, response: httpx.Response) -> None:
        super().__init__(response)


class AdsDataHubUnavailableError(AdsDataHubResponseStatusCodeError):
    """
    このメソッドがサーバーで利用できないため、google.rpc.Code.UNAVAILABLE を返した場合のエラー。

    See: https://developers.google.com/ads-data-hub/reference/rest/v1/operations/delete?hl=ja
    """

    def __init__(self, response: httpx.Response) -> None:
        super().__init__(response)


class AdsDataHubResponseBodyHasError(AdsDataHubResponseError):
    def __init__(self, response: httpx.Response, error: dict[str, Any]) -> None:
        self.response = response
        self.error = error

    @property
    @override
    def message(self) -> str:
        return f"ResponseBody has error: {json.dumps(self.error, ensure_ascii=False)}"


class AdsDataHubMockError(AdsDataHubError):
    pass


class AdsDataHubMockMethodError(AdsDataHubMockError, ValueError):
    """Mock method error for adsdatahub."""

    def __init__(self, method: str, expected_method: str) -> None:
        self.method = method
        self.expected_method = expected_method

    @property
    @override
    def message(self) -> str:
        return f"Mock Method Error {self.method}: expected {self.expected_method}"


class AdsDataHubMockDataTypeError(AdsDataHubMockError, TypeError):
    """Mock data type error for adsdatahub."""

    def __init__(self, response_type: type, expected_type: type) -> None:
        self.response_type = response_type
        self.expected_type = expected_type

    @property
    @override
    def message(self) -> str:
        return f"Mock Data Type Error {self.response_type.__name__}: expected {self.expected_type.__name__}"


class AdsDataHubMockStoreDataEmptyError(AdsDataHubMockError, ValueError):
    @property
    @override
    def message(self) -> str:
        return "Mock Store Data is empty"


class AdsDataHubMockStoreKeyError(AdsDataHubMockError, ValueError):
    def __init__(self, key: "StoreKey", expected_key: "StoreKey") -> None:
        self.key = key
        self.expected_key = expected_key

    @property
    @override
    def message(self) -> str:
        return f"Mock Store Key Error {self.key}: expected {self.expected_key}"


class AdsDataHubDestinationTableInfoNotFound(AdsDataHubError, ValueError):
    def __init__(self, operation_id: OperationId) -> None:
        self.operation_id = operation_id

    @property
    @override
    def message(self) -> str:
        return f"Destination Table Info Not Found: operation_id={self.operation_id}"
