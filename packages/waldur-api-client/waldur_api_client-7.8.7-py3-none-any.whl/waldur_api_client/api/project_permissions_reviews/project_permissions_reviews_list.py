import datetime
from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project_permission_review import ProjectPermissionReview
from ...models.project_permissions_reviews_list_o_item import ProjectPermissionsReviewsListOItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    closed: Union[Unset, datetime.datetime] = UNSET,
    is_pending: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[ProjectPermissionsReviewsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    reviewer_uuid: Union[Unset, UUID] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_closed: Union[Unset, str] = UNSET
    if not isinstance(closed, Unset):
        json_closed = closed.isoformat()
    params["closed"] = json_closed

    params["is_pending"] = is_pending

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["page"] = page

    params["page_size"] = page_size

    json_project_uuid: Union[Unset, str] = UNSET
    if not isinstance(project_uuid, Unset):
        json_project_uuid = str(project_uuid)
    params["project_uuid"] = json_project_uuid

    json_reviewer_uuid: Union[Unset, str] = UNSET
    if not isinstance(reviewer_uuid, Unset):
        json_reviewer_uuid = str(reviewer_uuid)
    params["reviewer_uuid"] = json_reviewer_uuid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/project-permissions-reviews/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["ProjectPermissionReview"]:
    if response.status_code == 404:
        raise errors.UnexpectedStatus(response.status_code, response.content, response.url)
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ProjectPermissionReview.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content, response.url)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["ProjectPermissionReview"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    closed: Union[Unset, datetime.datetime] = UNSET,
    is_pending: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[ProjectPermissionsReviewsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    reviewer_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["ProjectPermissionReview"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        closed (Union[Unset, datetime.datetime]):
        is_pending (Union[Unset, bool]):
        o (Union[Unset, list[ProjectPermissionsReviewsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        reviewer_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ProjectPermissionReview']]
    """

    kwargs = _get_kwargs(
        closed=closed,
        is_pending=is_pending,
        o=o,
        page=page,
        page_size=page_size,
        project_uuid=project_uuid,
        reviewer_uuid=reviewer_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    closed: Union[Unset, datetime.datetime] = UNSET,
    is_pending: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[ProjectPermissionsReviewsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    reviewer_uuid: Union[Unset, UUID] = UNSET,
) -> list["ProjectPermissionReview"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        closed (Union[Unset, datetime.datetime]):
        is_pending (Union[Unset, bool]):
        o (Union[Unset, list[ProjectPermissionsReviewsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        reviewer_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ProjectPermissionReview']
    """

    return sync_detailed(
        client=client,
        closed=closed,
        is_pending=is_pending,
        o=o,
        page=page,
        page_size=page_size,
        project_uuid=project_uuid,
        reviewer_uuid=reviewer_uuid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    closed: Union[Unset, datetime.datetime] = UNSET,
    is_pending: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[ProjectPermissionsReviewsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    reviewer_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["ProjectPermissionReview"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        closed (Union[Unset, datetime.datetime]):
        is_pending (Union[Unset, bool]):
        o (Union[Unset, list[ProjectPermissionsReviewsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        reviewer_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ProjectPermissionReview']]
    """

    kwargs = _get_kwargs(
        closed=closed,
        is_pending=is_pending,
        o=o,
        page=page,
        page_size=page_size,
        project_uuid=project_uuid,
        reviewer_uuid=reviewer_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    closed: Union[Unset, datetime.datetime] = UNSET,
    is_pending: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[ProjectPermissionsReviewsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    reviewer_uuid: Union[Unset, UUID] = UNSET,
) -> list["ProjectPermissionReview"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        closed (Union[Unset, datetime.datetime]):
        is_pending (Union[Unset, bool]):
        o (Union[Unset, list[ProjectPermissionsReviewsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        reviewer_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ProjectPermissionReview']
    """

    return (
        await asyncio_detailed(
            client=client,
            closed=closed,
            is_pending=is_pending,
            o=o,
            page=page,
            page_size=page_size,
            project_uuid=project_uuid,
            reviewer_uuid=reviewer_uuid,
        )
    ).parsed
