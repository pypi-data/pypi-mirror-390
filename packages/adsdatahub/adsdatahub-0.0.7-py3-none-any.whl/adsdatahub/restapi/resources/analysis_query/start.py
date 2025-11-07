from typing import NotRequired, TypedDict

from adsdatahub.restapi.schemas.query_execution_spec import QueryExecutionSpecRequest


class AnalysisQueryStartRequestBody(TypedDict):
    spec: QueryExecutionSpecRequest
    """
    クエリ実行パラメータを定義します。
    """

    destTable: str
    """
    'project.dataset.table_name' 形式のクエリ結果の宛先 BigQuery テーブル。

    指定するには、お客様の ADH アカウントのプロジェクトを明示的に許可リストに登録する必要があります。
    プロジェクトが指定されていない場合は、指定したお客様のデフォルトのプロジェクトが使用されます。
    プロジェクトもデータセットも指定しない場合、デフォルトのプロジェクトとデータセットが使用されます。
    """

    customerId: NotRequired[int | None]
    """
    （省略可）Ads Data Hub のお客様がクエリを実行します。

    指定しない場合は、デフォルトでクエリを所有する顧客が対象となります。
    """
