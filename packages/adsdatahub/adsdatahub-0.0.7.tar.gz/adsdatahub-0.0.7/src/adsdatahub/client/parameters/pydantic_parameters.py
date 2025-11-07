import datetime
from types import NoneType, UnionType
from typing import Any, List, Union, assert_never, get_args, get_origin

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from adsdatahub.restapi.schemas.field_type import ArrayTypeDict, FieldTypeDict, TypeDict
from adsdatahub.restapi.schemas.parameter_type import ParameterTypeDict
from adsdatahub.restapi.schemas.parameter_value import (
    ArrayValueDict,
    ArrayValueValuesDict,
    ParameterValueDict,
    ValueDict,
)


def convert_pydantic_parameter_types(params: BaseModel) -> dict[str, ParameterTypeDict]:
    return {
        name: _convert_parameter_type(
            convert_pydantic_parameter_type(field_info.annotation),
            field_info.description,
            field_info.get_default(call_default_factory=True),
        )
        for name, field_info in params.model_fields.items()
    }


def _convert_parameter_type(
    field_type: FieldTypeDict,
    description: str | None,
    default_value: Any,
) -> ParameterTypeDict:
    parameter_type: ParameterTypeDict = {"type": field_type}

    if description is not None:
        parameter_type["description"] = description

    if default_value is not PydanticUndefined:
        parameter_type["defaultValue"] = convert_pydantic_parameter_value(default_value)

    return parameter_type


def convert_pydantic_parameter_values(
    params: BaseModel,
) -> dict[str, ParameterValueDict]:
    return {key: convert_pydantic_parameter_value(value) for key, value in params}


def convert_pydantic_parameter_type(field_type: type | None) -> FieldTypeDict:
    if field_type is None:
        raise TypeError("Field annotation cannot be None")

    origin_type = get_origin(field_type)
    if origin_type is None:
        if issubclass(field_type, bool):
            return TypeDict({"type": "BOOL"})

        elif issubclass(field_type, str):
            return TypeDict({"type": "STRING"})

        elif issubclass(field_type, int):
            return TypeDict({"type": "INT64"})

        elif issubclass(field_type, float):
            return TypeDict({"type": "FLOAT64"})

        elif issubclass(field_type, datetime.datetime):
            return TypeDict({"type": "TIMESTAMP"})

        elif issubclass(field_type, datetime.date):
            return TypeDict({"type": "DATE"})

    elif origin_type is list or origin_type is List:
        element_type = get_args(field_type)[0]
        return ArrayTypeDict(
            {"arrayType": convert_pydantic_parameter_type(element_type)}
        )

    elif origin_type is UnionType or origin_type is Union:
        element_types = get_args(field_type)
        for element_type in element_types:
            if element_type is NoneType:
                continue
            return convert_pydantic_parameter_type(element_type)

    raise TypeError(f"Unsupported type: {field_type}")


def convert_pydantic_parameter_value(value: Any) -> ParameterValueDict:
    if value is None:
        # NOTE: nullを渡す方法がわかっていません。
        #       値フィールドにnullを渡すと、次のようなエラーになることはわかっています。
        #
        #      ```json
        #      {"code": 3, "message": "Value for parameter \"value\" not given and no default value found. (Error 0410)"}
        #      ```
        #
        # See: https://developers.google.com/ads-data-hub/reference/rest/v1/FieldType?hl=ja

        raise NotImplementedError("null is not supported yet.")

    match value:
        case str():
            return ValueDict({"value": value})

        case bool():
            return ValueDict({"value": str(value).upper()})

        case int() | float():
            return ValueDict({"value": str(value)})

        case datetime.date() | datetime.datetime():
            return ValueDict({"value": value.isoformat()})

        case list():
            return ArrayValueDict(
                {
                    "arrayValue": ArrayValueValuesDict(
                        {"values": [convert_pydantic_parameter_value(v) for v in value]}
                    )
                }
            )

        case _ as unreachable:
            assert_never(unreachable)
