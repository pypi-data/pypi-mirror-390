import datetime
from typing import Annotated

from pydantic import Field, field_serializer
from typing_extensions import NotRequired, TypedDict

from adsdatahub.restapi.schemas._model import ExtraAllowModel, ExtraForbidModel
from adsdatahub.restapi.schemas.date import DateDict, DateModel
from adsdatahub.restapi.schemas.parameter_value import (
    ParameterValueDict,
    ParameterValueModel,
)


class QueryExecutionSpecRequestDict(TypedDict):
    """クエリ実行パラメータを定義します。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/QueryExecutionSpec?hl=ja
    """

    adsDataCustomerId: NotRequired[str | None]
    """
    クエリで使用されている広告データを所有している、
    リンクされた Ads Data Hub お客様 ID。
    指定されていない場合、クエリは、Ads Data Hub ユーザーが所有する広告データを使用して実行されます。
    """

    matchDataCustomerId: NotRequired[str | None]
    """
    クエリの一致データを所有している、リンクされた Ads Data Hub お客様 ID。
    指定されていない場合、クエリは、該当する場合は Ads Data Hub お客様 ID が所有するマッチデータを使用して実行されます。
    """

    # TODO: converter
    startDate: DateDict | datetime.date | str
    """クエリの開始日（この日付を含む）。"""

    # TODO: converter
    endDate: DateDict | datetime.date | str
    """クエリの終了日（その日を含む）。"""

    timeZone: NotRequired[str | None]
    """クエリの開始日と終了日のタイムゾーン。指定しない場合、デフォルトは 'UTC' です。"""

    parameterValues: NotRequired[dict[str, ParameterValueDict] | None]
    """クエリで想定されるその他のパラメータ。各パラメータ名をそのバインドされた値にマッピングします。"""

    jobId: NotRequired[str | None]
    """
    クエリ オペレーションのジョブ ID。
    結果として得られるオペレーションは、"operations/[jobId]" という名前になります（例: "operations/job_123"）。
    同じジョブ ID のオペレーションがすでに存在する場合は、エラーが発生します。
    指定されていない場合、サーバーによってジョブ ID が生成されます。
    """


class QueryExecutionSpecRequestModel(ExtraForbidModel):
    ads_data_customer_id: Annotated[str | None, Field(alias="adsDataCustomerId")] = None
    match_data_customer_id: Annotated[
        str | None, Field(alias="matchDataCustomerId")
    ] = None
    start_date: Annotated[DateModel | datetime.date | str, Field(alias="startDate")]
    end_date: Annotated[DateModel | datetime.date | str, Field(alias="endDate")]
    time_zone: Annotated[str | None, Field(alias="timeZone")] = None
    parameter_values: Annotated[
        dict[str, ParameterValueModel],
        Field(alias="parameterValues", default_factory=dict),
    ]
    job_id: Annotated[str | None, Field(alias="jobId")] = None

    @field_serializer("start_date", "end_date")
    def serialize_dt(self, date: DateModel | datetime.date | str) -> DateDict:
        if isinstance(date, str):
            date = datetime.date.fromisoformat(date)

        if isinstance(date, datetime.date):
            return DateDict(year=date.year, month=date.month, day=date.day)

        else:
            return DateDict(year=date.year, month=date.month, day=date.day)


class QueryExecutionSpecModel(ExtraAllowModel):
    adsDataCustomerId: str
    matchDataCustomerId: str
    startDate: DateModel
    endDate: DateModel
    timeZone: str
    parameterValues: dict[str, ParameterValueModel]
    jobId: str


QueryExecutionSpecRequest = (
    QueryExecutionSpecRequestDict | QueryExecutionSpecRequestModel
)
