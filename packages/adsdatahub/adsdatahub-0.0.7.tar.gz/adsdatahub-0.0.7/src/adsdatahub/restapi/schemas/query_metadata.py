import datetime
from typing import Annotated

from pydantic import Field

from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.parameter_value import ParameterValueModel


class QueryMetadataBaseModel(ExtraAllowModel):
    """
    クエリ実行ジョブに関するメタデータ。
    これは、クエリ実行リクエストによって返される google.longrunning.Operation のメタデータフィールドに保存されます。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/QueryMetadata?hl=ja
    """

    type: Annotated[str, Field(alias="@type")]
    """
    タイプを識別する URI。
    """

    query_resource_name: Annotated[str | None, Field(alias="queryResourceName")] = None
    """
    実行されたクエリリソースの名前（例: customers/123/analysisQueries/abcd1234）
    格納されているクエリ実行に対してのみ存在します。
    """

    query_title: Annotated[str | None, Field(alias="queryTitle")] = None
    """
    実行されたクエリのタイトル。
    """

    customer_id: Annotated[str, Field(alias="customerId")]
    """
    クエリを実行した Ads Data Hub お客様 ID。
    """

    ads_data_customer_id: Annotated[str, Field(alias="adsDataCustomerId")]
    """
    広告データに使用される Ads Data Hub お客様 ID。
    """

    match_data_customer_id: Annotated[str, Field(alias="matchDataCustomerId")]
    """
    マッチテーブルのデータに使用する Ads Data Hub お客様 ID。
    """

    parameter_values: Annotated[
        dict[str, ParameterValueModel],
        Field(alias="parameterValues", default_factory=dict),
    ]
    start_time: Annotated[datetime.datetime, Field(alias="startTime")]
    """
    クエリ実行の開始時間。

    RFC3339 UTC の Zulu 形式のタイムスタンプ。
    ナノ秒単位で、小数点以下は 9 桁までとなります。
    （例: "2014-10-02T15:01:23Z"、"2014-10-02T15:01:23.045123456Z"）。
    """

    end_time: Annotated[datetime.datetime, Field(alias="endTime")]
    """
    クエリ実行の終了時間。

    RFC3339 UTC の Zulu 形式のタイムスタンプ。
    ナノ秒単位で、小数点以下は 9 桁までとなります。
    （例: "2014-10-02T15:01:23Z"、"2014-10-02T15:01:23.045123456Z"）。
    """

    dest_table: Annotated[str | None, Field(alias="destTable")] = None
    """
    クエリ結果の宛先テーブル。

    分析クエリに使用されます。
    """
