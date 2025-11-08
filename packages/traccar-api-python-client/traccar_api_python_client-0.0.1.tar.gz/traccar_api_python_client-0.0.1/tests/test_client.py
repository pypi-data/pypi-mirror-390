# tests/test_client.py

import httpx
import pytest

from src.traccar_api_client.client import Client


def test_client_initialization():
    client = Client(
        base_url="https://traccar.test.com",
        cookies={"session": "abc123"},
        headers={"User-Agent": "TestClient"},
        timeout=httpx.Timeout(10.0),
        verify_ssl=False,
        follow_redirects=True,
        raise_on_unexpected_status=True,
    )
    assert client._base_url == "https://traccar.test.com"
    assert client._cookies == {"session": "abc123"}
    assert client._headers == {"User-Agent": "TestClient"}
    assert client._timeout.connect == 10.0
    assert client._verify_ssl is False
    assert client._follow_redirects is True
    assert client.raise_on_unexpected_status is True


def test_with_headers():
    client = Client(base_url="https://traccar.test.com", headers={"User-Agent": "TestClient"})
    updated_client = client.with_headers({"Authorization": "Bearer token123"})
    assert client._headers == {"User-Agent": "TestClient"}
    assert updated_client._headers == {"User-Agent": "TestClient", "Authorization": "Bearer token123"}


def test_with_cookies():
    client = Client(base_url="https://traccar.test.com", cookies={"session": "abc123"})
    updated_client = client.with_cookies({"auth": "token123"})
    assert client._cookies == {"session": "abc123"}
    assert updated_client._cookies == {"session": "abc123", "auth": "token123"}


def test_with_timeout():
    client = Client(base_url="https://traccar.test.com", timeout=httpx.Timeout(5.0))
    updated_client = client.with_timeout(httpx.Timeout(10.0))
    assert client._timeout.connect == 5.0
    assert updated_client._timeout.connect == 10.0


def test_get_httpx_client():
    client = Client(base_url="https://traccar.test.com")
    httpx_client = client.get_httpx_client()
    assert isinstance(httpx_client, httpx.Client)
    assert httpx_client.base_url == "https://traccar.test.com"


def test_set_httpx_client():
    client = Client(base_url="https://traccar.test.com")
    external_client = httpx.Client(base_url="https://gps.something.com")
    client.set_httpx_client(external_client)
    assert client._client is external_client
    assert client._client.base_url == "https://gps.something.com"
