"""The EnergyZero Better Gas Prices integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .exceptions import ConfigEntryNotReady

PLATFORMS: list[Platform] = [Platform.SENSOR]


class EnergyZeroBetterGasPricesRuntimeData:
    """Class to hold runtime data for EnergyZero Better Gas Prices."""


type EnergyZeroBetterGasPricesConfigEntry = ConfigEntry[
    EnergyZeroBetterGasPricesRuntimeData
]


async def async_setup_entry(
    hass: HomeAssistant, entry: EnergyZeroBetterGasPricesConfigEntry
) -> bool:
    """Set up EnergyZero Better Gas Prices from a config entry."""
    # Test before setup - simulate a check that could fail
    if not await async_test_connection(hass):
        raise ConfigEntryNotReady("Failed to connect to EnergyZero service")

    entry.runtime_data = EnergyZeroBetterGasPricesRuntimeData()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_test_connection(hass: HomeAssistant) -> bool:
    """Test connection to EnergyZero service.

    This is a placeholder function that would normally test the connection
    to the service before proceeding with setup.

    Returns:
        True if connection is successful, otherwise would return False
        in a real implementation.

    """
    # In a real implementation, this would test the connection
    # For demonstration purposes, we're returning True
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: EnergyZeroBetterGasPricesConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
