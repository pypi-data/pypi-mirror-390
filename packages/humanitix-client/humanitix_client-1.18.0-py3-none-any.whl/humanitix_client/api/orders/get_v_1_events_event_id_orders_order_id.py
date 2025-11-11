from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.internal_server_error import InternalServerError
from ...models.not_found_error import NotFoundError
from ...models.order import Order
from ...models.unauthorized_error import UnauthorizedError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    event_id: str,
    order_id: str,
    *,
    override_location: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["overrideLocation"] = override_location

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/events/{event_id}/orders/{order_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> InternalServerError | NotFoundError | Order | UnauthorizedError:
    if response.status_code == 200:
        response_200 = Order.from_dict(response.json())

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
) -> Response[InternalServerError | NotFoundError | Order | UnauthorizedError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    event_id: str,
    order_id: str,
    *,
    client: AuthenticatedClient | Client,
    override_location: str | Unset = UNSET,
) -> Response[InternalServerError | NotFoundError | Order | UnauthorizedError]:
    """Get Order

     Returns an order for the given eventId.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        order_id (str):  Example: 5ac599d1a488620e6cd01d87.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[InternalServerError | NotFoundError | Order | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        order_id=order_id,
        override_location=override_location,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    event_id: str,
    order_id: str,
    *,
    client: AuthenticatedClient | Client,
    override_location: str | Unset = UNSET,
) -> InternalServerError | NotFoundError | Order | UnauthorizedError | None:
    """Get Order

     Returns an order for the given eventId.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        order_id (str):  Example: 5ac599d1a488620e6cd01d87.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        InternalServerError | NotFoundError | Order | UnauthorizedError
    """

    return sync_detailed(
        event_id=event_id,
        order_id=order_id,
        client=client,
        override_location=override_location,
    ).parsed


async def asyncio_detailed(
    event_id: str,
    order_id: str,
    *,
    client: AuthenticatedClient | Client,
    override_location: str | Unset = UNSET,
) -> Response[InternalServerError | NotFoundError | Order | UnauthorizedError]:
    """Get Order

     Returns an order for the given eventId.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        order_id (str):  Example: 5ac599d1a488620e6cd01d87.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[InternalServerError | NotFoundError | Order | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        order_id=order_id,
        override_location=override_location,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    event_id: str,
    order_id: str,
    *,
    client: AuthenticatedClient | Client,
    override_location: str | Unset = UNSET,
) -> InternalServerError | NotFoundError | Order | UnauthorizedError | None:
    """Get Order

     Returns an order for the given eventId.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        order_id (str):  Example: 5ac599d1a488620e6cd01d87.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        InternalServerError | NotFoundError | Order | UnauthorizedError
    """

    return (
        await asyncio_detailed(
            event_id=event_id,
            order_id=order_id,
            client=client,
            override_location=override_location,
        )
    ).parsed
