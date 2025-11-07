from pydantic import BaseModel

from adsdatahub.client.parameters.primitive_parameters import (
    PrimitivePythonParameter,
    convert_primitive_parameter_types,
    convert_primitive_parameter_values,
)
from adsdatahub.client.parameters.pydantic_parameters import (
    convert_pydantic_parameter_types,
    convert_pydantic_parameter_values,
)
from adsdatahub.restapi.schemas.parameter_type import ParameterTypeDict
from adsdatahub.restapi.schemas.parameter_value import ParameterValueDict

# TODO: 配列の型、デフォルト値などをサポートする必要があるが、後回し。
#
# TODO: デフォルト値や NULL のサポートをするためには、 dataclass や pydantic を利用する必要がある。
#
# NOTE: ドキュメントの記載は一貫性がない。
#       1. STRING または INT64 のプリミティブ型に加えて、配列と構造体をサポートしているように見える。
#          https://developers.google.com/ads-data-hub/reference/rest/v1/FieldType?hl=ja
#
#       2. AdsDataHub のコンソールからはさらに多くのパラメータの型を扱うことができるようだ。
#          https://developers.google.com/ads-data-hub/guides/run-queries?hl=ja#parameter_types
#
PythonParameter = PrimitivePythonParameter
"""
クエリのパラメータとして使える Python の型。
"""


def convert_parameter_types(
    parameter: dict[str, PrimitivePythonParameter] | BaseModel,
) -> dict[str, ParameterTypeDict]:
    if isinstance(parameter, BaseModel):
        return convert_pydantic_parameter_types(parameter)

    else:
        return convert_primitive_parameter_types(parameter)


def convert_parameter_values(
    parameter: dict[str, PrimitivePythonParameter] | BaseModel,
) -> dict[str, ParameterValueDict]:
    if isinstance(parameter, BaseModel):
        return convert_pydantic_parameter_values(parameter)

    else:
        return convert_primitive_parameter_values(parameter)
