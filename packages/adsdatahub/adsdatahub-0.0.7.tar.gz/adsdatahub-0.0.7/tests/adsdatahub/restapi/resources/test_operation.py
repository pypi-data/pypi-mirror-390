import asyncio
from typing import Callable

import adsdatahub.restapi
import adsdatahub.restapi.resources.operation
import pytest
from adsdatahub._helpers import get_extra_fields
from adsdatahub.exceptions import (
    AdsDataHubResponseStatusCodeError,
    AdsDataHubUnimplementedError,
)
from adsdatahub.restapi.resources import operation
from adsdatahub.restapi.schemas.analysis_query_metadata import (
    AnalysisQueryMetadataModel,
)
from adsdatahub.restapi.schemas.operation import OperationModel
from adsdatahub.types import CustomerId

from tests.conftest import SLEEP_TIME_SEC, synthetic_monitoring_is_disable

OperationId = str

OperationResourceGetter = Callable[[OperationId], operation.Resource]


@pytest.mark.skipif(**synthetic_monitoring_is_disable())
class TestOperation:
    @pytest.fixture
    def operation_response(
        self,
        restapi_client: adsdatahub.restapi.Client,
        customer_id: CustomerId,
        imp_query_text: str,
    ) -> OperationModel[AnalysisQueryMetadataModel]:
        return restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=customer_id,
        ).start_transient(
            {
                "query": {"queryText": imp_query_text},
                "spec": {
                    "startDate": "2023-01-01",
                    "endDate": "2023-01-01",
                },
                "destTable": "operation_test",
            }
        )

    @pytest.fixture
    def operation_resource(
        self,
        restapi_client: adsdatahub.restapi.Client,
        operation_response: OperationModel[AnalysisQueryMetadataModel],
    ) -> adsdatahub.restapi.resources.operation.Resource:
        return restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/operations/{operation_id}",
            operation_id=operation_response.name.operation_id,
        )

    @pytest.mark.asyncio
    async def test_cancel(
        self, operation_resource: adsdatahub.restapi.resources.operation.Resource
    ):
        await asyncio.sleep(SLEEP_TIME_SEC)

        with pytest.raises(AdsDataHubResponseStatusCodeError):
            # NOTE: raise FAILED_PRECONDITION error.
            operation_resource.cancel()

    def test_delete(
        self, operation_resource: adsdatahub.restapi.resources.operation.Resource
    ):
        try:
            assert operation_resource.delete() is None

        except AdsDataHubUnimplementedError:
            # NOTE: サーバーによっては google.rpc.Code.UNIMPLEMENTED を返すことがある。
            #       Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/operations/delete?hl=ja
            pass

    def test_get(
        self, operation_resource: adsdatahub.restapi.resources.operation.Resource
    ):
        response = operation_resource.get()

        assert get_extra_fields(response) == {}

    def test_wait(
        self, operation_resource: adsdatahub.restapi.resources.operation.Resource
    ):
        response = operation_resource.wait()

        assert get_extra_fields(response) == {}

    @pytest.mark.long
    def test_wait_until_done(
        self, operation_resource: adsdatahub.restapi.resources.operation.Resource
    ):
        while not (operation := operation_resource.wait()).done:
            pass

        assert get_extra_fields(operation) == {}
