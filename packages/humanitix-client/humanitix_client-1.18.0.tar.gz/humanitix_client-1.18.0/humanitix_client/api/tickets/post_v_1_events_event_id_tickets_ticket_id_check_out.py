from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.bad_request_error import BadRequestError
from ...models.check_in_out_result import CheckInOutResult
from ...models.forbidden_error import ForbiddenError
from ...models.internal_server_error import InternalServerError
from ...models.not_found_error import NotFoundError
from ...models.unauthorized_error import UnauthorizedError
from ...models.unprocessable_entity_error import UnprocessableEntityError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    event_id: str,
    ticket_id: str,
    *,
    override_location: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["overrideLocation"] = override_location

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/events/{event_id}/tickets/{ticket_id}/check-out",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    BadRequestError
    | CheckInOutResult
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | UnauthorizedError
    | UnprocessableEntityError
):
    if response.status_code == 200:
        response_200 = CheckInOutResult.from_dict(response.json())

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

    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404

    if response.status_code == 422:
        response_422 = UnprocessableEntityError.from_dict(response.json())

        return response_422

    response_default = InternalServerError.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    BadRequestError
    | CheckInOutResult
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | UnauthorizedError
    | UnprocessableEntityError
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    event_id: str,
    ticket_id: str,
    *,
    client: AuthenticatedClient | Client,
    override_location: str | Unset = UNSET,
) -> Response[
    BadRequestError
    | CheckInOutResult
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | UnauthorizedError
    | UnprocessableEntityError
]:
    """Check out

     Update the ticket to check it out

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        ticket_id (str):  Example: 5da50970ec90824b5ca3608f.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequestError | CheckInOutResult | ForbiddenError | InternalServerError | NotFoundError | UnauthorizedError | UnprocessableEntityError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        ticket_id=ticket_id,
        override_location=override_location,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    event_id: str,
    ticket_id: str,
    *,
    client: AuthenticatedClient | Client,
    override_location: str | Unset = UNSET,
) -> (
    BadRequestError
    | CheckInOutResult
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | UnauthorizedError
    | UnprocessableEntityError
    | None
):
    """Check out

     Update the ticket to check it out

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        ticket_id (str):  Example: 5da50970ec90824b5ca3608f.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequestError | CheckInOutResult | ForbiddenError | InternalServerError | NotFoundError | UnauthorizedError | UnprocessableEntityError
    """

    return sync_detailed(
        event_id=event_id,
        ticket_id=ticket_id,
        client=client,
        override_location=override_location,
    ).parsed


async def asyncio_detailed(
    event_id: str,
    ticket_id: str,
    *,
    client: AuthenticatedClient | Client,
    override_location: str | Unset = UNSET,
) -> Response[
    BadRequestError
    | CheckInOutResult
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | UnauthorizedError
    | UnprocessableEntityError
]:
    """Check out

     Update the ticket to check it out

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        ticket_id (str):  Example: 5da50970ec90824b5ca3608f.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequestError | CheckInOutResult | ForbiddenError | InternalServerError | NotFoundError | UnauthorizedError | UnprocessableEntityError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        ticket_id=ticket_id,
        override_location=override_location,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    event_id: str,
    ticket_id: str,
    *,
    client: AuthenticatedClient | Client,
    override_location: str | Unset = UNSET,
) -> (
    BadRequestError
    | CheckInOutResult
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | UnauthorizedError
    | UnprocessableEntityError
    | None
):
    """Check out

     Update the ticket to check it out

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        ticket_id (str):  Example: 5da50970ec90824b5ca3608f.
        override_location (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequestError | CheckInOutResult | ForbiddenError | InternalServerError | NotFoundError | UnauthorizedError | UnprocessableEntityError
    """

    return (
        await asyncio_detailed(
            event_id=event_id,
            ticket_id=ticket_id,
            client=client,
            override_location=override_location,
        )
    ).parsed
