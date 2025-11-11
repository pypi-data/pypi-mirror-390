import datetime
from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_identity import AgentIdentity
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    last_restarted: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    version: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_last_restarted: Union[Unset, str] = UNSET
    if not isinstance(last_restarted, Unset):
        json_last_restarted = last_restarted.isoformat()
    params["last_restarted"] = json_last_restarted

    params["name"] = name

    json_offering_uuid: Union[Unset, str] = UNSET
    if not isinstance(offering_uuid, Unset):
        json_offering_uuid = str(offering_uuid)
    params["offering_uuid"] = json_offering_uuid

    params["page"] = page

    params["page_size"] = page_size

    params["version"] = version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/marketplace-site-agent-identities/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["AgentIdentity"]:
    if response.status_code == 404:
        raise errors.UnexpectedStatus(response.status_code, response.content, response.url)
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AgentIdentity.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content, response.url)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["AgentIdentity"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    last_restarted: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    version: Union[Unset, str] = UNSET,
) -> Response[list["AgentIdentity"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        last_restarted (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['AgentIdentity']]
    """

    kwargs = _get_kwargs(
        last_restarted=last_restarted,
        name=name,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        version=version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    last_restarted: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    version: Union[Unset, str] = UNSET,
) -> list["AgentIdentity"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        last_restarted (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['AgentIdentity']
    """

    return sync_detailed(
        client=client,
        last_restarted=last_restarted,
        name=name,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        version=version,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    last_restarted: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    version: Union[Unset, str] = UNSET,
) -> Response[list["AgentIdentity"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        last_restarted (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['AgentIdentity']]
    """

    kwargs = _get_kwargs(
        last_restarted=last_restarted,
        name=name,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        version=version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    last_restarted: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    version: Union[Unset, str] = UNSET,
) -> list["AgentIdentity"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        last_restarted (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['AgentIdentity']
    """

    return (
        await asyncio_detailed(
            client=client,
            last_restarted=last_restarted,
            name=name,
            offering_uuid=offering_uuid,
            page=page,
            page_size=page_size,
            version=version,
        )
    ).parsed
