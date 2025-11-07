from abc import abstractmethod
from typing import TYPE_CHECKING, Unpack

from google.cloud import bigquery

import adsdatahub.restapi
from adsdatahub.restapi.real_client import RealRestApiClientConstructerKwargs
from adsdatahub.types import CustomerId

if TYPE_CHECKING:
    from adsdatahub.client.customer.customer import CustomerClient


class Client:
    def __new__(
        cls,
        restapi_client: adsdatahub.restapi.Client | None = None,
        bigquery_client: bigquery.Client | None = None,
        **kwargs: Unpack[RealRestApiClientConstructerKwargs],
    ) -> "Client":
        if cls is Client:
            from .real_client import RealClient

            return RealClient(restapi_client, bigquery_client, **kwargs)

        return super().__new__(cls)

    @abstractmethod
    def customer(self, customer_id: CustomerId, /) -> "CustomerClient":
        """
        クエリを実行するためのクライアントを生成する。
        """

        raise NotImplementedError
