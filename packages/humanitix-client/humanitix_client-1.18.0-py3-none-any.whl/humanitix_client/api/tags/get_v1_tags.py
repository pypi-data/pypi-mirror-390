from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.bad_request_error import BadRequestError
from ...models.get_v1_tags_response_200 import GetV1TagsResponse200
from ...models.internal_server_error import InternalServerError
from ...models.unauthorized_error import UnauthorizedError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: int,
    page_size: int | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["pageSize"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/tags",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BadRequestError | GetV1TagsResponse200 | InternalServerError | UnauthorizedError:
    if response.status_code == 200:
        response_200 = GetV1TagsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = UnauthorizedError.from_dict(response.json())

        return response_401

    response_default = InternalServerError.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[BadRequestError | GetV1TagsResponse200 | InternalServerError | UnauthorizedError]:
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
) -> Response[BadRequestError | GetV1TagsResponse200 | InternalServerError | UnauthorizedError]:
    """Get Tags

     Returns all tags for a user.

    Args:
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequestError | GetV1TagsResponse200 | InternalServerError | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
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
) -> BadRequestError | GetV1TagsResponse200 | InternalServerError | UnauthorizedError | None:
    """Get Tags

     Returns all tags for a user.

    Args:
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequestError | GetV1TagsResponse200 | InternalServerError | UnauthorizedError
    """

    return sync_detailed(
        client=client,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    page: int,
    page_size: int | Unset = UNSET,
) -> Response[BadRequestError | GetV1TagsResponse200 | InternalServerError | UnauthorizedError]:
    """Get Tags

     Returns all tags for a user.

    Args:
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequestError | GetV1TagsResponse200 | InternalServerError | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    page: int,
    page_size: int | Unset = UNSET,
) -> BadRequestError | GetV1TagsResponse200 | InternalServerError | UnauthorizedError | None:
    """Get Tags

     Returns all tags for a user.

    Args:
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequestError | GetV1TagsResponse200 | InternalServerError | UnauthorizedError
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            page_size=page_size,
        )
    ).parsed
