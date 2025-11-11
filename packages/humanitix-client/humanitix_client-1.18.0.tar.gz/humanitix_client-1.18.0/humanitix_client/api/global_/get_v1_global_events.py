from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.bad_request_error import BadRequestError
from ...models.category import Category
from ...models.forbidden_error import ForbiddenError
from ...models.get_v1_global_events_response_200 import GetV1GlobalEventsResponse200
from ...models.internal_server_error import InternalServerError
from ...models.subcategory import Subcategory
from ...models.type_ import Type
from ...models.unauthorized_error import UnauthorizedError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: int,
    page_size: int | Unset = UNSET,
    type_: Type | Unset = UNSET,
    category: Category | Unset = UNSET,
    subcategory: Subcategory | Unset = UNSET,
    override_location: str | Unset = UNSET,
    with_artists_only: bool | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["pageSize"] = page_size

    json_type_: str | Unset = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_.value

    params["type"] = json_type_

    json_category: str | Unset = UNSET
    if not isinstance(category, Unset):
        json_category = category.value

    params["category"] = json_category

    json_subcategory: str | Unset = UNSET
    if not isinstance(subcategory, Unset):
        json_subcategory = subcategory.value

    params["subcategory"] = json_subcategory

    params["overrideLocation"] = override_location

    params["withArtistsOnly"] = with_artists_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/global/events",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BadRequestError | ForbiddenError | GetV1GlobalEventsResponse200 | InternalServerError | UnauthorizedError:
    if response.status_code == 200:
        response_200 = GetV1GlobalEventsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = UnauthorizedError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ForbiddenError.from_dict(response.json())

        return response_403

    response_default = InternalServerError.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    BadRequestError | ForbiddenError | GetV1GlobalEventsResponse200 | InternalServerError | UnauthorizedError
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    page: int,
    page_size: int | Unset = UNSET,
    type_: Type | Unset = UNSET,
    category: Category | Unset = UNSET,
    subcategory: Subcategory | Unset = UNSET,
    override_location: str | Unset = UNSET,
    with_artists_only: bool | Unset = UNSET,
) -> Response[
    BadRequestError | ForbiddenError | GetV1GlobalEventsResponse200 | InternalServerError | UnauthorizedError
]:
    """Get Events global

     Returns an array of events from across the platform. Requires special user permission to use this
    endpoint, activated by Humanitix.

    Args:
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        type_ (Type | Unset):  Example: festivalOrFair.
        category (Category | Unset):  Example: music.
        subcategory (Subcategory | Unset):  Example: electronic.
        override_location (str | Unset):
        with_artists_only (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequestError | ForbiddenError | GetV1GlobalEventsResponse200 | InternalServerError | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        type_=type_,
        category=category,
        subcategory=subcategory,
        override_location=override_location,
        with_artists_only=with_artists_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    page: int,
    page_size: int | Unset = UNSET,
    type_: Type | Unset = UNSET,
    category: Category | Unset = UNSET,
    subcategory: Subcategory | Unset = UNSET,
    override_location: str | Unset = UNSET,
    with_artists_only: bool | Unset = UNSET,
) -> BadRequestError | ForbiddenError | GetV1GlobalEventsResponse200 | InternalServerError | UnauthorizedError | None:
    """Get Events global

     Returns an array of events from across the platform. Requires special user permission to use this
    endpoint, activated by Humanitix.

    Args:
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        type_ (Type | Unset):  Example: festivalOrFair.
        category (Category | Unset):  Example: music.
        subcategory (Subcategory | Unset):  Example: electronic.
        override_location (str | Unset):
        with_artists_only (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequestError | ForbiddenError | GetV1GlobalEventsResponse200 | InternalServerError | UnauthorizedError
    """

    return sync_detailed(
        client=client,
        page=page,
        page_size=page_size,
        type_=type_,
        category=category,
        subcategory=subcategory,
        override_location=override_location,
        with_artists_only=with_artists_only,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    page: int,
    page_size: int | Unset = UNSET,
    type_: Type | Unset = UNSET,
    category: Category | Unset = UNSET,
    subcategory: Subcategory | Unset = UNSET,
    override_location: str | Unset = UNSET,
    with_artists_only: bool | Unset = UNSET,
) -> Response[
    BadRequestError | ForbiddenError | GetV1GlobalEventsResponse200 | InternalServerError | UnauthorizedError
]:
    """Get Events global

     Returns an array of events from across the platform. Requires special user permission to use this
    endpoint, activated by Humanitix.

    Args:
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        type_ (Type | Unset):  Example: festivalOrFair.
        category (Category | Unset):  Example: music.
        subcategory (Subcategory | Unset):  Example: electronic.
        override_location (str | Unset):
        with_artists_only (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequestError | ForbiddenError | GetV1GlobalEventsResponse200 | InternalServerError | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        type_=type_,
        category=category,
        subcategory=subcategory,
        override_location=override_location,
        with_artists_only=with_artists_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    page: int,
    page_size: int | Unset = UNSET,
    type_: Type | Unset = UNSET,
    category: Category | Unset = UNSET,
    subcategory: Subcategory | Unset = UNSET,
    override_location: str | Unset = UNSET,
    with_artists_only: bool | Unset = UNSET,
) -> BadRequestError | ForbiddenError | GetV1GlobalEventsResponse200 | InternalServerError | UnauthorizedError | None:
    """Get Events global

     Returns an array of events from across the platform. Requires special user permission to use this
    endpoint, activated by Humanitix.

    Args:
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        type_ (Type | Unset):  Example: festivalOrFair.
        category (Category | Unset):  Example: music.
        subcategory (Subcategory | Unset):  Example: electronic.
        override_location (str | Unset):
        with_artists_only (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequestError | ForbiddenError | GetV1GlobalEventsResponse200 | InternalServerError | UnauthorizedError
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            page_size=page_size,
            type_=type_,
            category=category,
            subcategory=subcategory,
            override_location=override_location,
            with_artists_only=with_artists_only,
        )
    ).parsed
