from typing import Any, Union, Unpack, assert_never, overload

from typing_extensions import override

from adsdatahub.restapi import http
from adsdatahub.restapi.client import Client
from adsdatahub.restapi.resources import (
    analysis_queries,
    analysis_query,
    operation,
    operations,
)


class MockClient(Client):
    def __init__(self, **kwargs: Any) -> None:
        self._http_internal = http.MockClient()

    @property
    @override
    def _http(self) -> http.MockClient:
        return self._http_internal

    @overload
    def inject_response(
        self,
        resource_name: analysis_queries.ResourceName,
        **params: Unpack[analysis_queries.PathParameters],
    ) -> analysis_queries.MockResource: ...

    @overload
    def inject_response(
        self,
        resource_name: analysis_query.ResourceName,
        **params: Unpack[analysis_query.PathParameters],
    ) -> analysis_query.MockResource: ...

    @overload
    def inject_response(
        self,
        resource_name: operations.ResourceName,
        **params: Unpack[operations.PathParameters],
    ) -> operations.MockResource: ...

    @overload
    def inject_response(
        self,
        resource_name: operation.ResourceName,
        **params: Unpack[operation.PathParameters],
    ) -> operation.MockResource: ...

    def inject_response(
        self,
        resource_name: Union[
            analysis_queries.ResourceName,
            analysis_query.ResourceName,
            operations.ResourceName,
            operation.ResourceName,
        ],
        **params: Any,
    ) -> Union[
        analysis_queries.MockResource,
        analysis_query.MockResource,
        operations.MockResource,
        operation.MockResource,
    ]:
        match resource_name:
            case analysis_queries.RESOURCE_NAME:
                return analysis_queries.MockResource(self, **params)

            case analysis_query.RESOURCE_NAME:
                return analysis_query.MockResource(self, **params)

            case operations.RESOURCE_NAME:
                return operations.MockResource(self, **params)

            case operation.RESOURCE_NAME:
                return operation.MockResource(self, **params)

            case _ as unreachable:
                assert_never(unreachable)
