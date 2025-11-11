import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_v1_events_event_id_tickets_response_200 import GetV1EventsEventIdTicketsResponse200
from ...models.get_v1_events_event_id_tickets_status import GetV1EventsEventIdTicketsStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    event_id: str,
    *,
    event_date_id: str | Unset = UNSET,
    page: int,
    page_size: int | Unset = UNSET,
    status: GetV1EventsEventIdTicketsStatus | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    override_location: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["eventDateId"] = event_date_id

    params["page"] = page

    params["pageSize"] = page_size

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    json_since: str | Unset = UNSET
    if not isinstance(since, Unset):
        json_since = since.isoformat()
    params["since"] = json_since

    params["overrideLocation"] = override_location

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/events/{event_id}/tickets",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetV1EventsEventIdTicketsResponse200 | None:
    if response.status_code == 200:
        response_200 = GetV1EventsEventIdTicketsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetV1EventsEventIdTicketsResponse200]:
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
    status: GetV1EventsEventIdTicketsStatus | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    override_location: str | Unset = UNSET,
) -> Response[GetV1EventsEventIdTicketsResponse200]:
    """Get Tickets

     Returns all tickets for an event.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str | Unset):  Example: 5ac598ccd8fe7c0c0f212e2f.
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        status (GetV1EventsEventIdTicketsStatus | Unset):
        since (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetV1EventsEventIdTicketsResponse200]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        event_date_id=event_date_id,
        page=page,
        page_size=page_size,
        status=status,
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
    status: GetV1EventsEventIdTicketsStatus | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    override_location: str | Unset = UNSET,
) -> GetV1EventsEventIdTicketsResponse200 | None:
    """Get Tickets

     Returns all tickets for an event.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str | Unset):  Example: 5ac598ccd8fe7c0c0f212e2f.
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        status (GetV1EventsEventIdTicketsStatus | Unset):
        since (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetV1EventsEventIdTicketsResponse200
    """

    return sync_detailed(
        event_id=event_id,
        client=client,
        event_date_id=event_date_id,
        page=page,
        page_size=page_size,
        status=status,
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
    status: GetV1EventsEventIdTicketsStatus | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    override_location: str | Unset = UNSET,
) -> Response[GetV1EventsEventIdTicketsResponse200]:
    """Get Tickets

     Returns all tickets for an event.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str | Unset):  Example: 5ac598ccd8fe7c0c0f212e2f.
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        status (GetV1EventsEventIdTicketsStatus | Unset):
        since (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetV1EventsEventIdTicketsResponse200]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        event_date_id=event_date_id,
        page=page,
        page_size=page_size,
        status=status,
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
    status: GetV1EventsEventIdTicketsStatus | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    override_location: str | Unset = UNSET,
) -> GetV1EventsEventIdTicketsResponse200 | None:
    """Get Tickets

     Returns all tickets for an event.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str | Unset):  Example: 5ac598ccd8fe7c0c0f212e2f.
        page (int): Page number you wish to fetch.
        page_size (int | Unset): Page size of the results you wish to fetch.
        status (GetV1EventsEventIdTicketsStatus | Unset):
        since (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetV1EventsEventIdTicketsResponse200
    """

    return (
        await asyncio_detailed(
            event_id=event_id,
            client=client,
            event_date_id=event_date_id,
            page=page,
            page_size=page_size,
            status=status,
            since=since,
            override_location=override_location,
        )
    ).parsed
