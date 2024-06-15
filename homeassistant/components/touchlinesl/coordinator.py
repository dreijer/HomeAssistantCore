"""Coordinator for Touchlines SL."""

from __future__ import annotations

from datetime import timedelta
import logging

import TouchlineSLAPI

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class TouchlineSLCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from Touchline SL."""

    def __init__(self, hass: HomeAssistant, touchlinesl_connector, module_udid) -> None:
        """Initialize the TouchlineSL API coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Touchline SL device",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self._touchlinesl_connector = touchlinesl_connector
        self._module_udid = module_udid

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            return await self._touchlinesl_connector.async_get_zones(self._module_udid)
        except TouchlineSLAPI.TouchlineSLAuthException as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            raise UpdateFailed(err) from err
