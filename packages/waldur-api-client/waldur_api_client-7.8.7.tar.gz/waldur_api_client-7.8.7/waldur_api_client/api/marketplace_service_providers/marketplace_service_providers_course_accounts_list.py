import datetime
from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.course_account import CourseAccount
from ...models.marketplace_service_providers_course_accounts_list_o_item import (
    MarketplaceServiceProvidersCourseAccountsListOItem,
)
from ...models.marketplace_service_providers_course_accounts_list_state_item import (
    MarketplaceServiceProvidersCourseAccountsListStateItem,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    service_provider_uuid: UUID,
    *,
    email: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_end_date_after: Union[Unset, datetime.date] = UNSET,
    project_end_date_before: Union[Unset, datetime.date] = UNSET,
    project_start_date_after: Union[Unset, datetime.date] = UNSET,
    project_start_date_before: Union[Unset, datetime.date] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListStateItem]] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["email"] = email

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["page"] = page

    params["page_size"] = page_size

    json_project_end_date_after: Union[Unset, str] = UNSET
    if not isinstance(project_end_date_after, Unset):
        json_project_end_date_after = project_end_date_after.isoformat()
    params["project_end_date_after"] = json_project_end_date_after

    json_project_end_date_before: Union[Unset, str] = UNSET
    if not isinstance(project_end_date_before, Unset):
        json_project_end_date_before = project_end_date_before.isoformat()
    params["project_end_date_before"] = json_project_end_date_before

    json_project_start_date_after: Union[Unset, str] = UNSET
    if not isinstance(project_start_date_after, Unset):
        json_project_start_date_after = project_start_date_after.isoformat()
    params["project_start_date_after"] = json_project_start_date_after

    json_project_start_date_before: Union[Unset, str] = UNSET
    if not isinstance(project_start_date_before, Unset):
        json_project_start_date_before = project_start_date_before.isoformat()
    params["project_start_date_before"] = json_project_start_date_before

    json_project_uuid: Union[Unset, str] = UNSET
    if not isinstance(project_uuid, Unset):
        json_project_uuid = str(project_uuid)
    params["project_uuid"] = json_project_uuid

    json_state: Union[Unset, list[str]] = UNSET
    if not isinstance(state, Unset):
        json_state = []
        for state_item_data in state:
            state_item = state_item_data.value
            json_state.append(state_item)

    params["state"] = json_state

    params["username"] = username

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/marketplace-service-providers/{service_provider_uuid}/course_accounts/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["CourseAccount"]:
    if response.status_code == 404:
        raise errors.UnexpectedStatus(response.status_code, response.content, response.url)
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CourseAccount.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content, response.url)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["CourseAccount"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    service_provider_uuid: UUID,
    *,
    client: AuthenticatedClient,
    email: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_end_date_after: Union[Unset, datetime.date] = UNSET,
    project_end_date_before: Union[Unset, datetime.date] = UNSET,
    project_start_date_after: Union[Unset, datetime.date] = UNSET,
    project_start_date_before: Union[Unset, datetime.date] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListStateItem]] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> Response[list["CourseAccount"]]:
    """Return course project accounts that have access to resources managed by the provider.

            Checks for:
            - Projects with active service provider's resources
            - Course accounts with non-blank users



    Args:
        service_provider_uuid (UUID):
        email (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_end_date_after (Union[Unset, datetime.date]):
        project_end_date_before (Union[Unset, datetime.date]):
        project_start_date_after (Union[Unset, datetime.date]):
        project_start_date_before (Union[Unset, datetime.date]):
        project_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListStateItem]]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CourseAccount']]
    """

    kwargs = _get_kwargs(
        service_provider_uuid=service_provider_uuid,
        email=email,
        o=o,
        page=page,
        page_size=page_size,
        project_end_date_after=project_end_date_after,
        project_end_date_before=project_end_date_before,
        project_start_date_after=project_start_date_after,
        project_start_date_before=project_start_date_before,
        project_uuid=project_uuid,
        state=state,
        username=username,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    service_provider_uuid: UUID,
    *,
    client: AuthenticatedClient,
    email: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_end_date_after: Union[Unset, datetime.date] = UNSET,
    project_end_date_before: Union[Unset, datetime.date] = UNSET,
    project_start_date_after: Union[Unset, datetime.date] = UNSET,
    project_start_date_before: Union[Unset, datetime.date] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListStateItem]] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> list["CourseAccount"]:
    """Return course project accounts that have access to resources managed by the provider.

            Checks for:
            - Projects with active service provider's resources
            - Course accounts with non-blank users



    Args:
        service_provider_uuid (UUID):
        email (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_end_date_after (Union[Unset, datetime.date]):
        project_end_date_before (Union[Unset, datetime.date]):
        project_start_date_after (Union[Unset, datetime.date]):
        project_start_date_before (Union[Unset, datetime.date]):
        project_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListStateItem]]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CourseAccount']
    """

    return sync_detailed(
        service_provider_uuid=service_provider_uuid,
        client=client,
        email=email,
        o=o,
        page=page,
        page_size=page_size,
        project_end_date_after=project_end_date_after,
        project_end_date_before=project_end_date_before,
        project_start_date_after=project_start_date_after,
        project_start_date_before=project_start_date_before,
        project_uuid=project_uuid,
        state=state,
        username=username,
    ).parsed


