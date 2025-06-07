"""Config flow for EnergyZero Better Gas Prices integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EnergyZero Better Gas Prices."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        # Check if integration is already configured
        self._async_abort_entries_match()

        # Since no configuration is needed, create entry immediately
        return self.async_create_entry(title="EnergyZero Better Gas Prices", data={})
