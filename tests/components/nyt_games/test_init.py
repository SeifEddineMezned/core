"""Tests for the NYT Games integration."""

from unittest.mock import AsyncMock

from nyt_games import NYTGamesAuthenticationError
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.nyt_games.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from . import setup_integration

from tests.common import MockConfigEntry


async def test_device_info(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_nyt_games_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
    device_registry: dr.DeviceRegistry,
) -> None:
    """Test device registry integration."""
    await setup_integration(hass, mock_config_entry)
    for entity in ("wordle", "spelling_bee", "connections"):
        device_entry = device_registry.async_get_device(
            identifiers={(DOMAIN, f"{mock_config_entry.unique_id}_{entity}")}
        )
        assert device_entry is not None
        assert device_entry == snapshot(name=f"device_{entity}")


async def test_auth_error_triggers_reauth(
    hass: HomeAssistant,
    mock_nyt_games_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that an authentication error triggers a reauth flow."""
    mock_nyt_games_client.get_latest_stats.side_effect = NYTGamesAuthenticationError
    await setup_integration(hass, mock_config_entry)

    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    flows = hass.config_entries.flow.async_progress()
    assert len(flows) == 1
    assert flows[0]["handler"] == DOMAIN
    assert flows[0]["context"]["source"] == "reauth"
