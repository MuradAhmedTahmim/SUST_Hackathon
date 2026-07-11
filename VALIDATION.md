# Validation

## Test coverage

Current automated checks were run on the workflow slices that matter for the demo.

- Alerts test suite: 9 tests passed, 0 failures
- Transaction workflow test suite: 2 tests passed, 0 failures

## Verified workflow behavior

- Successful transaction creation creates a notification.
- Large recent cash-out transactions are flagged as anomalous by the fallback predictor.
- Liquidity forecasts are created from recent balance and transaction data.
- High-risk liquidity pressure creates an alert.
- Alert history and review workflow remain intact.

## Live demo metrics from the current database

Workflow metrics:

- Average shortage lead time: 0 min
- Injected anomalies detected: 43
- Alerts with explanations: 100.0%
- Average acknowledgement time: 0.0 min

Validation metrics:

- Forecast MAE: 2571.43 amount
- Anomaly precision: 9.3%
- Anomaly recall: 88.2%
- False-positive rate: 5.4%
- Explanation coverage: 100.0%
- API latency: 0.0 ms
- Alert ownership: 0.0%

## How to refresh metrics

Run the Django metrics dashboard or the helper in `analytics.metrics_service` to recalculate the stored validation rows from the current database.
