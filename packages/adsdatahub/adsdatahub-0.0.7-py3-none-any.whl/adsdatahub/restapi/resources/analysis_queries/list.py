from typing import Annotated, NotRequired, TypedDict

from pydantic import Field

from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.analysis_query import AnalysisQueryModel


class AnalysisQueryListQueryParams(TypedDict):
    pageSize: NotRequired[int | None]
    """返される最大アイテム数。0 の場合、サーバーは返されるクエリの数を決定します。"""

    pageToken: NotRequired[str | None]
    """前の呼び出しによって返されたページトークン。次のページの結果を返すために使用されます。"""

    filter: NotRequired[str | None]
    """
    レスポンスをフィルタします。

    次のフィールド / 形式を使用します。

    ```
    name=”customers/271828/analysisQueries/pi314159265359”
    title=”up_and_right”
    queryText="SELECT LN(2.7182818284);"
    queryState="RUNNABLE"
    updateTime>unix_seconds
    updateEmail=”abc@gmail.com”
    createTime>unix_seconds
    createEmail=”abc@gmail.com”
    ```
    """


class AnalysisQueryListResponse(ExtraAllowModel):
    queries: list[AnalysisQueryModel]
    """
    クエリのリスト。
    """

    next_page_token: Annotated[str | None, Field(alias="nextPageToken")] = None
    """
    次の結果ページのリクエストに使用できるトークン。

    他に結果がない場合、このフィールドは空です。
    """
