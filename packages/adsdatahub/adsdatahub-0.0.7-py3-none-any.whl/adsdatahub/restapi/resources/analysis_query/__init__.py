from typing import TYPE_CHECKING, Literal, TypedDict, Unpack

from adsdatahub._helpers import (
    convert_json_value,
)
from adsdatahub.restapi.resources.analysis_query.start import (
    AnalysisQueryStartRequestBody,
)
from adsdatahub.restapi.schemas.analysis_query import (
    AnalysisQueryModel,
    AnalysisQueryRequestDict,
    AnalysisQueryRequestModel,
)
from adsdatahub.restapi.schemas.analysis_query_metadata import (
    AnalysisQueryMetadataModel,
)
from adsdatahub.restapi.schemas.operation import OperationModel
from adsdatahub.restapi.schemas.query_execution_spec import (
    QueryExecutionSpecRequestModel,
)
from adsdatahub.types import AnalysisQueryId, CustomerId

if TYPE_CHECKING:
    import adsdatahub.restapi.http

ResourceName = Literal[
    "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}"
]
RESOURCE_NAME: ResourceName = "https://adsdatahub.googleapis.com/v1/customers/{customer_id}/analysisQueries/{analysis_query_id}"


class PathParameters(TypedDict):
    customer_id: CustomerId
    analysis_query_id: AnalysisQueryId


class Resource:
    def __init__(
        self, http: "adsdatahub.restapi.http.Client", path_parameters: PathParameters
    ) -> None:
        self._http = http
        self._base_url = RESOURCE_NAME.format(**path_parameters)

    def delete(self) -> None:
        """
        分析クエリを削除します。

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.analysisQueries/delete?hl=ja
        """
        return self._http.request("DELETE", self._base_url)

    def get(self) -> AnalysisQueryModel:
        """
        リクエストされた分析クエリを取得します。

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.analysisQueries/get?hl=ja
        """
        return self._http.request(
            "GET",
            self._base_url,
            AnalysisQueryModel,
        )

    def patch(
        self, request_body: AnalysisQueryRequestModel | AnalysisQueryRequestDict
    ) -> AnalysisQueryModel:
        """
        既存の分析クエリを更新します。部分更新はサポートされています。次のクエリ フィールドは、この方法では更新できないため、無視されます。

        - queryState
        - createTime
        - createEmail（作成メール）
        - updateTime
        - updateEmail

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.analysisQueries/patch?hl=ja
        """
        return self._http.request(
            "PATCH",
            self._base_url,
            AnalysisQueryModel,
            json=(
                AnalysisQueryRequestModel.model_validate(request_body)
                if isinstance(request_body, dict)
                else request_body
            ).model_dump(),
        )

    def start(
        self, request_body: AnalysisQueryStartRequestBody
    ) -> OperationModel[AnalysisQueryMetadataModel]:
        """
        保存された分析クエリの実行を開始します。
        結果は、指定した BigQuery 宛先テーブルに書き込まれます。
        返されたオペレーション名を使用して、クエリ完了ステータスをポーリングできます。

        Refarence: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.analysisQueries/start?hl=ja
        """

        return self._http.request(
            "POST",
            f"{self._base_url}:start",
            OperationModel[AnalysisQueryMetadataModel],
            json=convert_json_value(
                request_body,
                model_map={
                    "spec": QueryExecutionSpecRequestModel,
                },
            ),
        )


class MockResource:
    def __init__(
        self,
        mock_client: "adsdatahub.restapi.MockClient",
        **path_parameters: Unpack[PathParameters],
    ) -> None:
        self._mock_client = mock_client
        self._base_url = RESOURCE_NAME.format(**path_parameters)

    def delete(
        self, response: None | Exception = None
    ) -> "adsdatahub.restapi.MockClient":
        self._mock_client._http.inject_response("DELETE", self._base_url, response)

        return self._mock_client

    def get(
        self, response: AnalysisQueryModel | Exception
    ) -> "adsdatahub.restapi.MockClient":
        self._mock_client._http.inject_response("GET", self._base_url, response)

        return self._mock_client

    def patch(
        self, response: AnalysisQueryModel | Exception
    ) -> "adsdatahub.restapi.MockClient":
        self._mock_client._http.inject_response("PATCH", self._base_url, response)

        return self._mock_client

    def start(
        self, response: OperationModel[AnalysisQueryMetadataModel] | Exception
    ) -> "adsdatahub.restapi.MockClient":
        self._mock_client._http.inject_response(
            "POST", f"{self._base_url}:start", response
        )

        return self._mock_client
