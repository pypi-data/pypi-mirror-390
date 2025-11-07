from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Union, assert_never, cast

from typing_extensions import Unpack, overload

from adsdatahub.restapi.resources import (
    analysis_queries,
    analysis_query,
    operation,
    operations,
)
from adsdatahub.types import TimeoutTypes

if TYPE_CHECKING:
    import adsdatahub.restapi.http

    from .real_client import RealRestApiClientConstructerKwargs


class Client:
    def __new__(
        cls, **kwargs: "Unpack[RealRestApiClientConstructerKwargs]"
    ) -> "Client":
        if cls is Client:
            from .real_client import RealClient

            return RealClient(**kwargs)

        return super().__new__(cls)

    @property
    @abstractmethod
    def _http(self) -> "adsdatahub.restapi.http.Client": ...

    @property
    def timeout(self) -> TimeoutTypes:
        return self._http.timeout

    @timeout.setter
    def timeout(self, value: TimeoutTypes) -> None:
        self._http.timeout = value

    @overload
    def resource(
        self,
        resource_name: analysis_queries.ResourceName,
        **params: Unpack[analysis_queries.PathParameters],
    ) -> analysis_queries.Resource:
        """
        Ads Data Hub 内で実行できる分析クエリを定義します。

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.analysisQueries?hl=ja
        """
        ...

    @overload
    def resource(
        self,
        resource_name: analysis_query.ResourceName,
        **params: Unpack[analysis_query.PathParameters],
    ) -> analysis_query.Resource:
        """
        Ads Data Hub 内で実行できる分析クエリを定義します。

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.analysisQueries?hl=ja
        """
        ...

    @overload
    def resource(
        self,
        resource_name: operations.ResourceName,
        **params: Unpack[operations.PathParameters],
    ) -> operations.Resource:
        """
        このリソースは、ネットワーク API 呼び出しの結果である長時間実行オペレーションを表します。

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/operations?hl=ja
        """
        ...

    @overload
    def resource(
        self,
        resource_name: operation.ResourceName,
        **params: Unpack[operation.PathParameters],
    ) -> operation.Resource:
        """
        このリソースは、ネットワーク API 呼び出しの結果である長時間実行オペレーションを表します。

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/operations?hl=ja
        """
        ...

    def resource(
        self,
        resource_name: Union[
            analysis_queries.ResourceName,
            analysis_query.ResourceName,
            operations.ResourceName,
            operation.ResourceName,
        ],
        **params: Any,
    ) -> Union[
        analysis_queries.Resource,
        analysis_query.Resource,
        operations.Resource,
        operation.Resource,
    ]:
        match resource_name:
            case "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries":
                return analysis_queries.Resource(
                    self._http, cast(analysis_queries.PathParameters, params)
                )

            case "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}":
                return analysis_query.Resource(
                    self._http, cast(analysis_query.PathParameters, params)
                )

            case "https://adsdatahub.googleapis.com/v1/operations":
                return operations.Resource(
                    self._http, cast(operations.PathParameters, params)
                )

            case "https://adsdatahub.googleapis.com/v1/operations/{operation_id}":
                return operation.Resource(
                    self._http, cast(operation.PathParameters, params)
                )

            case _:
                assert_never(resource_name)
