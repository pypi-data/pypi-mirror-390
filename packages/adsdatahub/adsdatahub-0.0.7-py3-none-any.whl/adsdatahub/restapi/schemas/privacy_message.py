from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.privacy_message_type import PrivacyMessageType


class PrivacyMessageModel(ExtraAllowModel):
    """
    プライバシー関連の情報、または警告メッセージ。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/PrivacyMessage?hl=ja
    """

    type: PrivacyMessageType
    """メッセージのタイプ。"""

    details: str
    """メッセージのテキスト。"""
