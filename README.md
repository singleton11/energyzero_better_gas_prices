# Hacs component: EnergyZero Better Gas Prices

When you live in the Netherlands and you use Tibber as a provider of electricity + gas, gas is provided by an external 
partner (EnergyZero). And there is a core EnergyZero integration in home assistant. But the gas prices don't include the
purchase cost and the taxes.

So this component uses new EnergyZero GraphQL API to get the gas prices with all the data included.

The component exposes handful of sensors for current and the next day gas prices.

The handful for every time perios is:

- market price (from exchange)
- purchase cost
- energy tax
- total

## Price history

The four current-day price sensors provide Home Assistant long-term statistics (hourly
minimum, maximum, and mean), so their history can remain visible after the recorder
purges detailed states. The next-day sensors are forecasts and do not provide
long-term statistics. Previously purged history cannot be recovered by installing
this update; statistics are collected from new readings onward. Home Assistant's
recorder must be enabled and must not exclude these sensors.

## Installation

- Add custom repository to your HACS: https://github.com/singleton11/enegryzero_better_gas_prices
- Install the component
- Enjoy and have fun!
