from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.group import Group
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    all_: bool | Unset = UNSET,
    user_id: int | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["all"] = all_

    params["userId"] = user_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/groups",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> list[Group] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Group.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[list[Group]]:
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
) -> Response[list[Group]]:
    """Fetch a list of Groups

     Without any params, returns a list of the Groups the user belongs to

    Args:
        all_ (bool | Unset):
        user_id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[Group]]
    """

    kwargs = _get_kwargs(
        all_=all_,
        user_id=user_id,
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
) -> list[Group] | None:
    """Fetch a list of Groups

     Without any params, returns a list of the Groups the user belongs to

    Args:
        all_ (bool | Unset):
        user_id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[Group]
    """

    return sync_detailed(
        client=client,
        all_=all_,
        user_id=user_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    all_: bool | Unset = UNSET,
    user_id: int | Unset = UNSET,
) -> Response[list[Group]]:
    """Fetch a list of Groups

     Without any params, returns a list of the Groups the user belongs to

    Args:
        all_ (bool | Unset):
        user_id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[Group]]
    """

    kwargs = _get_kwargs(
        all_=all_,
        user_id=user_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    all_: bool | Unset = UNSET,
    user_id: int | Unset = UNSET,
) -> list[Group] | None:
    """Fetch a list of Groups

     Without any params, returns a list of the Groups the user belongs to

    Args:
        all_ (bool | Unset):
        user_id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[Group]
    """

    return (
        await asyncio_detailed(
            client=client,
            all_=all_,
            user_id=user_id,
        )
    ).parsed
