from typing import NotRequired

from typing_extensions import TypedDict

from adsdatahub.restapi.schemas._model import ExtraForbidModel

from .field_type import FieldType
from .parameter_value import ParameterValueDict, ParameterValueModel


class ParameterTypeDict(TypedDict):
    """
    特定のクエリ パラメータに関する情報。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/ParameterType?hl=ja
    """

    type: FieldType
    """
    パラメータ フィールドの型。
    """

    description: NotRequired[str | None]
    """
    パラメータの説明。
    """

    defaultValue: NotRequired[ParameterValueDict | None]
    """
    パラメータ値が指定されていない場合に使用する値。
    """


class ParameterTypeModel(ExtraForbidModel):
    type: FieldType
    """
    パラメータ フィールドの型。
    """

    description: str | None = None
    """
    パラメータの説明。
    """

    defaultValue: ParameterValueModel | None = None
    """
    パラメータ値が指定されていない場合に使用する値。
    """


ParameterType = ParameterTypeDict | ParameterTypeModel
