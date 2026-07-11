# Architecture

## Overview

```text
Django templates and pages
→ Django views
→ Transaction database
→ AI core
→ Forecast model
→ Anomaly model
→ Alert service
→ Notification service
→ Alert detail and workflow history
```

## Main Layers

- **Frontend layer**: Django templates, CSS, and JavaScript render dashboards, alerts, transactions, metrics, and data-quality pages.
- **View layer**: Django views handle login, transaction save, alert review, forecasting screens, and status coordination.
- **Data layer**: SQLite stores agents, providers, balances, transactions, forecasts, alerts, evidence, history, and notifications.
- **AI core**: `ai_core.engine` orchestrates anomaly detection, liquidity forecasting, alert creation, and notification creation.
- **Forecast layer**: `analytics.forecasting` calculates shortage probability, projected balance, estimated shortage time, and confidence.
- **Anomaly layer**: `ai_core.model_predictor` and `analytics.anomaly_detection` identify suspicious cash-out and transaction patterns.
- **Alert service**: `alerts.services` creates liquidity alerts, combined alerts, and in-app/email notifications.
- **Workflow layer**: `alerts.views` manages owner assignment, status transitions, history, and human review.

## Request Flow

1. A user signs in.
2. A transaction is created or edited.
3. The transaction is saved.
4. The anomaly model runs.
5. The liquidity forecast runs.
6. The alert service creates or updates an alert if risk is high.
7. The notification service creates an in-app notification and, for higher severities, sends email.
8. The alert detail page records owner changes, assignment, acknowledgement, escalation, and resolution.

## Safety Design

- No automatic money transfer happens.
- No account blocking happens.
- The system stays advisory and human-reviewed.
- Unusual activity is described carefully and never as proven fraud.
