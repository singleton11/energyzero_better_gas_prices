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

## Installation

- Add custom repository to your HACS: https://github.com/singleton11/enegryzero_better_gas_prices
- Install the component
- Enjoy and have fun!
