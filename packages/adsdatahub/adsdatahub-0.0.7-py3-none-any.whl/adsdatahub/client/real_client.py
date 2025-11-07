from typing import Unpack, cast

from google.cloud import bigquery
from typing_extensions import override

import adsdatahub.restapi
from adsdatahub.client.client import Client
from adsdatahub.restapi.real_client import RealRestApiClientConstructerKwargs
from adsdatahub.types import CustomerId


class RealClient(Client):
    def __init__(
        self,
        restapi_client: adsdatahub.restapi.RealClient | None = None,
        bigquery_client: bigquery.Client | None = None,
        **kwargs: Unpack[RealRestApiClientConstructerKwargs],
    ) -> None:
        if not restapi_client:
            restapi_client = cast(
                adsdatahub.restapi.RealClient,
                adsdatahub.restapi.RealClient(**kwargs),
            )

        if not bigquery_client:
            bigquery_client = bigquery.Client(**kwargs)  # type: ignore[arg-type]

        self.restapi = restapi_client
        self.bigquery_client = bigquery_client

    @override
    def customer(self, customer_id: CustomerId):
        from adsdatahub.client.customer.real_customer import RealCustomerClient

        return RealCustomerClient(self, customer_id)
