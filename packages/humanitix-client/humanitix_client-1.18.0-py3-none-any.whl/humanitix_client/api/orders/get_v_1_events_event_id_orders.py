import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.get_v1_events_event_id_orders_response_200 import GetV1EventsEventIdOrdersResponse200
from ...models.internal_server_error import InternalServerError
from ...models.not_found_error import NotFoundError
from ...models.unauthorized_error import UnauthorizedError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    event_id: str,
    *,
    event_date_id: str | Unset = UNSET,
    page: int,
    page_size: int | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    override_location: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["eventDateId"] = event_date_id

    params["page"] = page

    params["pageSize"] = page_size

    json_since: str | Unset = UNSET
    if not isinstance(since, Unset):
        json_since = since.isoformat()
    params["since"] = json_since

    params["overrideLocation"] = override_location

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/events/{event_id}/orders",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetV1EventsEventIdOrdersResponse200 | InternalServerError | NotFoundError | UnauthorizedError:
    if response.status_code == 200:
        response_200 = GetV1EventsEventIdOrdersResponse200.from_dict(response.json())

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
) -> Response[GetV1EventsEventIdOrdersResponse200 | InternalServerError | NotFoundError | UnauthorizedError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    event_id: str,
    *,
    client: AuthenticatedClient | Client,
    event_date_id: str | Unset = UNSET,
    page: int,
    page_size: int | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    override_location: str | Unset = UNSET,
) -> Response[GetV1EventsEventIdOrdersResponse200 | InternalServerError | NotFoundError | UnauthorizedError]:
    """Get Orders

     Returns all orders for a given event and eventDateId.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str | Unset):  Example: 5ac598ccd8fe7c0c0f212e2f.
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        since (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetV1EventsEventIdOrdersResponse200 | InternalServerError | NotFoundError | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        event_date_id=event_date_id,
        page=page,
        page_size=page_size,
        since=since,
        override_location=override_location,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    event_id: str,
    *,
    client: AuthenticatedClient | Client,
    event_date_id: str | Unset = UNSET,
    page: int,
    page_size: int | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    override_location: str | Unset = UNSET,
) -> GetV1EventsEventIdOrdersResponse200 | InternalServerError | NotFoundError | UnauthorizedError | None:
    """Get Orders

     Returns all orders for a given event and eventDateId.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str | Unset):  Example: 5ac598ccd8fe7c0c0f212e2f.
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        since (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetV1EventsEventIdOrdersResponse200 | InternalServerError | NotFoundError | UnauthorizedError
    """

    return sync_detailed(
        event_id=event_id,
        client=client,
        event_date_id=event_date_id,
        page=page,
        page_size=page_size,
        since=since,
        override_location=override_location,
    ).parsed


async def asyncio_detailed(
    event_id: str,
    *,
    client: AuthenticatedClient | Client,
    event_date_id: str | Unset = UNSET,
    page: int,
    page_size: int | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    override_location: str | Unset = UNSET,
) -> Response[GetV1EventsEventIdOrdersResponse200 | InternalServerError | NotFoundError | UnauthorizedError]:
    """Get Orders

     Returns all orders for a given event and eventDateId.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str | Unset):  Example: 5ac598ccd8fe7c0c0f212e2f.
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        since (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetV1EventsEventIdOrdersResponse200 | InternalServerError | NotFoundError | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        event_date_id=event_date_id,
        page=page,
        page_size=page_size,
        since=since,
        override_location=override_location,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    event_id: str,
    *,
    client: AuthenticatedClient | Client,
    event_date_id: str | Unset = UNSET,
    page: int,
    page_size: int | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    override_location: str | Unset = UNSET,
) -> GetV1EventsEventIdOrdersResponse200 | InternalServerError | NotFoundError | UnauthorizedError | None:
    """Get Orders

     Returns all orders for a given event and eventDateId.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str | Unset):  Example: 5ac598ccd8fe7c0c0f212e2f.
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        since (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetV1EventsEventIdOrdersResponse200 | InternalServerError | NotFoundError | UnauthorizedError
    """

    return (
        await asyncio_detailed(
            event_id=event_id,
            client=client,
            event_date_id=event_date_id,
            page=page,
            page_size=page_size,
            since=since,
            override_location=override_location,
        )
    ).parsed
