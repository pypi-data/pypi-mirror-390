import adsdatahub.restapi
import pytest
from adsdatahub.restapi.schemas.analysis_query_metadata import (
    AnalysisQueryMetadataModel,
    AnalysisQueryMetadataWithQueryTextModel,
)
from adsdatahub.restapi.schemas.operation import OperationModel
from adsdatahub.types import CustomerId, OperationId


@pytest.mark.mock
class TestMockOperation:
    def test_cancel(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_operation_id: OperationId,
    ):
        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/operations/{operation_id}",
            operation_id=mock_operation_id,
        ).cancel()

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/operations/{operation_id}",
            operation_id=mock_operation_id,
        ).cancel()

        assert response is None

    def test_delete(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_operation_id: OperationId,
    ):
        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/operations/{operation_id}",
            operation_id=mock_operation_id,
        ).delete()

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/operations/{operation_id}",
            operation_id=mock_operation_id,
        ).delete()

        assert response is None

    def test_get(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_customer_id: CustomerId,
        mock_operation_id: OperationId,
        imp_query_text: str,
    ):
        expected_response = OperationModel[
            AnalysisQueryMetadataWithQueryTextModel
        ].model_validate(
            {
                "name": f"operations/{mock_operation_id}",
                "metadata": {
                    "@type": "type.googleapis.com/google.ads.adsdatahub.v1.QueryMetadata",
                    "customerId": mock_customer_id,
                    "adsDataCustomerId": mock_customer_id,
                    "matchDataCustomerId": mock_customer_id,
                    "parameterValues": {
                        "start_date": {"value": "2023-01-01"},
                        "end_date": {"value": "2023-01-01"},
                        "time_zone": {"value": "UTC"},
                    },
                    "startTime": "2024-03-03T04:54:46.444162Z",
                    "endTime": "1970-01-01T00:00:00Z",
                    "destTable": "project.dataset.table",
                    "queryText": imp_query_text,
                },
            }
        )

        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/operations/{operation_id}",
            operation_id=mock_operation_id,
        ).get(expected_response)

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/operations/{operation_id}",
            operation_id=mock_operation_id,
        ).get()

        assert response == expected_response

    def test_wait(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_operation_id: OperationId,
        mock_customer_id: CustomerId,
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
                        "start_date": {"value": "2023-01-01"},
                        "end_date": {"value": "2023-01-01"},
                        "time_zone": {"value": "UTC"},
                    },
                    "startTime": "2024-03-03T05:00:15.382693Z",
                    "endTime": "1970-01-01T00:00:00Z",
                    "destTable": "project.dataset.table",
                },
            }
        )

        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/operations/{operation_id}",
            operation_id=mock_operation_id,
        ).wait(expected_response)

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/operations/{operation_id}",
            operation_id=mock_operation_id,
        ).wait()

        assert response == expected_response
