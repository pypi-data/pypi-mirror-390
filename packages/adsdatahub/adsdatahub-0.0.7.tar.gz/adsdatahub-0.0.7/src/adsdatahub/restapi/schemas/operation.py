from typing import Annotated, Generic, TypeVar

from pydantic import BeforeValidator, PlainSerializer, ValidationInfo

from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.analysis_query_metadata import (
    AnalysisQueryMetadataModel,
)
from adsdatahub.restapi.schemas.query_response import QueryResponseModel
from adsdatahub.restapi.schemas.status import StatusModel
from adsdatahub.types import OperationId

GenericAnalysisQueryMetadataModel = TypeVar(
    "GenericAnalysisQueryMetadataModel", bound=AnalysisQueryMetadataModel
)


class OperationNameModel(ExtraAllowModel):
    operation_id: OperationId

    def __str__(self) -> str:
        return f"operations/{self.operation_id}"


def _deserialize_name(value: str, info: ValidationInfo) -> dict[str, str]:
    if not value.startswith("operations/"):
        raise ValueError(f"Invalid operation name: {value}")

    return {"operation_id": value[len("operations/") :]}


def _serialize_name(model: OperationNameModel) -> str:
    return f"operations/{model.operation_id}"


class OperationModel(ExtraAllowModel, Generic[GenericAnalysisQueryMetadataModel]):
    """
    このリソースは、ネットワーク API 呼び出しの結果である長時間実行オペレーションを表します。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/operations?hl=ja#Operation
    """

    name: Annotated[
        OperationNameModel,
        BeforeValidator(_deserialize_name),
        PlainSerializer(_serialize_name),
    ]
    """
    サーバーによって割り当てられる名前。

    最初にその名前を返すサービスと同じサービス内でのみ一意になります。
    デフォルトの HTTP マッピングを使用している場合は、name を operations/{operation_id} で終わるリソース名にします。
    """

    metadata: GenericAnalysisQueryMetadataModel | None
    """
    オペレーションに関連付けられたサービス固有のデータを含む QueryMetadata オブジェクト。

    任意のデータ型のフィールドを含むオブジェクト。
    タイプを識別する URI を含むフィールド "@type" を追加できます。

    例: { "id": 1234, "@type": "types.example.com/standard/id" }
    """

    done: bool = False
    """
    値が false の場合は、オペレーションが進行中であることを意味します。

    true の場合、オペレーションは完了しており、error または response が利用可能です。
    """

    error: StatusModel | None = None
    """
    失敗またはキャンセルされた場合のオペレーションのエラー結果。
    """

    response: QueryResponseModel | None = None
    """
    クエリ オペレーションが成功した場合に返される QueryResponse オブジェクト。

    任意のデータ型のフィールドを含むオブジェクト。
    タイプを識別する URI を含むフィールド "@type" を追加できます。

    例: { "id": 1234, "@type": "types.example.com/standard/id" }
    """
