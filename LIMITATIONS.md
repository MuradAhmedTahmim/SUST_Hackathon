# Limitations

## Current limitations

- The project is a hackathon prototype and is not production-hardened.
- The demo database uses SQLite.
- Provider data is simulated rather than pulled from live APIs.
- Forecasting accuracy depends on the amount of synthetic history available.
- The anomaly fallback is deliberately conservative and heuristic when training artifacts are unavailable.
- Metrics are calculated from the current dataset and synthetic assumptions.
- Production deployment still needs stronger secret management and monitoring.

## Known gaps

- Email delivery may need real SMTP configuration for a public deployment.
- Alert ownership and assignment can still be refined for role-based routing.
- More labelled data would improve the validation metrics.
- A dedicated production model registry is not yet implemented.

## Why these limitations are acceptable for the hackathon

- The workflow is complete and explainable.
- The system remains advisory and safe.
- The demo can show forecasting, anomaly review, alert coordination, notifications, and metrics without external AI services.
