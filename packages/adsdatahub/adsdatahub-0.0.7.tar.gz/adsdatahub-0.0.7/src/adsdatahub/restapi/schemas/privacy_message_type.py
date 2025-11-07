from enum import Enum


class PrivacyMessageType(str, Enum):
    """
    プライバシー メッセージ タイプを列挙する一意のコードです。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/PrivacyMessageType?hl=ja
    """

    PRIVACY_MESSAGE_TYPE_UNSPECIFIED = "PRIVACY_MESSAGE_TYPE_UNSPECIFIED"
    """プライバシー メッセージ コードが指定されていません。"""

    TOUCHPOINT_ANALYSIS_EXCLUSIONS = "TOUCHPOINT_ANALYSIS_EXCLUSIONS"
    """タッチポイントおよび/またはユーザーをタッチポイント分析から除外しました。"""

    MERGE_ROW_NO_DATA_FILTERED = "MERGE_ROW_NO_DATA_FILTERED"
    """このジョブでデータはフィルタリングされませんでした。"""

    MERGE_ROW_DATA_ON_FEW_USERS_FILTERED = "MERGE_ROW_DATA_ON_FEW_USERS_FILTERED"
    """データはフィルタされましたが、含まれるユーザーが少なすぎます。"""

    MERGE_ROW_ONE_ROW_WITH_MANY_USERS_FILTERED = (
        "MERGE_ROW_ONE_ROW_WITH_MANY_USERS_FILTERED"
    )
    """多数のユーザーに関する情報を含む 1 行がフィルタされました。"""

    MERGE_ROW_NO_MERGE_SPEC = "MERGE_ROW_NO_MERGE_SPEC"
    """データはフィルタリングされましたが、マージ行の指定がジョブに対して構成されていないため、マージ行が表示されませんでした。"""

    MERGE_ROW_ADDED = "MERGE_ROW_ADDED"
    """マージ行がジョブ出力に追加されました。"""

    MERGE_ROW_TEMPORARILY_UNAVAILABLE = "MERGE_ROW_TEMPORARILY_UNAVAILABLE"
    """行の統合に関するプライバシー メッセージは、プライバシーに関する考慮事項または抑制された統合行情報がないため、抑制されました。"""

    LARGE_CREDIT_OUTLIER_USERS_FILTERED = "LARGE_CREDIT_OUTLIER_USERS_FILTERED"
    """タッチポイント分析から外れたユーザーを除外した。"""

    PRIVACY_MESSAGE_TEMPORARILY_UNAVAILABLE = "PRIVACY_MESSAGE_TEMPORARILY_UNAVAILABLE"
    """プライバシー上の問題がある、または関連情報が利用できないためにメールが抑制された。"""

    DATA_ACCESS_BUDGET_IS_NEARLY_EXHAUSTED = "DATA_ACCESS_BUDGET_IS_NEARLY_EXHAUSTED"
    """データアクセス予算はほぼなくなりました。"""
