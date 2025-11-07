import json
from typing import Any, Mapping, TypeVar

import httpx

from adsdatahub.exceptions import (
    AdsDataHubResponseBodyHasError,
    AdsDataHubResponseStatusCodeError,
    AdsDataHubUnavailableError,
    AdsDataHubUnimplementedError,
)
from adsdatahub.restapi.schemas._model import Model

GenericResponseBody = TypeVar("GenericResponseBody", bound=Model)


def convert_json_value(data: Mapping[str, Any], *, model_map: dict[str, type[Model]]):
    return {
        k: (
            (model_map[k].model_validate(v) if isinstance(v, dict) else v).model_dump()
            if k in model_map
            else v
        )
        for k, v in data.items()
    }


def validate_status_code(response: httpx.Response) -> None:
    if response.status_code != 200:
        match response.status_code:
            case 501:
                try:
                    if (
                        response.json().get("error", {}).get("status")
                        == "UNIMPLEMENTED"
                    ):
                        raise AdsDataHubUnimplementedError(response)
                except json.JSONDecodeError:
                    pass

            case 503:
                raise AdsDataHubUnavailableError(response)

        raise AdsDataHubResponseStatusCodeError(response)


def parse_response_body(
    response_body_type: type[GenericResponseBody],
    response: httpx.Response,
) -> GenericResponseBody:
    validate_status_code(response)

    data = response.json()

    if error := data.get("error"):
        raise AdsDataHubResponseBodyHasError(response, error)

    return response_body_type.model_validate(data)


def get_extra_fields(model: Model) -> dict[str, Any]:
    """
    Pydanticモデルにある未定義のフィールドを返却する。
    """

    extras = {}
    for key, value in model:
        if isinstance(value, Model):
            extra = get_extra_fields(value)
            if len(extra):
                extras[key] = extra

    for key, value in (model.__pydantic_extra__ or {}).items():
        if isinstance(value, Model):
            extras[key] = get_extra_fields(value)
        else:
            extras[key] = value

    return extras
