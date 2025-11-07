from typing import Annotated

from pydantic import Field

from adsdatahub.restapi.schemas._model import ExtraAllowModel


class QueryPerformanceInfoModel(ExtraAllowModel):
    """
    クエリ実行のパフォーマンス情報。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/QueryPerformanceInfo?hl=ja
    """

    zero_mb: Annotated[bool, Field(alias="zeroMb")] = False
    """
    処理されたデータが 0 バイトの場合は true。
    """

    less_than_one_mb: Annotated[bool, Field(alias="lessThanOneMb")] = False
    """
    処理されたデータが 1 MiB 未満の場合は true。
    """

    processed_mb: Annotated[int | None, Field(alias="processedMb")] = None
    """
    このクエリで読み取られる MiB データ。
    データサイズが 1 MiB 以上の場合に設定します。-1 は、このクエリで処理されたバイト数をフェッチできなかったことを意味します。
    """
