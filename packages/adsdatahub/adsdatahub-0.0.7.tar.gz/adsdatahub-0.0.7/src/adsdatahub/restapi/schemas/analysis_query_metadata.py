from typing import Annotated

from pydantic import Field

from adsdatahub.restapi.schemas.query_metadata import QueryMetadataBaseModel


class AnalysisQueryMetadataModel(QueryMetadataBaseModel):
    """
    クエリ実行ジョブに関するメタデータ。
    これは、クエリ実行リクエストによって返される google.longrunning.Operation のメタデータフィールドに保存されます。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/QueryMetadata?hl=ja
    """

    dest_table: Annotated[str | None, Field(alias="destTable")] = None
    """
    クエリ結果の宛先テーブル。

    分析クエリに使用されます。
    """


class AnalysisQueryMetadataWithQueryTextModel(AnalysisQueryMetadataModel):
    query_text: Annotated[str | None, Field(alias="queryText")] = None
    """
    実行されたクエリのテキスト。

    このフィールドは、google.longrunning.Operations.GetOperation 呼び出しのレスポンスでのみ設定されます。
    google.longrunning.Operations.ListOperations の呼び出しや他の呼び出しのレスポンスでは省略されます。
    """
