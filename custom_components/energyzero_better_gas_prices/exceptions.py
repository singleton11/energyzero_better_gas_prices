"""Exceptions for the EnergyZero Better Gas Prices integration."""

from homeassistant.exceptions import HomeAssistantError


class ConfigEntryAuthFailed(HomeAssistantError):
    """Exception to indicate authentication failed."""


class ConfigEntryNotReady(HomeAssistantError):
    """Exception to indicate integration is not ready yet."""


class ConfigEntryError(HomeAssistantError):
    """Exception to indicate a generic configuration entry error."""
