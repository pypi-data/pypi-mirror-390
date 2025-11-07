from typing_extensions import Literal, TypedDict


class TypeDict(TypedDict):
    # See: https://developers.google.com/ads-data-hub/marketers/guides/run-queries?hl=ja#parameter_types
    type: Literal[
        "INT64",
        "FLOAT64",
        "BOOL",
        "STRING",
        "DATE",
        "TIMESTAMP",
    ]


class ArrayTypeDict(TypedDict):
    arrayType: "FieldTypeDict"


class StructTypeDict(TypedDict):
    structType: list["StructFieldDict"]


class StructFieldDict(TypedDict):
    fieldName: str
    fieldType: "FieldTypeDict"


FieldTypeDict = TypeDict | ArrayTypeDict | StructTypeDict
"""
BigQuery のフィールド タイプを定義します。

Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/FieldType?hl=ja
"""


class TypeModel(TypedDict):
    # See: https://developers.google.com/ads-data-hub/marketers/guides/run-queries?hl=ja#parameter_types
    type: Literal[
        "INT64",
        "FLOAT64",
        "BOOL",
        "STRING",
        "DATE",
        "TIMESTAMP",
    ]


class ArrayTypeModel(TypedDict):
    arrayType: "FieldTypeModel"


class StructTypeModel(TypedDict):
    structType: list["StructFieldModel"]


class StructFieldModel(TypedDict):
    fieldName: str
    fieldType: "FieldTypeModel"


FieldTypeModel = TypeModel | ArrayTypeModel | StructTypeModel

FieldType = FieldTypeDict | FieldTypeModel
