import os
from typing import TYPE_CHECKING, Any, TypedDict, Union

import google.api_core.client_info
import google.api_core.client_options
import google.api_core.exceptions
import google.auth.credentials
import google.auth.transport.requests
from google.auth import environment_vars
from google.auth.credentials import AnonymousCredentials, Credentials
from google.cloud.client import ClientWithProject
from typing_extensions import Unpack, override

from .client import Client

if TYPE_CHECKING:
    import adsdatahub.restapi.http

_marker: object = object()


ADSDATAHUB_EMULATOR_ENV_VAR = "ADSDATAHUB_EMULATOR_HOST"
"""Environment variable defining host for Ads Data Hub emulator."""

_API_ENDPOINT_OVERRIDE_ENV_VAR = "API_ENDPOINT_OVERRIDE"
"""This is an experimental configuration variable. Use api_endpoint instead."""

_DEFAULT_ADSDATAHUB_HOST = os.getenv(
    _API_ENDPOINT_OVERRIDE_ENV_VAR, "https://adsdatahub.googleapis.com"
)


class RealRestApiClientConstructerKwargs(TypedDict, total=False):
    project: str | object | None
    credentials: Credentials | None
    client_info: google.api_core.client_info.ClientInfo | None
    client_options: Union[
        google.api_core.client_options.ClientOptions,
        dict[str, Any],
        None,
    ]
    _http: Any


class RealClient(Client, ClientWithProject):
    SCOPE = ("https://www.googleapis.com/auth/adsdatahub",)

    def __init__(self, **kwargs: Unpack[RealRestApiClientConstructerKwargs]) -> None:
        project = kwargs.pop("project", _marker)
        if project is None:
            no_project = True
            project = "<none>"
        else:
            no_project = False

        if project is _marker:
            project = None

        client_info = kwargs.pop("client_info", None)
        client_options = kwargs.pop("client_options", None)
        credentials = kwargs.pop("credentials", None)
        _http = kwargs.pop("_http", None)

        self._initial_client_info = client_info
        self._initial_client_options = client_options
        self._initial_credentials = credentials

        kw_args: dict[str, Any] = {"client_info": client_info}

        # `api_endpoint` should be only set by the user via `client_options`,
        # or if the _get_storage_host() returns a non-default value (_is_emulator_set).
        # `api_endpoint` plays an important role for mTLS, if it is not set,
        # then mTLS logic will be applied to decide which endpoint will be used.
        storage_host = _get_adsdatahub_host()
        _is_emulator_set = storage_host != _DEFAULT_ADSDATAHUB_HOST
        kw_args["api_endpoint"] = storage_host if _is_emulator_set else None

        if client_options:
            if isinstance(client_options, dict):
                client_options = google.api_core.client_options.from_dict(
                    client_options
                )
            if client_options.api_endpoint:
                api_endpoint = client_options.api_endpoint
                kw_args["api_endpoint"] = api_endpoint

        # If a custom endpoint is set, the client checks for credentials
        # or finds the default credentials based on the current environment.
        # Authentication may be bypassed under certain conditions:
        # (1) STORAGE_EMULATOR_HOST is set (for backwards compatibility), OR
        # (2) use_auth_w_custom_endpoint is set to False.
        if kw_args["api_endpoint"] is not None:
            if _is_emulator_set:
                if credentials is None:
                    credentials = AnonymousCredentials()
                if project is None:
                    project = _get_environ_project()
                if project is None:
                    no_project = True
                    project = "<none>"

        ClientWithProject.__init__(
            self,
            project=project,
            credentials=credentials,
            client_options=client_options,
            _http=_http,
        )

        if _http is None and self._credentials is not None:
            if not self._credentials.valid:  # type: ignore[attr-defined]
                self._credentials.refresh(google.auth.transport.requests.Request())  # type: ignore[attr-defined]

            import adsdatahub.restapi.http

            self._http_internal = adsdatahub.restapi.http.RealClient(
                headers={
                    "Authorization": f"Bearer {self._credentials.token}",  # type: ignore[attr-defined]
                },
                timeout=60,
            )

        if no_project:
            self.project = None

    @property
    @override
    def _http(self) -> "adsdatahub.restapi.http.Client":
        return self._http_internal


def _get_environ_project():
    return os.getenv(
        environment_vars.PROJECT,
        os.getenv(environment_vars.LEGACY_PROJECT),
    )


def _get_adsdatahub_host():
    return os.environ.get(ADSDATAHUB_EMULATOR_ENV_VAR, _DEFAULT_ADSDATAHUB_HOST)
