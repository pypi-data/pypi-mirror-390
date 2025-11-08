from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.device import Device
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    all_: bool | Unset = UNSET,
    user_id: int | Unset = UNSET,
    id: int | Unset = UNSET,
    unique_id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["all"] = all_

    params["userId"] = user_id

    params["id"] = id

    params["uniqueId"] = unique_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/devices",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | list[Device] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Device.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | list[Device]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    all_: bool | Unset = UNSET,
    user_id: int | Unset = UNSET,
    id: int | Unset = UNSET,
    unique_id: str | Unset = UNSET,
) -> Response[Any | list[Device]]:
    """Fetch a list of Devices

     Without any params, returns a list of the user's devices

    Args:
        all_ (bool | Unset):
        user_id (int | Unset):
        id (int | Unset):
        unique_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | list[Device]]
    """

    kwargs = _get_kwargs(
        all_=all_,
        user_id=user_id,
        id=id,
        unique_id=unique_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    all_: bool | Unset = UNSET,
    user_id: int | Unset = UNSET,
    id: int | Unset = UNSET,
    unique_id: str | Unset = UNSET,
) -> Any | list[Device] | None:
    """Fetch a list of Devices

     Without any params, returns a list of the user's devices

    Args:
        all_ (bool | Unset):
        user_id (int | Unset):
        id (int | Unset):
        unique_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | list[Device]
    """

    return sync_detailed(
        client=client,
        all_=all_,
        user_id=user_id,
        id=id,
        unique_id=unique_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    all_: bool | Unset = UNSET,
    user_id: int | Unset = UNSET,
    id: int | Unset = UNSET,
    unique_id: str | Unset = UNSET,
) -> Response[Any | list[Device]]:
    """Fetch a list of Devices

     Without any params, returns a list of the user's devices

    Args:
        all_ (bool | Unset):
        user_id (int | Unset):
        id (int | Unset):
        unique_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | list[Device]]
    """

    kwargs = _get_kwargs(
        all_=all_,
        user_id=user_id,
        id=id,
        unique_id=unique_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    all_: bool | Unset = UNSET,
    user_id: int | Unset = UNSET,
    id: int | Unset = UNSET,
    unique_id: str | Unset = UNSET,
) -> Any | list[Device] | None:
    """Fetch a list of Devices

     Without any params, returns a list of the user's devices

    Args:
        all_ (bool | Unset):
        user_id (int | Unset):
        id (int | Unset):
        unique_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | list[Device]
    """

    return (
        await asyncio_detailed(
            client=client,
            all_=all_,
            user_id=user_id,
            id=id,
            unique_id=unique_id,
        )
    ).parsed
