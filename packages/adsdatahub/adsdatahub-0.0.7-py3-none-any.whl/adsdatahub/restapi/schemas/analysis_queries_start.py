from typing_extensions import NotRequired, TypedDict

from adsdatahub.restapi.schemas._model import ExtraForbidModel
from adsdatahub.restapi.schemas.query_execution_spec import (
    QueryExecutionSpecRequestDict,
    QueryExecutionSpecRequestModel,
)


class AnalysisQueriesStartDict(TypedDict):
    """
    保存された分析クエリの実行を開始します。
    結果は、指定した BigQuery 宛先テーブルに書き込まれます。
    返されたオペレーション名を使用して、クエリ完了ステータスをポーリングできます。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.analysisQueries/start?hl=ja
    """

    spec: QueryExecutionSpecRequestDict
    """クエリ実行パラメータを定義します。"""

    destTable: str
    """
    'project.dataset.table_name' 形式のクエリ結果の宛先 BigQuery テーブル。
    指定するには、お客様の ADH アカウントのプロジェクトを明示的に許可リストに登録する必要があります。
    プロジェクトが指定されていない場合は、指定したお客様のデフォルトのプロジェクトが使用されます。
    プロジェクトもデータセットも指定しない場合、デフォルトのプロジェクトとデータセットが使用されます。
    """

    customerId: NotRequired[str | None]
    """
    Ads Data Hub のお客様がクエリを実行します。
    指定しない場合は、デフォルトでクエリを所有する顧客が対象となります。
    """


class AnalysisQueriesStartModel(ExtraForbidModel):
    spec: QueryExecutionSpecRequestModel
    destTable: str
    customerId: str | None
