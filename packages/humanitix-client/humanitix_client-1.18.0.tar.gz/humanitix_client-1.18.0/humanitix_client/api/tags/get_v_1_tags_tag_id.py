from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.internal_server_error import InternalServerError
from ...models.not_found_error import NotFoundError
from ...models.tag import Tag
from ...models.unauthorized_error import UnauthorizedError
from ...types import Response


def _get_kwargs(
    tag_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/tags/{tag_id}",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> InternalServerError | NotFoundError | Tag | UnauthorizedError:
    if response.status_code == 200:
        response_200 = Tag.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = UnauthorizedError.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404

    response_default = InternalServerError.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[InternalServerError | NotFoundError | Tag | UnauthorizedError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tag_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[InternalServerError | NotFoundError | Tag | UnauthorizedError]:
    """Get Tag

     Returns a tag for the given tagId.

    Args:
        tag_id (str):  Example: 5d806e987b0ffa3b26a8fc2b.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[InternalServerError | NotFoundError | Tag | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        tag_id=tag_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tag_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> InternalServerError | NotFoundError | Tag | UnauthorizedError | None:
    """Get Tag

     Returns a tag for the given tagId.

    Args:
        tag_id (str):  Example: 5d806e987b0ffa3b26a8fc2b.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        InternalServerError | NotFoundError | Tag | UnauthorizedError
    """

    return sync_detailed(
        tag_id=tag_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    tag_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[InternalServerError | NotFoundError | Tag | UnauthorizedError]:
    """Get Tag

     Returns a tag for the given tagId.

    Args:
        tag_id (str):  Example: 5d806e987b0ffa3b26a8fc2b.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[InternalServerError | NotFoundError | Tag | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        tag_id=tag_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tag_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> InternalServerError | NotFoundError | Tag | UnauthorizedError | None:
    """Get Tag

     Returns a tag for the given tagId.

    Args:
        tag_id (str):  Example: 5d806e987b0ffa3b26a8fc2b.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        InternalServerError | NotFoundError | Tag | UnauthorizedError
    """

    return (
        await asyncio_detailed(
            tag_id=tag_id,
            client=client,
        )
    ).parsed
