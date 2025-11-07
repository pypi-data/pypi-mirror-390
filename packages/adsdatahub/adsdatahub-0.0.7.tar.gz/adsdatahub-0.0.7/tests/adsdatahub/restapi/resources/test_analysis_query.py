import asyncio
import uuid

import adsdatahub.restapi
import adsdatahub.restapi.resources.analysis_query
import pytest
from adsdatahub._helpers import get_extra_fields
from adsdatahub.restapi.schemas.analysis_query import AnalysisQueryModel
from adsdatahub.types import CustomerId

from tests.conftest import SLEEP_TIME_SEC, synthetic_monitoring_is_disable


@pytest.mark.skipif(**synthetic_monitoring_is_disable())
class TestAnalysisQuery:
    @pytest.fixture
    def analysis_query(
        self, restapi_client: adsdatahub.restapi.Client, customer_id: CustomerId
    ) -> AnalysisQueryModel:
        return restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=customer_id,
        ).create(
            {
                "title": f"ads-data-hub-test-{uuid.uuid4()}",
                "queryText": "SELECT 1",
            }
        )

    @pytest.fixture
    def analysis_query_resource(
        self,
        analysis_query: AnalysisQueryModel,
        restapi_client: adsdatahub.restapi.Client,
    ) -> adsdatahub.restapi.resources.analysis_query.Resource:
        return restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}",
            customer_id=analysis_query.name.customer_id,
            analysis_query_id=analysis_query.name.analysis_query_id,
        )

    @pytest.mark.asyncio
    async def test_delete(
        self,
        analysis_query_resource: adsdatahub.restapi.resources.analysis_query.Resource,
    ):
        await asyncio.sleep(SLEEP_TIME_SEC)

        assert analysis_query_resource.delete() is None

    @pytest.mark.asyncio
    async def test_get(
        self,
        analysis_query_resource: adsdatahub.restapi.resources.analysis_query.Resource,
    ):
        await asyncio.sleep(SLEEP_TIME_SEC)

        try:
            analysis_query = analysis_query_resource.get()

            assert get_extra_fields(analysis_query) == {}

        finally:
            analysis_query_resource.delete()

    @pytest.mark.asyncio
    async def test_patch(
        self,
        analysis_query: AnalysisQueryModel,
        analysis_query_resource: adsdatahub.restapi.resources.analysis_query.Resource,
    ):
        await asyncio.sleep(SLEEP_TIME_SEC)

        try:
            analysis_query = analysis_query_resource.patch(
                {
                    "title": analysis_query.title,
                    "queryText": "SELECT 2",
                }
            )

            assert get_extra_fields(analysis_query) == {}

        finally:
            analysis_query_resource.delete()

    @pytest.mark.asyncio
    async def test_start(
        self,
        analysis_query_resource: adsdatahub.restapi.resources.analysis_query.Resource,
    ):
        await asyncio.sleep(SLEEP_TIME_SEC)

        try:
            operation = analysis_query_resource.start(
                {
                    "spec": {
                        "startDate": "2021-01-01",
                        "endDate": "2021-12-31",
                    },
                    "destTable": "project.dataset.table",
                }
            )

            assert get_extra_fields(operation) == {}

        finally:
            analysis_query_resource.delete()
