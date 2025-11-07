import datetime
from typing import NotRequired, TypedDict


class OperationWaitRequestBody(TypedDict):
    """
    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/operations/wait?hl=ja#request-body
    """

    timeout: NotRequired[datetime.timedelta | str | int | float | None]
    """
    タイムアウトするまでの最大待機時間。

    空白のままにした場合、待機時間は基になる HTTP/RPC プロトコルによって許可される最長の時間になります。
    RPC コンテキストの期限も指定されている場合は、短い方が使用されます。

    小数点以下 9 桁まで、「s」で終わる秒単位の期間（例: "3.5s"）。
    """
