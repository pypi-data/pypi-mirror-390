from enum import Enum


class ShareType(str, Enum):
    """
    サポートされているクエリ共有のタイプ。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/QueryShare?hl=ja
    """

    SHARE_TYPE_UNSPECIFIED = "SHARE_TYPE_UNSPECIFIED"
    """クエリの共有タイプが指定されていません。"""

    MANAGED_CUSTOMERS = "MANAGED_CUSTOMERS"
    """クエリは、Ads Data Hub ユーザー、またはお客様が管理している Ads Data Hub ユーザーのどちらからでも実行できます。"""
