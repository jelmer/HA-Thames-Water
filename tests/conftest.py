"""Fixtures for the Thames Water integration tests."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Generator
from unittest.mock import patch

import pytest
import requests


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Let Home Assistant load `custom_components` during a test.

    Home Assistant refuses to load a custom integration unless a test asks
    for it, and a test that sets an entry up has no other way to say so.
    """
    yield


def _canned_response(request: requests.PreparedRequest) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response.url = request.url or ""
    response.request = request
    response._content = b"{}"
    return response


@pytest.fixture
def guarded_http() -> Generator[None]:
    """Answer the library's requests, and refuse the ones on the event loop.

    `thameswaterapi` talks over `requests`, which blocks, so every call into
    it belongs in an executor. Reaching this transport with a loop running in
    the calling thread means one did not, which is the fault #32 fixed in the
    config flow.

    A mocked client cannot show that fault, because the mock replaces the
    blocking work itself. A test wanting this guard therefore drives a real
    `ThamesWater` and fakes the HTTP underneath it.
    """
    guard: Callable[..., requests.Response] = _send_unless_on_the_loop
    with patch("requests.adapters.HTTPAdapter.send", guard):
        yield


def _send_unless_on_the_loop(
    adapter: requests.adapters.HTTPAdapter,
    request: requests.PreparedRequest,
    **kwargs: object,
) -> requests.Response:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return _canned_response(request)
    raise AssertionError(
        f"{request.url} was fetched from the event loop; "
        "the call belongs in async_add_executor_job"
    )
