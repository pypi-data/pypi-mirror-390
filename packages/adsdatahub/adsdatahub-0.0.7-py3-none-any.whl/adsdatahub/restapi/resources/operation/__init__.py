import datetime
from typing import TYPE_CHECKING, Literal, TypedDict, Unpack

from adsdatahub.restapi.resources.operation.wait import OperationWaitRequestBody
from adsdatahub.restapi.schemas.analysis_query_metadata import (
    AnalysisQueryMetadataModel,
    AnalysisQueryMetadataWithQueryTextModel,
)
from adsdatahub.restapi.schemas.operation import OperationModel
from adsdatahub.types import OperationId

if TYPE_CHECKING:
    import adsdatahub.restapi.http

ResourceName = Literal["https://adsdatahub.googleapis.com/v1/operations/{operation_id}"]
RESOURCE_NAME: ResourceName = (
    "https://adsdatahub.googleapis.com/v1/operations/{operation_id}"
)


class PathParameters(TypedDict):
    operation_id: OperationId


class Resource:
    """
    このリソースは、ネットワーク API 呼び出しの結果である長時間実行オペレーションを表します。
    """

    def __init__(
        self, client: "adsdatahub.restapi.http.Client", path_parameters: PathParameters
    ) -> None:
        self._client = client
        self._base_url = RESOURCE_NAME.format(**path_parameters)

    def cancel(self) -> None:
        """
        長時間実行オペレーションの非同期キャンセルを開始します。
        サーバーは操作のキャンセルに全力を尽くしますが、成功は保証されません。
        このメソッドがサーバーでサポートされていない場合は、google.rpc.Code.UNIMPLEMENTED を返します。
        クライアントは Operations.GetOperation などのメソッドを使用して、キャンセルが成功したか、あるいはキャンセルしたにもかかわらずオペレーションが完了したかを確認できます。
        キャンセルが成功するとそのオペレーションは削除されず、google.rpc.Status.code が 1 の Operation.error 値を持つオペレーションになります。
        これは Code.CANCELLED に相当します。

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/operations/cancel?hl=ja
        """
        return self._client.request("POST", f"{self._base_url}:cancel")

    def delete(self) -> None:
        """
        長時間実行オペレーションを削除します。
        このメソッドは、クライアントがそのオペレーション結果に関心がなくなったことを表しています。
        このメソッドではオペレーションはキャンセルされません。
        このメソッドがサーバーでサポートされていない場合は、google.rpc.Code.UNIMPLEMENTED を返します。

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/operations/delete?hl=ja
        """

        return self._client.request("DELETE", self._base_url)

    def get(self) -> OperationModel[AnalysisQueryMetadataWithQueryTextModel]:
        """
        長時間実行オペレーションの最新の状態を取得します。
        クライアントはこのメソッドを使用して、API サービスで推奨される間隔でオペレーションの結果をポーリングできます。

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/operations/get?hl=ja
        """

        return self._client.request(
            "GET",
            self._base_url,
            OperationModel[AnalysisQueryMetadataWithQueryTextModel],
        )

    def wait(
        self, request_body: OperationWaitRequestBody | None = None
    ) -> OperationModel[AnalysisQueryMetadataModel]:
        """
        指定した長時間実行オペレーションが完了するか、指定したタイムアウトに達するまで待機し、最新の状態を返します。

        オペレーションがすでに完了している場合は、すぐに最新の状態が返されます。
        指定されたタイムアウトがデフォルトの HTTP/RPC タイムアウトを上回る場合は、HTTP/RPC タイムアウトが使用されます。
        サーバーがこのメソッドをサポートしていない場合は、google.rpc.Code.UNIMPLEMENTED を返します。
        このメソッドはベスト エフォートに基づきます。
        指定されたタイムアウト（直前を含む）の前に最新の状態を返すことがあります。
        つまり、すぐにレスポンスがあったとしても、オペレーションが完了したことを保証するものではありません。

        Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/operations/wait?hl=ja
        """
        request_body = request_body or {}

        if timeout := request_body.get("timeout"):
            match timeout:
                case str():
                    timeout_sec = timeout
                case int() | float():
                    timeout_sec = f"{timeout}s"
                case datetime.timedelta():
                    timeout_sec = f"{timeout.total_seconds()}s"
            request_body["timeout"] = timeout_sec

        return self._client.request(
            "POST",
            f"{self._base_url}:wait",
            OperationModel[AnalysisQueryMetadataModel],
            json=request_body,
        )


class MockResource:
    def __init__(
        self,
        mock_client: "adsdatahub.restapi.MockClient",
        **path_parameters: Unpack[PathParameters],
    ) -> None:
        self._mock_client = mock_client
        self._base_url = RESOURCE_NAME.format(**path_parameters)

    def cancel(
        self, response: None | Exception = None
    ) -> "adsdatahub.restapi.MockClient":
        self._mock_client._http.inject_response(
            "POST", f"{self._base_url}:cancel", response
        )

        return self._mock_client

    def delete(
        self, response: None | Exception = None
    ) -> "adsdatahub.restapi.MockClient":
        self._mock_client._http.inject_response("DELETE", self._base_url, response)

        return self._mock_client

    def get(
        self,
        response: OperationModel[AnalysisQueryMetadataWithQueryTextModel] | Exception,
    ) -> "adsdatahub.restapi.MockClient":
        self._mock_client._http.inject_response("GET", self._base_url, response)

        return self._mock_client

    def wait(
        self, response: OperationModel[AnalysisQueryMetadataModel] | Exception
    ) -> "adsdatahub.restapi.MockClient":
        self._mock_client._http.inject_response(
            "POST", f"{self._base_url}:wait", response
        )

        return self._mock_client
