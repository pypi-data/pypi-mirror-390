import adsdatahub
import pytest

from tests.conftest import synthetic_monitoring_is_disable


@pytest.mark.skipif(**synthetic_monitoring_is_disable())
class TestRealClient:
    def test_constructor_type(self):
        assert isinstance(adsdatahub.RealClient(), adsdatahub.RealClient)
