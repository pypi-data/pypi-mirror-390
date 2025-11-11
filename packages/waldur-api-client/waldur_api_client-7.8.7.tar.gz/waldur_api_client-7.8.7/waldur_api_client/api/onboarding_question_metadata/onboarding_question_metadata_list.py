from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.onboarding_question_metadata import OnboardingQuestionMetadata
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    checklist_uuid: Union[Unset, UUID] = UNSET,
    intent_field: Union[Unset, str] = UNSET,
    maps_to_customer_field: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    question_description: Union[Unset, str] = UNSET,
    question_uuid: Union[Unset, UUID] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_checklist_uuid: Union[Unset, str] = UNSET
    if not isinstance(checklist_uuid, Unset):
        json_checklist_uuid = str(checklist_uuid)
    params["checklist_uuid"] = json_checklist_uuid

    params["intent_field"] = intent_field

    params["maps_to_customer_field"] = maps_to_customer_field

    params["page"] = page

    params["page_size"] = page_size

    params["question_description"] = question_description

    json_question_uuid: Union[Unset, str] = UNSET
    if not isinstance(question_uuid, Unset):
        json_question_uuid = str(question_uuid)
    params["question_uuid"] = json_question_uuid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/onboarding-question-metadata/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["OnboardingQuestionMetadata"]:
    if response.status_code == 404:
        raise errors.UnexpectedStatus(response.status_code, response.content, response.url)
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = OnboardingQuestionMetadata.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content, response.url)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["OnboardingQuestionMetadata"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    checklist_uuid: Union[Unset, UUID] = UNSET,
    intent_field: Union[Unset, str] = UNSET,
    maps_to_customer_field: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    question_description: Union[Unset, str] = UNSET,
    question_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["OnboardingQuestionMetadata"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        checklist_uuid (Union[Unset, UUID]):
        intent_field (Union[Unset, str]):
        maps_to_customer_field (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        question_description (Union[Unset, str]):
        question_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['OnboardingQuestionMetadata']]
    """

    kwargs = _get_kwargs(
        checklist_uuid=checklist_uuid,
        intent_field=intent_field,
        maps_to_customer_field=maps_to_customer_field,
        page=page,
        page_size=page_size,
        question_description=question_description,
        question_uuid=question_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    checklist_uuid: Union[Unset, UUID] = UNSET,
    intent_field: Union[Unset, str] = UNSET,
    maps_to_customer_field: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    question_description: Union[Unset, str] = UNSET,
    question_uuid: Union[Unset, UUID] = UNSET,
) -> list["OnboardingQuestionMetadata"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        checklist_uuid (Union[Unset, UUID]):
        intent_field (Union[Unset, str]):
        maps_to_customer_field (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        question_description (Union[Unset, str]):
        question_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['OnboardingQuestionMetadata']
    """

    return sync_detailed(
        client=client,
        checklist_uuid=checklist_uuid,
        intent_field=intent_field,
        maps_to_customer_field=maps_to_customer_field,
        page=page,
        page_size=page_size,
        question_description=question_description,
        question_uuid=question_uuid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    checklist_uuid: Union[Unset, UUID] = UNSET,
    intent_field: Union[Unset, str] = UNSET,
    maps_to_customer_field: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    question_description: Union[Unset, str] = UNSET,
    question_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["OnboardingQuestionMetadata"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        checklist_uuid (Union[Unset, UUID]):
        intent_field (Union[Unset, str]):
        maps_to_customer_field (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        question_description (Union[Unset, str]):
        question_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['OnboardingQuestionMetadata']]
    """

    kwargs = _get_kwargs(
        checklist_uuid=checklist_uuid,
        intent_field=intent_field,
        maps_to_customer_field=maps_to_customer_field,
        page=page,
        page_size=page_size,
        question_description=question_description,
        question_uuid=question_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    checklist_uuid: Union[Unset, UUID] = UNSET,
    intent_field: Union[Unset, str] = UNSET,
    maps_to_customer_field: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    question_description: Union[Unset, str] = UNSET,
    question_uuid: Union[Unset, UUID] = UNSET,
) -> list["OnboardingQuestionMetadata"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        checklist_uuid (Union[Unset, UUID]):
        intent_field (Union[Unset, str]):
        maps_to_customer_field (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        question_description (Union[Unset, str]):
        question_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['OnboardingQuestionMetadata']
    """

    return (
        await asyncio_detailed(
            client=client,
            checklist_uuid=checklist_uuid,
            intent_field=intent_field,
            maps_to_customer_field=maps_to_customer_field,
            page=page,
            page_size=page_size,
            question_description=question_description,
            question_uuid=question_uuid,
        )
    ).parsed
