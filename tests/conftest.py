"""Fixtures for the Thames Water integration tests."""

from __future__ import annotations

from collections.abc import Generator

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Let Home Assistant load `custom_components` during a test.

    Home Assistant refuses to load a custom integration unless a test asks
    for it, and a test that sets an entry up has no other way to say so.
    """
    yield
