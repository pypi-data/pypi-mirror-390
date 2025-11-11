from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_service import AgentService
from ...models.marketplace_site_agent_services_list_state_item import MarketplaceSiteAgentServicesListStateItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    identity_uuid: Union[Unset, UUID] = UNSET,
    mode: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    state: Union[Unset, list[MarketplaceSiteAgentServicesListStateItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_identity_uuid: Union[Unset, str] = UNSET
    if not isinstance(identity_uuid, Unset):
        json_identity_uuid = str(identity_uuid)
    params["identity_uuid"] = json_identity_uuid

    params["mode"] = mode

    params["page"] = page

    params["page_size"] = page_size

    json_state: Union[Unset, list[int]] = UNSET
    if not isinstance(state, Unset):
        json_state = []
        for state_item_data in state:
            state_item = state_item_data.value
            json_state.append(state_item)

    params["state"] = json_state

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/marketplace-site-agent-services/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["AgentService"]:
    if response.status_code == 404:
        raise errors.UnexpectedStatus(response.status_code, response.content, response.url)
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AgentService.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content, response.url)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["AgentService"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    identity_uuid: Union[Unset, UUID] = UNSET,
    mode: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    state: Union[Unset, list[MarketplaceSiteAgentServicesListStateItem]] = UNSET,
) -> Response[list["AgentService"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        identity_uuid (Union[Unset, UUID]):
        mode (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        state (Union[Unset, list[MarketplaceSiteAgentServicesListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['AgentService']]
    """

    kwargs = _get_kwargs(
        identity_uuid=identity_uuid,
        mode=mode,
        page=page,
        page_size=page_size,
        state=state,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    identity_uuid: Union[Unset, UUID] = UNSET,
    mode: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    state: Union[Unset, list[MarketplaceSiteAgentServicesListStateItem]] = UNSET,
) -> list["AgentService"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        identity_uuid (Union[Unset, UUID]):
        mode (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        state (Union[Unset, list[MarketplaceSiteAgentServicesListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['AgentService']
    """

    return sync_detailed(
        client=client,
        identity_uuid=identity_uuid,
        mode=mode,
        page=page,
        page_size=page_size,
        state=state,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    identity_uuid: Union[Unset, UUID] = UNSET,
    mode: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    state: Union[Unset, list[MarketplaceSiteAgentServicesListStateItem]] = UNSET,
) -> Response[list["AgentService"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        identity_uuid (Union[Unset, UUID]):
        mode (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        state (Union[Unset, list[MarketplaceSiteAgentServicesListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['AgentService']]
    """

    kwargs = _get_kwargs(
        identity_uuid=identity_uuid,
        mode=mode,
        page=page,
        page_size=page_size,
        state=state,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    identity_uuid: Union[Unset, UUID] = UNSET,
    mode: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    state: Union[Unset, list[MarketplaceSiteAgentServicesListStateItem]] = UNSET,
) -> list["AgentService"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        identity_uuid (Union[Unset, UUID]):
        mode (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        state (Union[Unset, list[MarketplaceSiteAgentServicesListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['AgentService']
    """

    return (
        await asyncio_detailed(
            client=client,
            identity_uuid=identity_uuid,
            mode=mode,
            page=page,
            page_size=page_size,
            state=state,
        )
    ).parsed
