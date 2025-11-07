import adsdatahub.exceptions
import adsdatahub.restapi
import pytest


class TestMockClient:
    def test_client_constructer_type(self):
        assert isinstance(
            adsdatahub.restapi.MockClient(), adsdatahub.restapi.MockClient
        )

    def test_raise_mock_store_date_empty_error(
        self, mock_restapi_client: adsdatahub.restapi.MockClient
    ):
        with pytest.raises(adsdatahub.exceptions.AdsDataHubMockStoreDataEmptyError):
            mock_restapi_client.resource(
                "https://adsdatahub.googleapis.com/v1/operations"
            ).list()
