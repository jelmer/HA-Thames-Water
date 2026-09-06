"""Tests for the fixture that keeps blocking HTTP off the event loop."""

from __future__ import annotations

import pytest
import requests
from homeassistant.core import HomeAssistant


def _fetch() -> requests.Response:
    """Stand in for a `thameswaterapi` call, which reaches the same transport."""
    return requests.get("http://example.invalid/", timeout=1)


async def test_a_call_on_the_event_loop_fails(
    hass: HomeAssistant, guarded_http: None
) -> None:
    with pytest.raises(AssertionError, match="event loop"):
        _fetch()


async def test_the_same_call_through_an_executor_passes(
    hass: HomeAssistant, guarded_http: None
) -> None:
    response = await hass.async_add_executor_job(_fetch)
    assert response.status_code == 200
