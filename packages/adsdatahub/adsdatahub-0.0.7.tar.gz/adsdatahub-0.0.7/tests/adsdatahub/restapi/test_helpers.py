import pytest
from adsdatahub import _helpers as helpers
from adsdatahub.restapi.schemas._model import ExtraAllowModel


class TestGetExtraFields:
    @pytest.mark.parametrize(
        "data, expected",
        [
            ({"a": 1}, {}),
            ({"a": 1, "b": "text"}, {}),
            ({"a": 1, "b": "text", "c": "extra"}, {"c": "extra"}),
        ],
    )
    def test_simple_model(self, data, expected):
        class Data(ExtraAllowModel):
            a: int
            b: str | None = None

        assert helpers.get_extra_fields(Data.model_validate(data)) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ({"a": 1}, {}),
            ({"a": 1, "c": "extra"}, {"c": "extra"}),
            ({"a": 1, "b": {"c": "nested"}}, {}),
            ({"a": 1, "b": {"c": "nested", "d": "extra"}}, {"b": {"d": "extra"}}),
            (
                {"a": 1, "b": {"c": "nested", "d": "extra"}, "c": 12},
                {"b": {"d": "extra"}, "c": 12},
            ),
        ],
    )
    def test_nested_model(self, data, expected):
        class Nested(ExtraAllowModel):
            c: str

        class Data(ExtraAllowModel):
            a: int
            b: Nested | None = None

        assert helpers.get_extra_fields(Data.model_validate(data)) == expected
