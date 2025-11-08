import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.event import Event
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    device_id: list[int] | Unset = UNSET,
    group_id: list[int] | Unset = UNSET,
    type_: list[str] | Unset = UNSET,
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

    json_type_: list[str] | Unset = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_

    params["type"] = json_type_

    json_from_ = from_.isoformat()
    params["from"] = json_from_

    json_to = to.isoformat()
    params["to"] = json_to

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/reports/events",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> list[Event] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Event.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[list[Event]]:
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
    type_: list[str] | Unset = UNSET,
    from_: datetime.datetime,
    to: datetime.datetime,
) -> Response[list[Event]]:
    """Fetch a list of Events within the time period for the Devices or Groups

     At least one _deviceId_ or one _groupId_ must be passed

    Args:
        device_id (list[int] | Unset):
        group_id (list[int] | Unset):
        type_ (list[str] | Unset):
        from_ (datetime.datetime):
        to (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[Event]]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        group_id=group_id,
        type_=type_,
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
    type_: list[str] | Unset = UNSET,
    from_: datetime.datetime,
    to: datetime.datetime,
) -> list[Event] | None:
    """Fetch a list of Events within the time period for the Devices or Groups

     At least one _deviceId_ or one _groupId_ must be passed

    Args:
        device_id (list[int] | Unset):
        group_id (list[int] | Unset):
        type_ (list[str] | Unset):
        from_ (datetime.datetime):
        to (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[Event]
    """

    return sync_detailed(
        client=client,
        device_id=device_id,
        group_id=group_id,
        type_=type_,
        from_=from_,
        to=to,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    device_id: list[int] | Unset = UNSET,
    group_id: list[int] | Unset = UNSET,
    type_: list[str] | Unset = UNSET,
    from_: datetime.datetime,
    to: datetime.datetime,
) -> Response[list[Event]]:
    """Fetch a list of Events within the time period for the Devices or Groups

     At least one _deviceId_ or one _groupId_ must be passed

    Args:
        device_id (list[int] | Unset):
        group_id (list[int] | Unset):
        type_ (list[str] | Unset):
        from_ (datetime.datetime):
        to (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[Event]]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        group_id=group_id,
        type_=type_,
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
    type_: list[str] | Unset = UNSET,
    from_: datetime.datetime,
    to: datetime.datetime,
) -> list[Event] | None:
    """Fetch a list of Events within the time period for the Devices or Groups

     At least one _deviceId_ or one _groupId_ must be passed

    Args:
        device_id (list[int] | Unset):
        group_id (list[int] | Unset):
        type_ (list[str] | Unset):
        from_ (datetime.datetime):
        to (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[Event]
    """

    return (
        await asyncio_detailed(
            client=client,
            device_id=device_id,
            group_id=group_id,
            type_=type_,
            from_=from_,
            to=to,
        )
    ).parsed
