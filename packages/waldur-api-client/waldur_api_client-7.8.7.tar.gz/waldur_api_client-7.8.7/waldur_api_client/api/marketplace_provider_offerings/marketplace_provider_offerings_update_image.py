from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.offering_image_request import OfferingImageRequest
from ...models.offering_image_request_form import OfferingImageRequestForm
from ...models.offering_image_request_multipart import OfferingImageRequestMultipart
from ...models.provider_offering_details import ProviderOfferingDetails
from ...types import Response


def _get_kwargs(
    uuid: UUID,
    *,
    body: Union[
        OfferingImageRequest,
        OfferingImageRequestForm,
        OfferingImageRequestMultipart,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/marketplace-provider-offerings/{uuid}/update_image/",
    }

    if isinstance(body, OfferingImageRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, OfferingImageRequestForm):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, OfferingImageRequestMultipart):
        _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> ProviderOfferingDetails:
    if response.status_code == 404:
        raise errors.UnexpectedStatus(response.status_code, response.content, response.url)
    if response.status_code == 200:
        response_200 = ProviderOfferingDetails.from_dict(response.json())

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content, response.url)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ProviderOfferingDetails]:
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
    body: Union[
        OfferingImageRequest,
        OfferingImageRequestForm,
        OfferingImageRequestMultipart,
    ],
) -> Response[ProviderOfferingDetails]:
    """Update offering image.

    Args:
        uuid (UUID):
        body (OfferingImageRequest):
        body (OfferingImageRequestForm):
        body (OfferingImageRequestMultipart):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProviderOfferingDetails]
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
    body: Union[
        OfferingImageRequest,
        OfferingImageRequestForm,
        OfferingImageRequestMultipart,
    ],
) -> ProviderOfferingDetails:
    """Update offering image.

    Args:
        uuid (UUID):
        body (OfferingImageRequest):
        body (OfferingImageRequestForm):
        body (OfferingImageRequestMultipart):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProviderOfferingDetails
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
    body: Union[
        OfferingImageRequest,
        OfferingImageRequestForm,
        OfferingImageRequestMultipart,
    ],
) -> Response[ProviderOfferingDetails]:
    """Update offering image.

    Args:
        uuid (UUID):
        body (OfferingImageRequest):
        body (OfferingImageRequestForm):
        body (OfferingImageRequestMultipart):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProviderOfferingDetails]
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
    body: Union[
        OfferingImageRequest,
        OfferingImageRequestForm,
        OfferingImageRequestMultipart,
    ],
) -> ProviderOfferingDetails:
    """Update offering image.

    Args:
        uuid (UUID):
        body (OfferingImageRequest):
        body (OfferingImageRequestForm):
        body (OfferingImageRequestMultipart):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProviderOfferingDetails
    """

    return (
        await asyncio_detailed(
            uuid=uuid,
            client=client,
            body=body,
        )
    ).parsed
