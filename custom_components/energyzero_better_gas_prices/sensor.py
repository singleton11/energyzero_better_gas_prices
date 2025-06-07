"""Sensor platform for EnergyZero Better Gas Prices integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CURRENCY_EURO, UnitOfVolume

from .const import DOMAIN
from .coordinator import EnergyZeroBetterGasPricesCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor platform.

    Args:
        hass: The Home Assistant instance.
        config_entry: The configuration entry for the integration.
        async_add_entities: A callback to add entities to Home Assistant.

    """
    coordinator = EnergyZeroBetterGasPricesCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    entities = [
        # Current day sensors
        EnergyZeroBetterGasMarketPriceSensor(coordinator, config_entry, "current"),
        EnergyZeroBetterGasEnergyTaxSensor(coordinator, config_entry, "current"),
        EnergyZeroBetterGasPurchasingCostSensor(coordinator, config_entry, "current"),
        EnergyZeroBetterGasTotalPriceSensor(coordinator, config_entry, "current"),
        # Next day sensors
        EnergyZeroBetterGasMarketPriceSensor(coordinator, config_entry, "next"),
        EnergyZeroBetterGasEnergyTaxSensor(coordinator, config_entry, "next"),
        EnergyZeroBetterGasPurchasingCostSensor(coordinator, config_entry, "next"),
        EnergyZeroBetterGasTotalPriceSensor(coordinator, config_entry, "next"),
    ]

    async_add_entities(entities)


class EnergyZeroBetterGasPriceBaseSensor(
    CoordinatorEntity[EnergyZeroBetterGasPricesCoordinator], SensorEntity
):
    """Base class for EnergyZero Better Gas Prices sensors."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfVolume.CUBIC_METERS}"
    _attr_icon = "mdi:meter-gas"

    def __init__(
        self,
        coordinator: EnergyZeroBetterGasPricesCoordinator,
        config_entry: ConfigEntry,
        period: str,
        sensor_type: str,
        name_suffix: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._period = period  # "current" or "next"
        self._sensor_type = sensor_type  # "market", "energy_tax", "purchase", "total"
        self._attr_name = f"Better Gas {name_suffix}"
        self._attr_unique_id = f"{DOMAIN}_{period}_{sensor_type}_gas_price"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        data = self.coordinator.data
        if not data:
            return {}

        period_prefix = "current" if self._period == "current" else "next"

        return {
            "last_updated": data.last_updated,
            f"{period_prefix}_from": getattr(data, f"{period_prefix}_from"),
            f"{period_prefix}_till": getattr(data, f"{period_prefix}_till"),
        }

    @property
    def device_info(self):
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "EnergyZero Better Gas Prices",
            "manufacturer": "EnergyZero",
        }


class EnergyZeroBetterGasMarketPriceSensor(EnergyZeroBetterGasPriceBaseSensor):
    """Sensor for EnergyZero Better Gas Market Price."""

    def __init__(
        self,
        coordinator: EnergyZeroBetterGasPricesCoordinator,
        config_entry: ConfigEntry,
        period: str,
    ) -> None:
        """Initialize the sensor."""
        name_suffix = f"{period.capitalize()} Market Price"
        super().__init__(coordinator, config_entry, period, "market", name_suffix)

    @property
    def native_value(self) -> float | None:
        """Return the market price including VAT."""
        if not self.coordinator.data:
            return None

        return getattr(self.coordinator.data, f"{self._period}_market_price_incl")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        if self.coordinator.data:
            attrs["price_excl_vat"] = getattr(
                self.coordinator.data, f"{self._period}_market_price_excl"
            )

        return attrs


class EnergyZeroBetterGasEnergyTaxSensor(EnergyZeroBetterGasPriceBaseSensor):
    """Sensor for EnergyZero Better Gas Energy Tax."""

    def __init__(
        self,
        coordinator: EnergyZeroBetterGasPricesCoordinator,
        config_entry: ConfigEntry,
        period: str,
    ) -> None:
        """Initialize the sensor."""
        name_suffix = f"{period.capitalize()} Energy Tax"
        super().__init__(coordinator, config_entry, period, "energy_tax", name_suffix)

    @property
    def native_value(self) -> float | None:
        """Return the energy tax including VAT."""
        if not self.coordinator.data:
            return None

        return getattr(self.coordinator.data, f"{self._period}_energy_tax_incl")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        if self.coordinator.data:
            attrs["price_excl_vat"] = getattr(
                self.coordinator.data, f"{self._period}_energy_tax_excl"
            )

        return attrs


class EnergyZeroBetterGasPurchasingCostSensor(EnergyZeroBetterGasPriceBaseSensor):
    """Sensor for EnergyZero Better Gas Purchasing Cost."""

    def __init__(
        self,
        coordinator: EnergyZeroBetterGasPricesCoordinator,
        config_entry: ConfigEntry,
        period: str,
    ) -> None:
        """Initialize the sensor."""
        name_suffix = f"{period.capitalize()} Purchasing Cost"
        super().__init__(
            coordinator, config_entry, period, "purchasing_cost", name_suffix
        )

    @property
    def native_value(self) -> float | None:
        """Return the purchasing cost including VAT."""
        if not self.coordinator.data:
            return None

        return getattr(self.coordinator.data, f"{self._period}_purchasing_cost_incl")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        if self.coordinator.data:
            attrs["price_excl_vat"] = getattr(
                self.coordinator.data, f"{self._period}_purchasing_cost_excl"
            )

        return attrs


class EnergyZeroBetterGasTotalPriceSensor(EnergyZeroBetterGasPriceBaseSensor):
    """Sensor for EnergyZero Better Gas Total Price."""

    def __init__(
        self,
        coordinator: EnergyZeroBetterGasPricesCoordinator,
        config_entry: ConfigEntry,
        period: str,
    ) -> None:
        """Initialize the sensor."""
        name_suffix = f"{period.capitalize()} Total Price"
        super().__init__(coordinator, config_entry, period, "total", name_suffix)

    @property
    def native_value(self) -> float | None:
        """Return the total price including VAT."""
        if not self.coordinator.data:
            return None

        return getattr(self.coordinator.data, f"{self._period}_total_price_incl")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        if self.coordinator.data:
            attrs["price_excl_vat"] = getattr(
                self.coordinator.data, f"{self._period}_total_price_excl"
            )
            attrs["market_price_incl_vat"] = getattr(
                self.coordinator.data, f"{self._period}_market_price_incl"
            )
            attrs["market_price_excl_vat"] = getattr(
                self.coordinator.data, f"{self._period}_market_price_excl"
            )
            attrs["energy_tax_incl_vat"] = getattr(
                self.coordinator.data, f"{self._period}_energy_tax_incl"
            )
            attrs["energy_tax_excl_vat"] = getattr(
                self.coordinator.data, f"{self._period}_energy_tax_excl"
            )
            attrs["purchasing_cost_incl_vat"] = getattr(
                self.coordinator.data, f"{self._period}_purchasing_cost_incl"
            )
            attrs["purchasing_cost_excl_vat"] = getattr(
                self.coordinator.data, f"{self._period}_purchasing_cost_excl"
            )

        return attrs
