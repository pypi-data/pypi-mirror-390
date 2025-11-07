from collections import UserList
from typing import Annotated

from pydantic import Field, PlainSerializer, PlainValidator

from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.column_info import ColumnInfoModel
from adsdatahub.restapi.schemas.table_noise_impact import TableNoiseImpact


class ColumnInfoModelList(UserList[ColumnInfoModel]):
    def __getitem__(self, key: int | str) -> ColumnInfoModel:  # type: ignore[override]
        if isinstance(key, int):
            return super().__getitem__(key)

        else:
            if column := self.get(key):
                return column
            raise KeyError(f"Column not found: {key}")

    def get(
        self, key: int | str, default: ColumnInfoModel | None = None
    ) -> ColumnInfoModel | None:
        if isinstance(key, int):
            if len(self) > key:
                return self[key]

            else:
                return default

        else:
            for column in self:
                if column.name == key:
                    return column

            else:
                return default


def _validate_column_info_list(value: list[ColumnInfoModel]) -> ColumnInfoModelList:
    return ColumnInfoModelList(
        [ColumnInfoModel.model_validate(model) for model in value]
    )


def _serialize_column_info_list(value: ColumnInfoModelList):
    return [v for v in value]


class DestinationTableInfoModel(ExtraAllowModel):
    """
    Metadata of an exported query output table.

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/DestinationTableInfo
    """

    table_path: Annotated[str, Field(alias="tablePath")]
    """
    Table path in the customer BigQuery project.
    """

    row_count: Annotated[int, Field(alias="rowCount")] = 0
    """
    Number of rows in the result.
    """

    columns: Annotated[
        ColumnInfoModelList,
        Field(default_factory=list),
        PlainValidator(_validate_column_info_list),
        PlainSerializer(_serialize_column_info_list),
    ]
    """
    Information about columns in result.
    """

    noise_impact: Annotated[TableNoiseImpact, Field(alias="noiseImpact")]
    """
    The noise impact message for this table.
    """

    impact_percentage: Annotated[float | None, Field(alias="impactPercentage")] = None
    """
    If applicable, the percent of cells in this table which are not greatly affected by noise.
    """
