import adsdatahub.restapi
import pytest

from tests.conftest import synthetic_monitoring_is_disable


@pytest.mark.skipif(**synthetic_monitoring_is_disable())
class TestRealClient:
    def test_client_constructer_type(self):
        assert isinstance(
            adsdatahub.restapi.RealClient(), adsdatahub.restapi.RealClient
        )
