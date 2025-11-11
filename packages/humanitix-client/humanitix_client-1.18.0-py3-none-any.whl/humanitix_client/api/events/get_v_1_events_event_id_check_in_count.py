from http import HTTPStatus
from typing import Any

import httpx

from ...client import AuthenticatedClient, Client
from ...models.check_in_count_result import CheckInCountResult
from ...models.internal_server_error import InternalServerError
from ...models.not_found_error import NotFoundError
from ...models.unauthorized_error import UnauthorizedError
from ...types import UNSET, Response


def _get_kwargs(
    event_id: str,
    *,
    event_date_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["eventDateId"] = event_date_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/events/{event_id}/check-in-count",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CheckInCountResult | InternalServerError | NotFoundError | UnauthorizedError:
    if response.status_code == 200:
        response_200 = CheckInCountResult.from_dict(response.json())

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
) -> Response[CheckInCountResult | InternalServerError | NotFoundError | UnauthorizedError]:
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
    event_date_id: str,
) -> Response[CheckInCountResult | InternalServerError | NotFoundError | UnauthorizedError]:
    """Get Event check in count (BETA)

     Returns a check in count object for a given eventId and eventDateId for all tickets that have had
    sales (this endpoint is in Beta and is subject to change).

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str):  Example: 5ac598ccd8fe7c0c0f212e2f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CheckInCountResult | InternalServerError | NotFoundError | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        event_date_id=event_date_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    event_id: str,
    *,
    client: AuthenticatedClient | Client,
    event_date_id: str,
) -> CheckInCountResult | InternalServerError | NotFoundError | UnauthorizedError | None:
    """Get Event check in count (BETA)

     Returns a check in count object for a given eventId and eventDateId for all tickets that have had
    sales (this endpoint is in Beta and is subject to change).

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str):  Example: 5ac598ccd8fe7c0c0f212e2f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CheckInCountResult | InternalServerError | NotFoundError | UnauthorizedError
    """

    return sync_detailed(
        event_id=event_id,
        client=client,
        event_date_id=event_date_id,
    ).parsed


async def asyncio_detailed(
    event_id: str,
    *,
    client: AuthenticatedClient | Client,
    event_date_id: str,
) -> Response[CheckInCountResult | InternalServerError | NotFoundError | UnauthorizedError]:
    """Get Event check in count (BETA)

     Returns a check in count object for a given eventId and eventDateId for all tickets that have had
    sales (this endpoint is in Beta and is subject to change).

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str):  Example: 5ac598ccd8fe7c0c0f212e2f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CheckInCountResult | InternalServerError | NotFoundError | UnauthorizedError]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        event_date_id=event_date_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    event_id: str,
    *,
    client: AuthenticatedClient | Client,
    event_date_id: str,
) -> CheckInCountResult | InternalServerError | NotFoundError | UnauthorizedError | None:
    """Get Event check in count (BETA)

     Returns a check in count object for a given eventId and eventDateId for all tickets that have had
    sales (this endpoint is in Beta and is subject to change).

    Args:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str):  Example: 5ac598ccd8fe7c0c0f212e2f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CheckInCountResult | InternalServerError | NotFoundError | UnauthorizedError
    """

    return (
        await asyncio_detailed(
            event_id=event_id,
            client=client,
            event_date_id=event_date_id,
        )
    ).parsed
