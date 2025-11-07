import adsdatahub.restapi
import pytest
from adsdatahub.restapi.resources.operations.list import OperationsListResponseBody
from adsdatahub.types import CustomerId, OperationId


@pytest.mark.mock
class TestMockOperations:
    def test_list(
        self,
        mock_restapi_client: adsdatahub.restapi.MockClient,
        mock_operation_id: OperationId,
        mock_customer_id: CustomerId,
    ):
        expected_response = OperationsListResponseBody.model_validate(
            {
                "operations": [
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
                ]
            }
        )

        mock_restapi_client.inject_response(
            "https://adsdatahub.googleapis.com/v1/operations"
        ).list(expected_response)

        response = mock_restapi_client.resource(
            "https://adsdatahub.googleapis.com/v1/operations"
        ).list()

        assert response == expected_response
