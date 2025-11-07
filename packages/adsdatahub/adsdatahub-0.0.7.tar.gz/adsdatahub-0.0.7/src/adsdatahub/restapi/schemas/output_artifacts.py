from typing import Annotated

from pydantic import Field

from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.temp_table import TempTableModel


class OutputArtifactsModel(ExtraAllowModel):
    """
    クエリの実行中に作成される出力アーティファクト。
    一時テーブルは、Ads Data Hub クエリで CREATE TABLE temp_table AS (...) を使用して作成されます。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/OutputArtifacts?hl=ja
    """

    temp_tables: Annotated[
        list[TempTableModel], Field(alias="tempTables", default_factory=list)
    ]
