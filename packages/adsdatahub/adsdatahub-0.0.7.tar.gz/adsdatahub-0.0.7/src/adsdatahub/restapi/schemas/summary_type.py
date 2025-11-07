from enum import Enum


class SummaryType(str, Enum):
    """
    概要の種類。

    列の結合でサポートされているすべてのオペレーション。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.analysisQueries?hl=ja#SummaryType
    """

    SUMMARY_TYPE_UNSPECIFIED = "SUMMARY_TYPE_UNSPECIFIED"
    """サマリータイプが指定されていません。概要列の値は NULL になります。"""

    CONSTANT = "CONSTANT"
    """マージされた列の値を、指定された定数に置き換えます。"""
    SUM = "SUM"
    """結合された列の値の合計を取得します。"""
