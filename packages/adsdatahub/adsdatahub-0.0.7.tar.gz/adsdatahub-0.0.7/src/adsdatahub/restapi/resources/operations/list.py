from typing import Annotated, NotRequired, TypedDict

from pydantic import Field

from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.analysis_query_metadata import (
    AnalysisQueryMetadataModel,
)
from adsdatahub.restapi.schemas.operation import OperationModel


class OperationsListQueryParams(TypedDict):
    filter: NotRequired[str | None]
    pageSize: NotRequired[int | None]
    pageToken: NotRequired[str | None]


class OperationsListResponseBody(ExtraAllowModel):
    operations: Annotated[
        list[OperationModel[AnalysisQueryMetadataModel]], Field(default_factory=list)
    ]
    """
    リクエストで指定されたフィルタに一致するオペレーションのリスト。
    """

    next_page_token: Annotated[str | None, Field(alias="nextPageToken")] = None
    """
    標準的なリストの次ページのトークン。
    """
