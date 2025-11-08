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
    device_id: list[int] | Unset = UNSET,
    group_id: list[int] | Unset = UNSET,
    from_: datetime.datetime,
    to: datetime.datetime,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_device_id: list[int] | Unset = UNSET
    if not isinstance(device_id, Unset):
        json_device_id = device_id

    params["deviceId"] = json_device_id

    json_group_id: list[int] | Unset = UNSET
    if not isinstance(group_id, Unset):
        json_group_id = group_id

    params["groupId"] = json_group_id

    json_from_ = from_.isoformat()
    params["from"] = json_from_

    json_to = to.isoformat()
    params["to"] = json_to

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/reports/route",
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
    device_id: list[int] | Unset = UNSET,
    group_id: list[int] | Unset = UNSET,
    from_: datetime.datetime,
    to: datetime.datetime,
) -> Response[list[Position]]:
    """Fetch a list of Positions within the time period for the Devices or Groups

     At least one _deviceId_ or one _groupId_ must be passed

    Args:
        device_id (list[int] | Unset):
        group_id (list[int] | Unset):
        from_ (datetime.datetime):
        to (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[Position]]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        group_id=group_id,
        from_=from_,
        to=to,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    device_id: list[int] | Unset = UNSET,
    group_id: list[int] | Unset = UNSET,
    from_: datetime.datetime,
    to: datetime.datetime,
) -> list[Position] | None:
    """Fetch a list of Positions within the time period for the Devices or Groups

     At least one _deviceId_ or one _groupId_ must be passed

    Args:
        device_id (list[int] | Unset):
        group_id (list[int] | Unset):
        from_ (datetime.datetime):
        to (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[Position]
    """

    return sync_detailed(
        client=client,
        device_id=device_id,
        group_id=group_id,
        from_=from_,
        to=to,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    device_id: list[int] | Unset = UNSET,
    group_id: list[int] | Unset = UNSET,
    from_: datetime.datetime,
    to: datetime.datetime,
) -> Response[list[Position]]:
    """Fetch a list of Positions within the time period for the Devices or Groups

     At least one _deviceId_ or one _groupId_ must be passed

    Args:
        device_id (list[int] | Unset):
        group_id (list[int] | Unset):
        from_ (datetime.datetime):
        to (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[Position]]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        group_id=group_id,
        from_=from_,
        to=to,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    device_id: list[int] | Unset = UNSET,
    group_id: list[int] | Unset = UNSET,
    from_: datetime.datetime,
    to: datetime.datetime,
) -> list[Position] | None:
    """Fetch a list of Positions within the time period for the Devices or Groups

     At least one _deviceId_ or one _groupId_ must be passed

    Args:
        device_id (list[int] | Unset):
        group_id (list[int] | Unset):
        from_ (datetime.datetime):
        to (datetime.datetime):

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
            group_id=group_id,
            from_=from_,
            to=to,
        )
    ).parsed
