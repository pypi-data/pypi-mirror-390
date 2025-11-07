from typing import Callable

import adsdatahub.restapi
import pytest
from adsdatahub._helpers import get_extra_fields
from adsdatahub.exceptions import (
    AdsDataHubUnavailableError,
    AdsDataHubUnimplementedError,
)
from adsdatahub.restapi.resources import operation
from adsdatahub.restapi.schemas._model import Model
from adsdatahub.restapi.schemas.operation import OperationModel

from tests.conftest import synthetic_monitoring_is_disable

OperationId = str

OperationResourceGetter = Callable[[OperationId], operation.Resource]


class Operations(Model):
    operations: list[OperationModel]


@pytest.mark.skipif(**synthetic_monitoring_is_disable())
class TestOperations:
    def test_list(self, restapi_client: adsdatahub.restapi.Client):
        try:
            response = restapi_client.resource(
                "https://adsdatahub.googleapis.com/v1/operations"
            ).list()

            assert get_extra_fields(response) == {}

        except (AdsDataHubUnimplementedError, AdsDataHubUnavailableError):
            # NOTE: たまに 503 が返ってくることがある。
            pass
