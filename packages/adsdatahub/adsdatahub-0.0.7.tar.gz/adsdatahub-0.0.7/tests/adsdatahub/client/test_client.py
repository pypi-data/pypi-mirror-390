import datetime
import uuid

import adsdatahub
import pytest
from adsdatahub.client.parameters import PythonParameter
from adsdatahub.exceptions import (
    AdsDataHubResponseBodyHasError,
    AdsDataHubResponseStatusCodeError,
)
from adsdatahub.types import CustomerId
from google.cloud import bigquery

from tests.conftest import synthetic_monitoring_is_disable


@pytest.mark.skipif(**synthetic_monitoring_is_disable())
class TestClient:
    @pytest.fixture
    def table_name(self, project: str, dataset: str) -> str:
        return f"{project}.{dataset}.ads_data_bub_test_{str(uuid.uuid4()).replace('-', '')}"

    def test_constructor_type(self):
        assert isinstance(adsdatahub.Client(), adsdatahub.RealClient)

    @pytest.mark.long
    def test_query(
        self,
        client: adsdatahub.Client,
        imp_query_text: str,
        customer_id: CustomerId,
        table_name: str,
    ):
        try:
            client.customer(customer_id).query(
                imp_query_text,
                start_date="2021-01-01",
                end_date="2021-01-02",
                dest_table=table_name,
            )

        finally:
            bigquery.Client().delete_table(table_name, not_found_ok=True)

    @pytest.mark.long
    def test_query_with_default_parameter(
        self,
        client: adsdatahub.Client,
        customer_id: CustomerId,
        table_name: str,
    ):
        try:
            # NOTE: start_date, end_date はデフォルトで定義されているため、エラーにならない。
            client.customer(customer_id).query(
                "SELECT @start_date as start_date",
                start_date="2021-01-01",
                end_date="2021-01-02",
                dest_table=table_name,
            )

        finally:
            bigquery.Client().delete_table(table_name, not_found_ok=True)

    @pytest.mark.long
    def test_query_with_undefined_parameter(
        self,
        client: adsdatahub.Client,
        customer_id: CustomerId,
    ):
        with pytest.raises(AdsDataHubResponseBodyHasError):
            client.customer(customer_id).query(
                "SELECT @value as value",
                start_date="2021-01-01",
                end_date="2021-01-02",
                dest_table="test",
            )

    @pytest.mark.long
    def test_query_with_parameter(
        self,
        client: adsdatahub.Client,
        customer_id: CustomerId,
        table_name: str,
    ):
        try:
            client.customer(customer_id).query(
                "SELECT @value as value",
                {"value": 1},
                start_date="2021-01-01",
                end_date="2021-01-02",
                dest_table=table_name,
            )

        finally:
            bigquery.Client().delete_table(table_name, not_found_ok=True)

    @pytest.mark.long
    def test_query_with_pydantic_parameter(
        self,
        client: adsdatahub.Client,
        customer_id: CustomerId,
    ):
        from pydantic import BaseModel

        class MyParameter(BaseModel):
            value: str | None = None

        result = client.customer(customer_id).query(
            "SELECT @value as value",
            MyParameter(),
            start_date="2024-01-01",
            end_date="2024-02-02",
            dest_table="test",
        )

        assert result.operation.done is True

    def test_validate_with_default_parameter(
        self,
        client: adsdatahub.Client,
        customer_id: CustomerId,
    ):
        # NOTE: start_date, end_date はデフォルトで定義されているため、エラーにならない。
        client.customer(customer_id).validate(
            "SELECT @start_date as start_date",
        )

    def test_validate_with_undefined_parameter(
        self,
        client: adsdatahub.Client,
        customer_id: CustomerId,
    ):
        with pytest.raises(AdsDataHubResponseStatusCodeError):
            client.customer(customer_id).validate(
                "SELECT @value as value",
            )

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(1, id="int"),
            pytest.param(1.1, id="float"),
            pytest.param("str", id="str"),
            pytest.param(True, id="bool"),
            pytest.param(datetime.date.today(), id="date"),
            pytest.param(datetime.datetime.now(), id="timestamp"),
            pytest.param(["a", "b", "c"], id="str_list"),
            pytest.param([1, 2, 3], id="int_list"),
            pytest.param([1.1, 2.2, 3.3], id="float_list"),
            pytest.param([True, False], id="bool_list"),
            pytest.param([datetime.date.today()], id="date_list"),
            pytest.param([datetime.datetime.now()], id="timestamp_list"),
            pytest.param([], id="empty_list"),
            # pytest.param(None, id="None"), # NOTE: None はエラーになる。NULL と言う方はサポートされていない。
        ],
    )
    def test_validate_with_parameter(
        self,
        client: adsdatahub.Client,
        customer_id: CustomerId,
        value: PythonParameter,
    ):
        client.customer(customer_id).validate(
            "SELECT @value as value",
            {"value": value},
        )

    def test_validate_with_pydantic_parameter(
        self,
        client: adsdatahub.Client,
        customer_id: CustomerId,
    ):
        from pydantic import BaseModel

        class MyParameter(BaseModel):
            value: str | None = None

        client.customer(customer_id).validate(
            "SELECT @value as value",
            MyParameter(),
        )
