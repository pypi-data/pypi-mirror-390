from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.bad_request_error import BadRequestError
from ...models.forbidden_error import ForbiddenError
from ...models.internal_server_error import InternalServerError
from ...models.not_found_error import NotFoundError
from ...models.transfer_ticket_request import TransferTicketRequest
from ...models.transfer_ticket_result import TransferTicketResult
from ...models.unauthorized_error import UnauthorizedError
from ...models.unprocessable_entity_error import UnprocessableEntityError
from ...types import Response


def _get_kwargs(
    event_id: str,
    ticket_id: str,
    *,
    body: TransferTicketRequest,
    x_access_api_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-access-api-key"] = x_access_api_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/events/{event_id}/tickets/{ticket_id}/transfer",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    BadRequestError
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | TransferTicketResult
    | UnauthorizedError
    | UnprocessableEntityError
):
    if response.status_code == 200:
        response_200 = TransferTicketResult.from_dict(response.json())

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
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | TransferTicketResult
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
    body: TransferTicketRequest,
    x_access_api_key: str,
) -> Response[
    BadRequestError
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | TransferTicketResult
    | UnauthorizedError
    | UnprocessableEntityError
]:
    """Transfer Ticket

     Transfers a ticket from one person to another. Requires special user permission to use this
    endpoint, activated by Humanitix.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        ticket_id (str):  Example: 5da50970ec90824b5ca3608f.
        x_access_api_key (str):
        body (TransferTicketRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequestError | ForbiddenError | InternalServerError | NotFoundError | TransferTicketResult | UnauthorizedError | UnprocessableEntityError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        ticket_id=ticket_id,
        body=body,
        x_access_api_key=x_access_api_key,
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
    body: TransferTicketRequest,
    x_access_api_key: str,
) -> (
    BadRequestError
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | TransferTicketResult
    | UnauthorizedError
    | UnprocessableEntityError
    | None
):
    """Transfer Ticket

     Transfers a ticket from one person to another. Requires special user permission to use this
    endpoint, activated by Humanitix.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        ticket_id (str):  Example: 5da50970ec90824b5ca3608f.
        x_access_api_key (str):
        body (TransferTicketRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequestError | ForbiddenError | InternalServerError | NotFoundError | TransferTicketResult | UnauthorizedError | UnprocessableEntityError
    """

    return sync_detailed(
        event_id=event_id,
        ticket_id=ticket_id,
        client=client,
        body=body,
        x_access_api_key=x_access_api_key,
    ).parsed


async def asyncio_detailed(
    event_id: str,
    ticket_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: TransferTicketRequest,
    x_access_api_key: str,
) -> Response[
    BadRequestError
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | TransferTicketResult
    | UnauthorizedError
    | UnprocessableEntityError
]:
    """Transfer Ticket

     Transfers a ticket from one person to another. Requires special user permission to use this
    endpoint, activated by Humanitix.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        ticket_id (str):  Example: 5da50970ec90824b5ca3608f.
        x_access_api_key (str):
        body (TransferTicketRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequestError | ForbiddenError | InternalServerError | NotFoundError | TransferTicketResult | UnauthorizedError | UnprocessableEntityError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        ticket_id=ticket_id,
        body=body,
        x_access_api_key=x_access_api_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    event_id: str,
    ticket_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: TransferTicketRequest,
    x_access_api_key: str,
) -> (
    BadRequestError
    | ForbiddenError
    | InternalServerError
    | NotFoundError
    | TransferTicketResult
    | UnauthorizedError
    | UnprocessableEntityError
    | None
):
    """Transfer Ticket

     Transfers a ticket from one person to another. Requires special user permission to use this
    endpoint, activated by Humanitix.

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        ticket_id (str):  Example: 5da50970ec90824b5ca3608f.
        x_access_api_key (str):
        body (TransferTicketRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequestError | ForbiddenError | InternalServerError | NotFoundError | TransferTicketResult | UnauthorizedError | UnprocessableEntityError
    """

    return (
        await asyncio_detailed(
            event_id=event_id,
            ticket_id=ticket_id,
            client=client,
            body=body,
            x_access_api_key=x_access_api_key,
        )
    ).parsed
