from typing import Annotated

import pytest
from adsdatahub.restapi.schemas._model import Model
from adsdatahub.restapi.schemas.destination_table_info import (
    ColumnInfoModel,
    ColumnInfoModelList,
    _serialize_column_info_list,
    _validate_column_info_list,
)
from adsdatahub.restapi.schemas.noise_impact import NoiseImpact
from pydantic import PlainSerializer, PlainValidator


class Data(Model):
    items: Annotated[
        ColumnInfoModelList,
        PlainValidator(_validate_column_info_list),
        PlainSerializer(_serialize_column_info_list),
    ]


class TestColumnInfoList:
    def test_getitem_key(self):
        column_info = ColumnInfoModel.model_validate(
            {"name": "name", "noiseImpact": NoiseImpact.NOT_NOISED}
        )

        data = Data(items=ColumnInfoModelList([column_info]))

        assert data.items["name"] == column_info

        with pytest.raises(KeyError):
            data.items["name2"]

    def test_getitem_index(self):
        column_info = ColumnInfoModel.model_validate(
            {"name": "name", "noiseImpact": NoiseImpact.NOT_NOISED}
        )

        data = Data(items=ColumnInfoModelList([column_info]))

        assert data.items[0] == column_info

        with pytest.raises(IndexError):
            data.items[1]

    def test_get_key(self):
        column_info = ColumnInfoModel.model_validate(
            {"name": "name", "noiseImpact": NoiseImpact.NOT_NOISED}
        )

        data = Data(items=ColumnInfoModelList([column_info]))

        assert data.items.get("name") == column_info
        assert data.items.get("name2") is None

    def test_get_index(self):
        column_info = ColumnInfoModel.model_validate(
            {"name": "name", "noiseImpact": NoiseImpact.NOT_NOISED}
        )

        data = Data(items=ColumnInfoModelList([column_info]))

        assert data.items.get(0) == column_info
        assert data.items.get(1) is None

    def test_validate(self):
        data = Data.model_validate(
            {"items": [{"name": "name", "noiseImpact": NoiseImpact.NOT_NOISED}]}
        )

        assert isinstance(data.items, ColumnInfoModelList)
        assert isinstance(data.items[0], ColumnInfoModel)

    def test_model_dump(self):
        column_info = ColumnInfoModel.model_validate(
            {"name": "name", "noiseImpact": NoiseImpact.NOT_NOISED}
        )

        assert Data(items=ColumnInfoModelList([column_info])).model_dump()

    def test_model_dump_json(self):
        column_info = ColumnInfoModel.model_validate(
            {"name": "name", "noiseImpact": NoiseImpact.NOT_NOISED}
        )

        assert Data(items=ColumnInfoModelList([column_info])).model_dump_json()
