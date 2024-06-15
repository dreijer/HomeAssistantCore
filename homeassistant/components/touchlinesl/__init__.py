"""The Roth Touchline SL integration."""

from __future__ import annotations

from datetime import timedelta

import TouchlineSLAPI

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import TOUCHLINESL_DOMAIN

PLATFORMS = [Platform.CLIMATE]

CONFIG_SCHEMA = cv.removed(TOUCHLINESL_DOMAIN, raise_if_present=False)

MIN_TIME_BETWEEN_DEVICE_UPDATES = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Roth Touchline SL from a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    touchlinesl_connector = TouchlineSLAPI.TouchlineSLAPI(username, password)

    # Store an API object for the  platform to use.
    hass.data.setdefault(TOUCHLINESL_DOMAIN, {}).update(
        {entry.entry_id: touchlinesl_connector}
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[TOUCHLINESL_DOMAIN].pop(entry.entry_id)

    return unload_ok