async def asyncio_detailed(
    service_provider_uuid: UUID,
    *,
    client: AuthenticatedClient,
    email: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_end_date_after: Union[Unset, datetime.date] = UNSET,
    project_end_date_before: Union[Unset, datetime.date] = UNSET,
    project_start_date_after: Union[Unset, datetime.date] = UNSET,
    project_start_date_before: Union[Unset, datetime.date] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListStateItem]] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> Response[list["CourseAccount"]]:
    """Return course project accounts that have access to resources managed by the provider.

            Checks for:
            - Projects with active service provider's resources
            - Course accounts with non-blank users



    Args:
        service_provider_uuid (UUID):
        email (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_end_date_after (Union[Unset, datetime.date]):
        project_end_date_before (Union[Unset, datetime.date]):
        project_start_date_after (Union[Unset, datetime.date]):
        project_start_date_before (Union[Unset, datetime.date]):
        project_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListStateItem]]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CourseAccount']]
    """

    kwargs = _get_kwargs(
        service_provider_uuid=service_provider_uuid,
        email=email,
        o=o,
        page=page,
        page_size=page_size,
        project_end_date_after=project_end_date_after,
        project_end_date_before=project_end_date_before,
        project_start_date_after=project_start_date_after,
        project_start_date_before=project_start_date_before,
        project_uuid=project_uuid,
        state=state,
        username=username,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    service_provider_uuid: UUID,
    *,
    client: AuthenticatedClient,
    email: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_end_date_after: Union[Unset, datetime.date] = UNSET,
    project_end_date_before: Union[Unset, datetime.date] = UNSET,
    project_start_date_after: Union[Unset, datetime.date] = UNSET,
    project_start_date_before: Union[Unset, datetime.date] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListStateItem]] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> list["CourseAccount"]:
    """Return course project accounts that have access to resources managed by the provider.

            Checks for:
            - Projects with active service provider's resources
            - Course accounts with non-blank users



    Args:
        service_provider_uuid (UUID):
        email (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_end_date_after (Union[Unset, datetime.date]):
        project_end_date_before (Union[Unset, datetime.date]):
        project_start_date_after (Union[Unset, datetime.date]):
        project_start_date_before (Union[Unset, datetime.date]):
        project_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceServiceProvidersCourseAccountsListStateItem]]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CourseAccount']
    """

    return (
        await asyncio_detailed(
            service_provider_uuid=service_provider_uuid,
            client=client,
            email=email,
            o=o,
            page=page,
            page_size=page_size,
            project_end_date_after=project_end_date_after,
            project_end_date_before=project_end_date_before,
            project_start_date_after=project_start_date_after,
            project_start_date_before=project_start_date_before,
            project_uuid=project_uuid,
            state=state,
            username=username,
        )
    ).parsed
