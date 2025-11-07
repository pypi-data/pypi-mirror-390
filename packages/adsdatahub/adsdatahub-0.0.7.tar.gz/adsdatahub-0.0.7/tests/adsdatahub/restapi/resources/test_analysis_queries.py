import uuid

import adsdatahub.restapi
import pytest
from adsdatahub._helpers import get_extra_fields
from adsdatahub.restapi.resources import analysis_queries
from adsdatahub.types import CustomerId

from tests.conftest import synthetic_monitoring_is_disable
from tests.helper import write_response_json


@pytest.mark.skipif(**synthetic_monitoring_is_disable())
class TestAnalysisQueries:
    @pytest.fixture
    def analysis_queries_resource(
        self,
        restapi_client: adsdatahub.restapi.Client,
        customer_id: CustomerId,
    ) -> analysis_queries.Resource:
        return restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=customer_id,
        )

    def test_create(
        self,
        analysis_queries_resource: analysis_queries.Resource,
        restapi_client: adsdatahub.restapi.Client,
        imp_query_text: str,
    ):
        analysis_query = None
        try:
            analysis_query = analysis_queries_resource.create(
                {
                    "title": f"ads-data-hub-test-{uuid.uuid4()}",
                    "queryText": imp_query_text,
                }
            )

            assert get_extra_fields(analysis_query) == {}

        finally:
            if analysis_query:
                restapi_client.resource(
                    "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}",
                    customer_id=analysis_query.name.customer_id,
                    analysis_query_id=analysis_query.name.analysis_query_id,
                )

    def test_list(self, analysis_queries_resource: analysis_queries.Resource):
        response = analysis_queries_resource.list()

        assert get_extra_fields(response) == {}

    def test_start_transient(
        self,
        analysis_queries_resource: analysis_queries.Resource,
    ):
        operation = analysis_queries_resource.start_transient(
            {
                "query": {
                    "queryText": "SELECT * FROM project.dataset.table",
                },
                "spec": {
                    "startDate": "2021-01-01",
                    "endDate": "2021-12-31",
                },
                "destTable": "project.dataset.table",
            }
        )

        assert get_extra_fields(operation) == {}

    def test_validate(
        self,
        analysis_queries_resource: analysis_queries.Resource,
        imp_query_text: str,
    ):
        validation = analysis_queries_resource.validate(
            {
                "query": {"queryText": imp_query_text},
            }
        )

        write_response_json(validation)

        assert get_extra_fields(validation) == {}
