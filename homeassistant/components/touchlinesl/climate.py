"""Platform for Roth Touchline SL floor heating controller."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import TOUCHLINESL_DOMAIN
from .coordinator import TouchlineSLCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE]


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Old way of setting up a platform."""


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Touchline SL devices."""
    touchlinesl_connector = hass.data[TOUCHLINESL_DOMAIN].get(entry.entry_id)

    modules = await touchlinesl_connector.async_get_modules()

    # Get the devices for the first module only.
    module_udid = modules[0]["udid"]

    coordinator = TouchlineSLCoordinator(hass, touchlinesl_connector, module_udid)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    module_zones = coordinator.data

    # Enumerate all the devices.
    async_add_entities(
        [
            TouchlineSLDevice(touchlinesl_connector, coordinator, device)
            for device in module_zones["zones"]["elements"]
        ],
        True,
    )


class TouchlineSLDevice(CoordinatorEntity, ClimateEntity):
    """Representation of a Touchline SL device."""

    _attr_hvac_mode = HVACMode.HEAT
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, touchline_connector, coordinator, device_info) -> None:
        """Initialize the Touchline device."""
        self._api_connector = touchline_connector
        self._coordinator = coordinator
        self._zone_id = device_info["zone"]["id"]
        self._name = None
        self._current_temperature = 0.0
        self._target_temperature = 0.0
        self._current_humidity = 0.0
        self._battery_level = None
        self._signalStrength = None
        self._mode = None
        self._current_operation_mode = HVACMode.HEAT

        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=self._zone_id)

        self._refresh_device_values(device_info)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        updated_state = self.coordinator.data["zones"]["elements"]
        device_info = next(
            (z for z in updated_state if z["zone"]["id"] == self._zone_id), None
        )
        if device_info is None:
            # The zone is no longer available.
            raise HomeAssistantError(
                f"Device for zone {self._zone_id} is no longer available."
            )

        self._refresh_device_values(device_info)

        self.async_write_ha_state()

    def _refresh_device_values(self, device_info) -> None:
        self._name = device_info["description"]["name"]
        self._current_temperature = device_info["zone"]["currentTemperature"] / 10.0
        self._target_temperature = device_info["zone"]["setTemperature"] / 10.0
        self._current_humidity = device_info["zone"]["humidity"]
        self._battery_level = device_info["zone"]["batteryLevel"]
        self._signalStrength = device_info["zone"]["signalStrength"]
        self._mode = device_info["mode"]["mode"]

    @property
    def name(self) -> str | None:
        """Return the name of the climate device."""
        return self._name

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def current_humidity(self) -> float | None:
        """Return the current humidity."""
        return self._current_humidity

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        self._current_operation_mode = HVACMode.HEAT

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        # if kwargs.get(ATTR_TEMPERATURE) is not None:
        #    self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
        # self.unit.set_target_temperature(self._target_temperature)

        # Call the API to set the temperature.

        # Refresh the data.
        await self._coordinator.async_request_refresh()
