import datetime
from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_processor import AgentProcessor
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    backend_type: Union[Unset, str] = UNSET,
    backend_version: Union[Unset, str] = UNSET,
    last_run: Union[Unset, datetime.datetime] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    service_uuid: Union[Unset, UUID] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["backend_type"] = backend_type

    params["backend_version"] = backend_version

    json_last_run: Union[Unset, str] = UNSET
    if not isinstance(last_run, Unset):
        json_last_run = last_run.isoformat()
    params["last_run"] = json_last_run

    params["page"] = page

    params["page_size"] = page_size

    json_service_uuid: Union[Unset, str] = UNSET
    if not isinstance(service_uuid, Unset):
        json_service_uuid = str(service_uuid)
    params["service_uuid"] = json_service_uuid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/marketplace-site-agent-processors/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["AgentProcessor"]:
    if response.status_code == 404:
        raise errors.UnexpectedStatus(response.status_code, response.content, response.url)
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AgentProcessor.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content, response.url)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["AgentProcessor"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    backend_type: Union[Unset, str] = UNSET,
    backend_version: Union[Unset, str] = UNSET,
    last_run: Union[Unset, datetime.datetime] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    service_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["AgentProcessor"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_type (Union[Unset, str]):
        backend_version (Union[Unset, str]):
        last_run (Union[Unset, datetime.datetime]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        service_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['AgentProcessor']]
    """

    kwargs = _get_kwargs(
        backend_type=backend_type,
        backend_version=backend_version,
        last_run=last_run,
        page=page,
        page_size=page_size,
        service_uuid=service_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    backend_type: Union[Unset, str] = UNSET,
    backend_version: Union[Unset, str] = UNSET,
    last_run: Union[Unset, datetime.datetime] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    service_uuid: Union[Unset, UUID] = UNSET,
) -> list["AgentProcessor"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_type (Union[Unset, str]):
        backend_version (Union[Unset, str]):
        last_run (Union[Unset, datetime.datetime]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        service_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['AgentProcessor']
    """

    return sync_detailed(
        client=client,
        backend_type=backend_type,
        backend_version=backend_version,
        last_run=last_run,
        page=page,
        page_size=page_size,
        service_uuid=service_uuid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    backend_type: Union[Unset, str] = UNSET,
    backend_version: Union[Unset, str] = UNSET,
    last_run: Union[Unset, datetime.datetime] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    service_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["AgentProcessor"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_type (Union[Unset, str]):
        backend_version (Union[Unset, str]):
        last_run (Union[Unset, datetime.datetime]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        service_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['AgentProcessor']]
    """

    kwargs = _get_kwargs(
        backend_type=backend_type,
        backend_version=backend_version,
        last_run=last_run,
        page=page,
        page_size=page_size,
        service_uuid=service_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    backend_type: Union[Unset, str] = UNSET,
    backend_version: Union[Unset, str] = UNSET,
    last_run: Union[Unset, datetime.datetime] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    service_uuid: Union[Unset, UUID] = UNSET,
) -> list["AgentProcessor"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_type (Union[Unset, str]):
        backend_version (Union[Unset, str]):
        last_run (Union[Unset, datetime.datetime]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        service_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['AgentProcessor']
    """

    return (
        await asyncio_detailed(
            client=client,
            backend_type=backend_type,
            backend_version=backend_version,
            last_run=last_run,
            page=page,
            page_size=page_size,
            service_uuid=service_uuid,
        )
    ).parsed
