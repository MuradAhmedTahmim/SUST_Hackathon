# Data and Simulation

## Data Source

All operational data in this project is synthetic or simulated for hackathon use.

## What is simulated

- Agent identities and outlet names
- Provider records such as bKash, Nagad, Rocket, Upay, and SureCash
- Shared physical cash balances
- Provider-specific electronic balances
- Transaction histories
- Repeated-amount anomalies
- High-velocity transaction bursts
- Delayed, missing, and conflicting provider balance states
- Alerts, evidence, histories, and notifications

## Synthetic transaction design

- Customer IDs are synthetic and do not correspond to real people.
- Cash-in and cash-out values are fabricated for demo and testing.
- Large cash-out scenarios are used to demonstrate liquidity pressure.
- Some transactions are injected as anomaly examples for review workflows.

## Anomaly injection approach

Anomalies are simulated by either:

- setting a transaction as injected in seed/demo data,
- generating repeated near-identical amounts in a short window, or
- creating unusually large cash-out activity that exceeds the normal threshold.

## Assumptions

- Provider balances are independent per provider.
- Shared physical cash is separate from provider balances.
- Forecasting uses recent transaction patterns and current balances.
- Data-quality status affects confidence and recommendation strength.
- Missing or conflicting provider data should not produce a confident recommendation.

## Demo philosophy

The dataset is designed to show realistic workflow behavior, not to model a real financial institution.
