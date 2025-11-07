import datetime
from typing import assert_never

from adsdatahub.restapi.schemas.field_type import (
    ArrayTypeDict,
    FieldTypeDict,
    TypeDict,
)
from adsdatahub.restapi.schemas.parameter_type import (
    ParameterTypeDict,
)
from adsdatahub.restapi.schemas.parameter_value import (
    ArrayValueDict,
    ArrayValueValuesDict,
    ParameterValueDict,
    ValueDict,
)

PrimitivePythonParameter = (
    str
    | int
    | float
    | bool
    | datetime.date
    | datetime.datetime
    | list["PrimitivePythonParameter"]
)


def convert_primitive_parameter_types(
    params: dict[str, PrimitivePythonParameter],
) -> dict[str, ParameterTypeDict]:
    return {
        key: ParameterTypeDict({"type": convert_primitive_parameter_type(value)})
        for key, value in params.items()
    }


def convert_primitive_parameter_values(
    params: dict[str, PrimitivePythonParameter],
) -> dict[str, ParameterValueDict]:
    return {
        key: convert_primitive_parameter_value(value) for key, value in params.items()
    }


def convert_primitive_parameter_type(
    value: PrimitivePythonParameter,
) -> FieldTypeDict:
    match value:
        case str():
            return TypeDict({"type": "STRING"})

        case int():
            return TypeDict({"type": "INT64"})

        case float():
            return TypeDict({"type": "FLOAT64"})

        case bool():
            return TypeDict({"type": "BOOL"})

        case datetime.date():
            return TypeDict({"type": "DATE"})

        case datetime.datetime():
            return TypeDict({"type": "TIMESTAMP"})

        case list():
            return ArrayTypeDict(
                {
                    "arrayType": convert_primitive_parameter_type(
                        # NOTE: 配列の要素が空の場合は、型を推測できないため、文字列を仮に入れる。
                        #       クエリ文の側でパラメータの型が明確である場合、文字列は自動で変換処理されるため、最も安全な選択肢となる。
                        value[0] if len(value) > 0 else "STRING"
                    )
                }
            )

        case _ as unreachable:
            assert_never(unreachable)


def convert_primitive_parameter_value(
    value: PrimitivePythonParameter,
) -> ParameterValueDict:
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
                        {
                            "values": [
                                convert_primitive_parameter_value(v) for v in value
                            ]
                        }
                    )
                }
            )

        case _ as unreachable:
            assert_never(unreachable)
