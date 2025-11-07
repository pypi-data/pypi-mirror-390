import os
import random
from textwrap import dedent

import adsdatahub.restapi
import pytest
from adsdatahub.types import AnalysisQueryId, CustomerId, OperationId

SLEEP_TIME_SEC = 3


def synthetic_monitoring_is_disable() -> dict:
    """
    外形監視が無効であるかどうかを確認する。

    下記の環境変数を設定すると、実際に API を叩いてテストが行われる。

    ```env
    SYNTHETIC_MONITORING_TEST=true
    ```
    """

    return dict(
        condition=(
            "SYNTHETIC_MONITORING_TEST" not in os.environ
            or os.environ["SYNTHETIC_MONITORING_TEST"].lower() != "true"
        ),
        reason="外形監視が有効時（環境変数 SYNTHETIC_MONITORING_TEST が true ）に実行されます。",
    )


@pytest.fixture
def client() -> adsdatahub.Client:
    return adsdatahub.Client(
        client_options={
            "credentials_file": os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
        },
    )


@pytest.fixture
def restapi_client():
    return adsdatahub.restapi.Client(
        client_options={
            "credentials_file": os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
        }
    )


@pytest.fixture
def mock_restapi_client():
    return adsdatahub.restapi.MockClient()


@pytest.fixture
def customer_id() -> CustomerId:
    # NOTE: Customer ID は複数指定できる。
    #       これは実際に API を叩く際に、1分間に使える Job 数制限を回避するため。
    if customer_ids := os.environ.get("CUSTOMER_IDS"):
        return random.choice(customer_ids.split(","))

    else:
        return os.environ["CUSTOMER_ID"]


@pytest.fixture
def project() -> str:
    return os.environ["PROJECT"]


@pytest.fixture
def dataset() -> str:
    return os.environ["DATASET"]


@pytest.fixture
def imp_query_text() -> str:
    return dedent(
        """
        SELECT
            campaign_id,
            date(timestamp_micros(query_id.time_usec), 'Asia/Tokyo') AS date,
            count(query_id.time_usec) AS imp
        FROM
            adh.google_ads_impressions
        GROUP BY
            campaign_id,
            date
        """
    )


@pytest.fixture
def mock_customer_id() -> CustomerId:
    return "this_is_mock_customer_query_id"


@pytest.fixture
def mock_analysis_query_id() -> AnalysisQueryId:
    return "this_is_mock_analysis_query_id"


@pytest.fixture
def mock_operation_id() -> OperationId:
    return "this_is_mock_operation_id"
