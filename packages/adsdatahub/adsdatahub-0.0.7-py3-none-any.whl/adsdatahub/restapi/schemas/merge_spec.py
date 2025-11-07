from typing import Annotated

from pydantic import Field
from typing_extensions import TypedDict

from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.merge_column import MergeColumnDict, MergeColumnModel


class MergeSpecDict(TypedDict):
    columns: dict[str, MergeColumnDict]


class MergeSpecModel(ExtraAllowModel):
    columns: Annotated[dict[str, MergeColumnModel], Field(default_factory=dict)]
