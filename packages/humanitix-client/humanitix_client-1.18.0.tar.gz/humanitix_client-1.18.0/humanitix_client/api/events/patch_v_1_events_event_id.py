from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.bad_request_error import BadRequestError
from ...models.event import Event
from ...models.forbidden_error import ForbiddenError
from ...models.internal_server_error import InternalServerError
from ...models.unauthorized_error import UnauthorizedError
from ...models.update_event_request import UpdateEventRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    event_id: str,
    *,
    body: UpdateEventRequest,
    override_location: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["overrideLocation"] = override_location

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/v1/events/{event_id}",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BadRequestError | Event | ForbiddenError | InternalServerError | UnauthorizedError:
    if response.status_code == 200:
        response_200 = Event.from_dict(response.json())

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
) -> Response[BadRequestError | Event | ForbiddenError | InternalServerError | UnauthorizedError]:
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
    body: UpdateEventRequest,
    override_location: str | Unset = UNSET,
) -> Response[BadRequestError | Event | ForbiddenError | InternalServerError | UnauthorizedError]:
    """Update Event. Requires special user permission to use this endpoint, activated by Humanitix.

     Update an event

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        override_location (str | Unset):
        body (UpdateEventRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequestError | Event | ForbiddenError | InternalServerError | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        body=body,
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
    body: UpdateEventRequest,
    override_location: str | Unset = UNSET,
) -> BadRequestError | Event | ForbiddenError | InternalServerError | UnauthorizedError | None:
    """Update Event. Requires special user permission to use this endpoint, activated by Humanitix.

     Update an event

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        override_location (str | Unset):
        body (UpdateEventRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequestError | Event | ForbiddenError | InternalServerError | UnauthorizedError
    """

    return sync_detailed(
        event_id=event_id,
        client=client,
        body=body,
        override_location=override_location,
    ).parsed


async def asyncio_detailed(
    event_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateEventRequest,
    override_location: str | Unset = UNSET,
) -> Response[BadRequestError | Event | ForbiddenError | InternalServerError | UnauthorizedError]:
    """Update Event. Requires special user permission to use this endpoint, activated by Humanitix.

     Update an event

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        override_location (str | Unset):
        body (UpdateEventRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequestError | Event | ForbiddenError | InternalServerError | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        body=body,
        override_location=override_location,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    event_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateEventRequest,
    override_location: str | Unset = UNSET,
) -> BadRequestError | Event | ForbiddenError | InternalServerError | UnauthorizedError | None:
    """Update Event. Requires special user permission to use this endpoint, activated by Humanitix.

     Update an event

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        override_location (str | Unset):
        body (UpdateEventRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequestError | Event | ForbiddenError | InternalServerError | UnauthorizedError
    """

    return (
        await asyncio_detailed(
            event_id=event_id,
            client=client,
            body=body,
            override_location=override_location,
        )
    ).parsed
