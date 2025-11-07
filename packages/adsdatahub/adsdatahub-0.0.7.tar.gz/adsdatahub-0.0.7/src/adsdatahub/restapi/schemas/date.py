import datetime

from typing_extensions import TypedDict

from adsdatahub.restapi.schemas._model import ExtraForbidModel


class DateDict(TypedDict):
    """
    カレンダーの日付全体または一部（誕生日など）を表します。時間帯とタイムゾーンは他の場所で指定されているか、重要ではありません。日付はグレゴリオ暦に基づき、次のいずれかを表します。

    年、月、日の値が 0 以外の完全な日付。
    年と 0 年の年（記念日など）。
    自ら年（0 か月と 0 日）。
    年と月、ゼロ日（クレジット カードの有効期限など）

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/Date?hl=ja
    """

    year: int
    """日付の年。1 ～ 9999 の範囲で指定するか、年のない日付を指定する場合は 0 にする必要があります。"""

    month: int
    """月。1 ～ 12 の範囲で指定するか、特定の月を指定しない年（0）を指定します。"""

    day: int
    """日。その年と月で有効な値を 1 ～ 31 の範囲で指定するか、0: 1 年のみを指定するか、日付が重要ではない年と月を指定します。"""


class DateModel(ExtraForbidModel):
    year: int
    month: int
    day: int

    def to_date(self) -> datetime.date:
        return datetime.date(self.year, self.month, self.day)
