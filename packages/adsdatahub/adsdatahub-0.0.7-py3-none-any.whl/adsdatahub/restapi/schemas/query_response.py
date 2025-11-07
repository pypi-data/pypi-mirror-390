from typing import Annotated

from pydantic import Field

from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.destination_table_info import DestinationTableInfoModel
from adsdatahub.restapi.schemas.output_artifacts import OutputArtifactsModel
from adsdatahub.restapi.schemas.privacy_message import PrivacyMessageModel


class QueryResponseModel(ExtraAllowModel):
    """
    クエリ実行ジョブが成功すると、レスポンスが返されます。
    これは、クエリ実行リクエストによって返される google.longrunning.Operation のレスポンス フィールドに保存されます。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/QueryResponse?hl=ja
    """

    type: Annotated[
        str,
        Field(alias="@type"),
    ]
    """
    タイプを識別する URI を含むフィールド。
    """

    row_count: Annotated[
        int,
        Field(alias="rowCount"),
    ]
    """
    最終出力テーブルの行数。

    ラップされた値は、行数が 0 のケースと、この情報が利用できないケースを区別するために使用されます。
    """

    destination_tables: Annotated[
        list[DestinationTableInfoModel],
        Field(alias="destinationTables", default_factory=list),
    ]
    """
    実行結果のテーブル情報。

    ドキュメントには記載されていないが、実際のレスポンスには含まれる。
    ノイズなどの情報が含まれている。
    """

    output_artifacts: Annotated[
        OutputArtifactsModel,
        Field(alias="outputArtifacts"),
    ]
    """
    クエリ実行中に生成された出力アーティファクト。
    """

    privacy_messages: Annotated[
        list[PrivacyMessageModel],
        Field(alias="privacyMessages", default_factory=list),
    ]
    """
    プライバシー関連の情報または警告メッセージのリスト。
    """
