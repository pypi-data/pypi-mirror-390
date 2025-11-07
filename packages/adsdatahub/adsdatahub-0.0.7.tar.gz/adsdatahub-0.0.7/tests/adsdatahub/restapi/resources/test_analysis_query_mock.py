import uuid

import adsdatahub.restapi
import adsdatahub.restapi.resources.analysis_query
import pytest
from adsdatahub.restapi.schemas.analysis_query import AnalysisQueryModel
from adsdatahub.restapi.schemas.analysis_query_metadata import (
    AnalysisQueryMetadataModel,
)
from adsdatahub.restapi.schemas.operation import OperationModel
from adsdatahub.types import AnalysisQueryId, CustomerId


@pytest.mark.mock
class TestMockAnalysisQuery:
    @pytest.fixture
    def analysis_query(
        self,
        mock_customer_id: CustomerId,
        mock_analysis_query_id: AnalysisQueryId,
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

    def test_delete(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_customer_id: CustomerId,
        mock_analysis_query_id: AnalysisQueryId,
    ):
        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}",
            customer_id=mock_customer_id,
            analysis_query_id=mock_analysis_query_id,
        ).delete()

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}",
            customer_id=mock_customer_id,
            analysis_query_id=mock_analysis_query_id,
        ).delete()

        assert response is None

    def test_get(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_customer_id: CustomerId,
        mock_analysis_query_id: AnalysisQueryId,
        analysis_query: AnalysisQueryModel,
    ):
        expected_response = analysis_query

        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}",
            customer_id=mock_customer_id,
            analysis_query_id=mock_analysis_query_id,
        ).get(expected_response)

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}",
            customer_id=mock_customer_id,
            analysis_query_id=mock_analysis_query_id,
        ).get()

        assert response == expected_response

    def test_patch(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_customer_id: CustomerId,
        mock_analysis_query_id: AnalysisQueryId,
        analysis_query: AnalysisQueryModel,
        imp_query_text: str,
    ):
        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}",
            customer_id=mock_customer_id,
            analysis_query_id=mock_analysis_query_id,
        ).patch(analysis_query)

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}",
            customer_id=mock_customer_id,
            analysis_query_id=mock_analysis_query_id,
        ).patch(
            {
                "title": analysis_query.title,
                "queryText": imp_query_text,
            }
        )

        assert response == analysis_query

    def test_start(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_operation_id: AnalysisQueryId,
        mock_customer_id: CustomerId,
        mock_analysis_query_id: AnalysisQueryId,
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
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}",
            customer_id=mock_customer_id,
            analysis_query_id=mock_analysis_query_id,
        ).start(expected_response)

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}",
            customer_id=mock_customer_id,
            analysis_query_id=mock_analysis_query_id,
        ).start(
            {
                "spec": {
                    "startDate": "2021-01-01",
                    "endDate": "2021-12-31",
                },
                "destTable": "project.dataset.table",
            }
        )

        assert response == expected_response
