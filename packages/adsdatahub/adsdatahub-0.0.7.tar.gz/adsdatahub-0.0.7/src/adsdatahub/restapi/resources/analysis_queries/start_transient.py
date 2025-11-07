from typing_extensions import TypedDict

from adsdatahub.restapi.schemas.analysis_query import AnalysisQueryOptionalTitleRequest
from adsdatahub.restapi.schemas.query_execution_spec import QueryExecutionSpecRequest


class AnalysisQueriesStartTransientQueryParams(TypedDict):
    """
    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.analysisQueries/startTransient?hl=ja#request-body
    """

    query: AnalysisQueryOptionalTitleRequest
    """
    実行するクエリ。
    """

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
