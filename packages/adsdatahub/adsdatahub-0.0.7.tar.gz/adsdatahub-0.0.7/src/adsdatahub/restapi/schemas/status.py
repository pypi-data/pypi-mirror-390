from typing import Annotated

from pydantic import Field
from typing_extensions import TypedDict

from adsdatahub.restapi.schemas._model import ExtraAllowModel


class StatusDict(TypedDict):
    """
    Status 型は、REST API や RPC API など、さまざまなプログラミング環境に適した論理エラーモデルを定義します。
    gRPC により使用されます。
    各 Status メッセージには、エラーコード、エラー メッセージ、エラーの詳細という 3 種類のデータが含まれます。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/operations?hl=ja#Status
    """

    code: int
    """ステータス コード。google.rpc.Code の列挙値である必要があります。"""

    message: str
    """
    デベロッパー向けのエラー メッセージ。
    英語で記述します。
    ユーザー向けのエラー メッセージは、ローカライズして google.rpc.Status.details フィールドで送信するか、
    クライアントでローカライズする必要があります。
    """

    details: list[dict]
    """
    エラーの詳細を保持するメッセージのリスト。
    API が使用する共通のメッセージ タイプのセットがあります。

    任意のデータ型のフィールドを含むオブジェクト。
    タイプを識別する URI を含むフィールド "@type" を追加できます。

    例: { "id": 1234, "@type": "types.example.com/standard/id" }
    """


class StatusModel(ExtraAllowModel):
    code: int

    message: str

    details: Annotated[list[dict], Field(default_factory=list)]
