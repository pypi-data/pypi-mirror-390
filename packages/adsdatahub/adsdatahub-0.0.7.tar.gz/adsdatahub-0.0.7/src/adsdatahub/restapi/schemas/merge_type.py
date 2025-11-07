from enum import Enum


class MergeType(str, Enum):
    """
    列の結合でサポートされているすべてのオペレーション。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.analysisQueries?hl=ja#MergeType
    """

    MERGE_TYPE_UNSPECIFIED = "MERGE_TYPE_UNSPECIFIED"
    """マージタイプが指定されていません。結合された列の値は NULL になります。"""

    CONSTANT = "CONSTANT"
    """マージされた列の値を、指定された定数に置き換えます。"""

    SUM = "SUM"
    """結合された列の値の合計を取得します。"""
