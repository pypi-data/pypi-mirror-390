from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.proposal_protected_calls_add_user_response_400 import ProposalProtectedCallsAddUserResponse400
from ...models.user_role_create_request import UserRoleCreateRequest
from ...models.user_role_expiration_time import UserRoleExpirationTime
from ...types import Response


def _get_kwargs(
    uuid: UUID,
    *,
    body: UserRoleCreateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/proposal-protected-calls/{uuid}/add_user/",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[ProposalProtectedCallsAddUserResponse400, UserRoleExpirationTime]:
    if response.status_code == 404:
        raise errors.UnexpectedStatus(response.status_code, response.content, response.url)
    if response.status_code == 201:
        response_201 = UserRoleExpirationTime.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = ProposalProtectedCallsAddUserResponse400.from_dict(response.json())

        return response_400
    raise errors.UnexpectedStatus(response.status_code, response.content, response.url)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ProposalProtectedCallsAddUserResponse400, UserRoleExpirationTime]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: UserRoleCreateRequest,
) -> Response[Union[ProposalProtectedCallsAddUserResponse400, UserRoleExpirationTime]]:
    """
    Args:
        uuid (UUID):
        body (UserRoleCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ProposalProtectedCallsAddUserResponse400, UserRoleExpirationTime]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: UserRoleCreateRequest,
) -> Union[ProposalProtectedCallsAddUserResponse400, UserRoleExpirationTime]:
    """
    Args:
        uuid (UUID):
        body (UserRoleCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ProposalProtectedCallsAddUserResponse400, UserRoleExpirationTime]
    """

    return sync_detailed(
        uuid=uuid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: UserRoleCreateRequest,
) -> Response[Union[ProposalProtectedCallsAddUserResponse400, UserRoleExpirationTime]]:
    """
    Args:
        uuid (UUID):
        body (UserRoleCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ProposalProtectedCallsAddUserResponse400, UserRoleExpirationTime]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: UserRoleCreateRequest,
) -> Union[ProposalProtectedCallsAddUserResponse400, UserRoleExpirationTime]:
    """
    Args:
        uuid (UUID):
        body (UserRoleCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ProposalProtectedCallsAddUserResponse400, UserRoleExpirationTime]
    """

    return (
        await asyncio_detailed(
            uuid=uuid,
            client=client,
            body=body,
        )
    ).parsed
