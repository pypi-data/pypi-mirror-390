import uuid

import adsdatahub.restapi
import pytest
from adsdatahub.restapi.resources.analysis_queries.list import AnalysisQueryListResponse
from adsdatahub.restapi.resources.analysis_queries.validate import (
    AnalysisQueriesValidateResponseBodyModel,
)
from adsdatahub.restapi.schemas.analysis_query import (
    AnalysisQueryModel,
)
from adsdatahub.restapi.schemas.analysis_query_metadata import (
    AnalysisQueryMetadataModel,
)
from adsdatahub.restapi.schemas.operation import OperationModel
from adsdatahub.types import AnalysisQueryId, CustomerId, OperationId


@pytest.mark.mock
class TestMockAnalysisQueries:
    @pytest.fixture
    def analysis_query(
        self,
        mock_analysis_query_id: AnalysisQueryId,
        mock_customer_id: CustomerId,
        imp_query_text: str,
    ):
        return AnalysisQueryModel.model_validate(
            {
                "name": f"customers/{mock_customer_id}/analysisQueries/{mock_analysis_query_id}",
                "title": f"ads-data-hub-test-{uuid.uuid4()}",
                "queryText": imp_query_text,
                "queryState": "RUNNABLE",
                "updateTime": "2024-02-28T15:50:11.497000Z",
                "updateEmail": "myaccount@myproject.iam.gserviceaccount.com",
                "createTime": "2024-02-28T15:50:11.497000Z",
                "createEmail": "myaccount@myproject.iam.gserviceaccount.com",
            }
        )

    def test_create(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_customer_id: CustomerId,
        analysis_query: AnalysisQueryModel,
        imp_query_text: str,
    ):
        title = f"ads-data-hub-test-{uuid.uuid4()}"

        expected_response = analysis_query

        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=mock_customer_id,
        ).create(
            expected_response,
        )

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=mock_customer_id,
        ).create(
            {
                "title": title,
                "queryText": imp_query_text,
            }
        )

        assert response == expected_response

    def test_list(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_customer_id: CustomerId,
        analysis_query: AnalysisQueryModel,
    ):
        expected_response = AnalysisQueryListResponse.model_validate(
            {
                "queries": [
                    analysis_query,
                ]
            }
        )

        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=mock_customer_id,
        ).list(expected_response)

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=mock_customer_id,
        ).list()

        assert response == expected_response

    def test_start_transient(
        self,
        mock_operation_id: OperationId,
        mock_customer_id: CustomerId,
        mock_restapi_client: adsdatahub.restapi.MockClient,
    ):
        expected_response = OperationModel[AnalysisQueryMetadataModel].model_validate(
            {
                "name": f"operations/{mock_operation_id}",
                "metadata": {
                    "@type": "type.googleapis.com/google.ads.adsdatahub.v1.QueryMetadata",
                    "customerId": mock_customer_id,
                    "adsDataCustomerId": mock_customer_id,
                    "matchDataCustomerId": mock_customer_id,
                    "parameterValues": {
                        "start_date": {"value": "2021-01-01"},
                        "end_date": {"value": "2021-12-31"},
                        "time_zone": {"value": "UTC"},
                    },
                    "startTime": "2024-03-03T02:13:32.165710Z",
                    "endTime": "1970-01-01T00:00:00Z",
                    "destTable": "project.dataset.table",
                },
            }
        )

        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=mock_customer_id,
        ).start_transient(expected_response)

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=mock_customer_id,
        ).start_transient(
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

        assert response == expected_response

    def test_validate(
        self,
        mock_customer_id: CustomerId,
        mock_restapi_client: adsdatahub.restapi.MockClient,
    ):
        expected_response = AnalysisQueriesValidateResponseBodyModel.model_validate(
            {
                "queryPerformanceInfo": {
                    "zeroMb": True,
                },
                "filteredRowSummary": {},
            }
        )

        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=mock_customer_id,
        ).validate(expected_response)

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries",
            customer_id=mock_customer_id,
        ).validate(
            {
                "query": {
                    "queryText": "SELECT * FROM project.dataset.table",
                },
                "spec": {
                    "startDate": "2021-01-01",
                    "endDate": "2021-12-31",
                },
                "includePerformanceInfo": True,
            }
        )

        assert response == expected_response
