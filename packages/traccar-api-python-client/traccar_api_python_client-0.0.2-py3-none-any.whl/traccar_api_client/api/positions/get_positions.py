import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.position import Position
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    device_id: int | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    id: int | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["deviceId"] = device_id

    json_from_: str | Unset = UNSET
    if not isinstance(from_, Unset):
        json_from_ = from_.isoformat()
    params["from"] = json_from_

    json_to: str | Unset = UNSET
    if not isinstance(to, Unset):
        json_to = to.isoformat()
    params["to"] = json_to

    params["id"] = id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/positions",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> list[Position] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Position.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[list[Position]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    device_id: int | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    id: int | Unset = UNSET,
) -> Response[list[Position]]:
    """Fetches a list of Positions

     We strongly recommend using [Traccar WebSocket API](https://www.traccar.org/traccar-api/) instead of
    periodically polling positions endpoint. Without any params, it returns a list of last known
    positions for all the user's Devices. _from_ and _to_ fields are not required with _id_.

    Args:
        device_id (int | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[Position]]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        from_=from_,
        to=to,
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    device_id: int | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    id: int | Unset = UNSET,
) -> list[Position] | None:
    """Fetches a list of Positions

     We strongly recommend using [Traccar WebSocket API](https://www.traccar.org/traccar-api/) instead of
    periodically polling positions endpoint. Without any params, it returns a list of last known
    positions for all the user's Devices. _from_ and _to_ fields are not required with _id_.

    Args:
        device_id (int | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[Position]
    """

    return sync_detailed(
        client=client,
        device_id=device_id,
        from_=from_,
        to=to,
        id=id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    device_id: int | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    id: int | Unset = UNSET,
) -> Response[list[Position]]:
    """Fetches a list of Positions

     We strongly recommend using [Traccar WebSocket API](https://www.traccar.org/traccar-api/) instead of
    periodically polling positions endpoint. Without any params, it returns a list of last known
    positions for all the user's Devices. _from_ and _to_ fields are not required with _id_.

    Args:
        device_id (int | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[Position]]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        from_=from_,
        to=to,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    device_id: int | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    id: int | Unset = UNSET,
) -> list[Position] | None:
    """Fetches a list of Positions

     We strongly recommend using [Traccar WebSocket API](https://www.traccar.org/traccar-api/) instead of
    periodically polling positions endpoint. Without any params, it returns a list of last known
    positions for all the user's Devices. _from_ and _to_ fields are not required with _id_.

    Args:
        device_id (int | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[Position]
    """

    return (
        await asyncio_detailed(
            client=client,
            device_id=device_id,
            from_=from_,
            to=to,
            id=id,
        )
    ).parsed
