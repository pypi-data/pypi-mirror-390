from enum import Enum


class QueryState(str, Enum):
    """
    分析クエリの実行モードを決定する状態。

    See https://developers.google.com/ads-data-hub/reference/rest/v1/QueryState?hl=ja
    """

    QUERY_STATE_UNSPECIFIED = "QUERY_STATE_UNSPECIFIED"
    """クエリの状態は指定されていません。"""

    RUNNABLE = "RUNNABLE"
    """クエリはお客様が実行できます。"""

    WHITELISTED = "WHITELISTED"
    """クエリは手動で安全であることが確認されています。"""
