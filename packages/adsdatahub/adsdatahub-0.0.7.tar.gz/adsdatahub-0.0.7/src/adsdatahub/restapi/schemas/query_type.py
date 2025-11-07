from enum import Enum


class QueryType(str, Enum):
    """
    クエリのタイプ。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.tempTables?hl=ja#QueryType
    """

    QUERY_TYPE_UNSPECIFIED = "QUERY_TYPE_UNSPECIFIED"
    """クエリの種類が指定されていません。"""

    ANALYSIS = "ANALYSIS"
    """AnalysisQuery。"""

    USER_LIST = "USER_LIST"
    """UserListQuery。"""

    SPECIAL_ENDPOINT = "SPECIAL_ENDPOINT"
    """特殊なエンドポイントによってトリガーされたクエリ。"""
