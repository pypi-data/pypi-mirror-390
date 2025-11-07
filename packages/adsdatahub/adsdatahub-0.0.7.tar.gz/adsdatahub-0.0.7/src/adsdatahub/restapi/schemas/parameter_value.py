from typing_extensions import TypedDict

from adsdatahub.restapi.schemas._model import ExtraForbidModel


class ValueDict(TypedDict):
    value: str


class ArrayValueDict(TypedDict):
    arrayValue: "ArrayValueValuesDict"


class ArrayValueValuesDict(TypedDict):
    values: list["ParameterValueDict"]


class StructValueDict(TypedDict):
    structValue: "StructValueValuesDict"


class StructValueValuesDict(TypedDict):
    values: dict[str, "ParameterValueDict"]


ParameterValueDict = ValueDict | ArrayValueDict | StructValueDict


class ValueModel(ExtraForbidModel):
    value: str


class ArrayValueModel(ExtraForbidModel):
    arrayValue: "ArrayValueValuesModel"


class ArrayValueValuesModel(ExtraForbidModel):
    values: list["ParameterValueModel"]


class StructValueModel(ExtraForbidModel):
    structValue: "StructValueValuesModel"


class StructValueValuesModel(ExtraForbidModel):
    values: dict[str, "ParameterValueModel"]


ParameterValueModel = ValueModel | ArrayValueModel | StructValueModel
