"""Coordinator for the EnergyZero Better Gas Prices integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .utils import round_monetary_value

_LOGGER = logging.getLogger(__name__)

API_ENDPOINT = "https://api.energyzero.nl/v1/gql"

UPDATE_INTERVAL = timedelta(hours=1)


@dataclass
class GasPriceData:
    """Class to hold gas price data."""

    # Current day data
    current_market_price_excl: float | None = None
    current_market_price_incl: float | None = None
    current_energy_tax_excl: float | None = None
    current_energy_tax_incl: float | None = None
    current_purchasing_cost_excl: float | None = None
    current_purchasing_cost_incl: float | None = None
    current_total_price_excl: float | None = None
    current_total_price_incl: float | None = None

    # Next day data
    next_market_price_excl: float | None = None
    next_market_price_incl: float | None = None
    next_energy_tax_excl: float | None = None
    next_energy_tax_incl: float | None = None
    next_purchasing_cost_excl: float | None = None
    next_purchasing_cost_incl: float | None = None
    next_total_price_excl: float | None = None
    next_total_price_incl: float | None = None

    # Timestamps
    current_from: str | None = None
    current_till: str | None = None
    next_from: str | None = None
    next_till: str | None = None
    last_updated: str | None = None


GAS_PRICE_QUERY = """
query EnergyMarketPricesGas(
  $gasCurrentFrom: Time!
  $gasCurrentTill: Time!
  $gasNextFrom: Time!
  $gasNextTill: Time!
) {
  current: energyMarketPrices(
    input: {
      from: $gasCurrentFrom
      till: $gasCurrentTill
      intervalType: Daily
      type: Gas
    }
  ) {
    averageIncl
    averageExcl
    prices {
      energyPriceExcl
      energyPriceIncl
      from
      isAverage
      till
      type
      vat
      additionalCosts {
        name
        priceExcl
        priceIncl
      }
    }
  }
  next: energyMarketPrices(
    input: {
      from: $gasNextFrom
      till: $gasNextTill
      intervalType: Daily
      type: Gas
    }
  ) {
    averageIncl
    averageExcl
    prices {
      energyPriceExcl
      energyPriceIncl
      from
      isAverage
      till
      type
      vat
      additionalCosts {
        name
        priceExcl
        priceIncl
      }
    }
  }
}
"""


class EnergyZeroBetterGasPricesCoordinator(DataUpdateCoordinator[GasPriceData]):
    """Class to manage fetching EnergyZero Better Gas Prices data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="EnergyZero Better Gas Prices",
            update_interval=UPDATE_INTERVAL,
        )
        self._session = aiohttp.ClientSession()

    def _process_price_data(
        self, price_data: dict, period: str, gas_price_data: GasPriceData
    ) -> None:
        """Process price data for a specific period (current or next).

        Args:
            price_data: The price data from the API response
            period: The period to process ('current' or 'next')
            gas_price_data: The gas price data object to update
        """
        if not price_data or "prices" not in price_data or not price_data["prices"]:
            return

        price = price_data["prices"][0]

        # Set market price (base price)
        setattr(
            gas_price_data,
            f"{period}_market_price_excl",
            round_monetary_value(price.get("energyPriceExcl")),
        )
        setattr(
            gas_price_data,
            f"{period}_market_price_incl",
            round_monetary_value(price.get("energyPriceIncl")),
        )

        # Initialize total price with market price
        total_price_excl = price.get("energyPriceExcl", 0)
        total_price_incl = price.get("energyPriceIncl", 0)

        # Set timestamps
        setattr(gas_price_data, f"{period}_from", price.get("from"))
        setattr(gas_price_data, f"{period}_till", price.get("till"))

        # Process additional costs (energy tax and purchasing cost)
        energy_tax_excl = 0
        energy_tax_incl = 0
        purchasing_cost_excl = 0
        purchasing_cost_incl = 0

        if price.get("additionalCosts"):
            for cost in price["additionalCosts"]:
                cost_name = cost.get("name", "")
                cost_excl = cost.get("priceExcl", 0)
                cost_incl = cost.get("priceIncl", 0)

                # Add to total price
                total_price_excl += cost_excl
                total_price_incl += cost_incl

                # Categorize by name
                if cost_name == "Energy tax":
                    energy_tax_excl = cost_excl
                    energy_tax_incl = cost_incl
                elif cost_name == "Purchasing cost":
                    purchasing_cost_excl = cost_excl
                    purchasing_cost_incl = cost_incl

        # Set all the calculated values
        setattr(
            gas_price_data,
            f"{period}_energy_tax_excl",
            round_monetary_value(energy_tax_excl),
        )
        setattr(
            gas_price_data,
            f"{period}_energy_tax_incl",
            round_monetary_value(energy_tax_incl),
        )
        setattr(
            gas_price_data,
            f"{period}_purchasing_cost_excl",
            round_monetary_value(purchasing_cost_excl),
        )
        setattr(
            gas_price_data,
            f"{period}_purchasing_cost_incl",
            round_monetary_value(purchasing_cost_incl),
        )
        setattr(
            gas_price_data,
            f"{period}_total_price_excl",
            round_monetary_value(total_price_excl),
        )
        setattr(
            gas_price_data,
            f"{period}_total_price_incl",
            round_monetary_value(total_price_incl),
        )

    async def _async_update_data(self) -> GasPriceData:
        """Fetch data from API endpoint."""
        try:
            # Get current and next day timestamps
            now = dt_util.now()
            current_day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            next_day_start = current_day_start + timedelta(days=1)
            day_after_next_start = current_day_start + timedelta(days=2)

            # Format timestamps for the API
            gas_current_from = current_day_start.isoformat()
            gas_current_till = next_day_start.isoformat()
            gas_next_from = next_day_start.isoformat()
            gas_next_till = day_after_next_start.isoformat()

            # Prepare variables for the GraphQL query
            variables = {
                "gasCurrentFrom": gas_current_from,
                "gasCurrentTill": gas_current_till,
                "gasNextFrom": gas_next_from,
                "gasNextTill": gas_next_till,
            }

            # Prepare the request payload
            payload = {
                "query": GAS_PRICE_QUERY,
                "variables": variables,
            }

            # Make the API request
            async with self._session.post(API_ENDPOINT, json=payload) as response:
                if response.status != 200:
                    _LOGGER.error(
                        "Error fetching gas prices: %s %s",
                        response.status,
                        await response.text(),
                    )
                    raise Exception(f"Error fetching gas prices: {response.status}")

                data = await response.json()

                if "errors" in data:
                    _LOGGER.error("GraphQL errors: %s", data["errors"])
                    raise Exception(f"GraphQL errors: {data['errors']}")

                if "data" not in data:
                    _LOGGER.error("No data in response: %s", data)
                    raise Exception("No data in response")

                # Process the response data
                current_data = data["data"]["current"]
                next_data = data["data"]["next"]

                # Initialize the data object
                gas_price_data = GasPriceData(
                    last_updated=dt_util.now().isoformat(),
                )

                # Process current and next day data
                self._process_price_data(current_data, "current", gas_price_data)
                self._process_price_data(next_data, "next", gas_price_data)

                return gas_price_data

        except Exception as ex:
            _LOGGER.error("Error updating gas price data: %s", ex)
            raise

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        await super().async_shutdown()
        if self._session:
            await self._session.close()
