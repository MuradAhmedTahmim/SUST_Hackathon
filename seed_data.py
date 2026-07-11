from decimal import Decimal
from django.utils import timezone

from agents.models import (
    Provider,
    Area,
    Agent,
    AgentProviderBalance,
)
from transactions.models import Transaction
from alerts.models import Alert, AlertEvidence
from analytics.models import (
    LiquidityForecast,
    ValidationMetric,
)


# --------------------------------------------------
# Provider
# --------------------------------------------------

provider, _ = Provider.objects.get_or_create(
    code="BKASH",
    defaults={
        "name": "bKash",
        "is_active": True,
    },
)


# --------------------------------------------------
# Area
# --------------------------------------------------

area, _ = Area.objects.get_or_create(
    name="Dhaka North",
    defaults={
        "district": "Dhaka",
    },
)


# --------------------------------------------------
# Agent
# --------------------------------------------------

agent, _ = Agent.objects.get_or_create(
    agent_code="AG-001",
    defaults={
        "outlet_name": "Badhan Telecom",
        "area": area,
        "physical_cash": Decimal("50000.00"),
        "safety_cash_threshold": Decimal("10000.00"),
    },
)


# --------------------------------------------------
# Provider balance / Data Quality
# --------------------------------------------------

balance, _ = AgentProviderBalance.objects.update_or_create(
    agent=agent,
    provider=provider,
    defaults={
        "current_balance": Decimal("12000.00"),
        "safety_threshold": Decimal("10000.00"),
        "data_timestamp": timezone.now(),
        "data_status": "FRESH",
    },
)


# --------------------------------------------------
# Normal transaction
# --------------------------------------------------

Transaction.objects.update_or_create(
    transaction_reference="TXN-1001",
    defaults={
        "agent": agent,
        "provider": provider,
        "transaction_type": "CASH_IN",
        "amount": Decimal("5000.00"),
        "status": "SUCCESS",
        "occurred_at": timezone.now(),
        "synthetic_customer_id": "CUS-001",
        "is_injected_anomaly": False,
    },
)


# --------------------------------------------------
# Anomaly transactions
# --------------------------------------------------

Transaction.objects.update_or_create(
    transaction_reference="TXN-ANOM-001",
    defaults={
        "agent": agent,
        "provider": provider,
        "transaction_type": "CASH_OUT",
        "amount": Decimal("45000.00"),
        "status": "SUCCESS",
        "occurred_at": timezone.now(),
        "synthetic_customer_id": "CUS-ANOM-001",
        "is_injected_anomaly": True,
    },
)

Transaction.objects.update_or_create(
    transaction_reference="TXN-ANOM-002",
    defaults={
        "agent": agent,
        "provider": provider,
        "transaction_type": "CASH_OUT",
        "amount": Decimal("38000.00"),
        "status": "SUCCESS",
        "occurred_at": timezone.now(),
        "synthetic_customer_id": "CUS-ANOM-002",
        "is_injected_anomaly": True,
    },
)


# --------------------------------------------------
# Alerts
# --------------------------------------------------

alert1, _ = Alert.objects.update_or_create(
    alert_code="ALT-001",
    defaults={
        "agent": agent,
        "provider": provider,
        "alert_type": "LIQUIDITY_PRESSURE",
        "severity": "CRITICAL",
        "confidence": 94.5,
        "title": "Critical bKash liquidity shortage",
        "explanation": (
            "The projected bKash balance is expected to fall "
            "below the configured safety threshold."
        ),
        "recommended_action": (
            "Add provider liquidity immediately and review "
            "recent cash-out activity."
        ),
        "status": "NEW",
    },
)

AlertEvidence.objects.get_or_create(
    alert=alert1,
    label="Current balance",
    defaults={
        "value": "৳12,000",
    },
)

AlertEvidence.objects.get_or_create(
    alert=alert1,
    label="Safety threshold",
    defaults={
        "value": "৳10,000",
    },
)


alert2, _ = Alert.objects.update_or_create(
    alert_code="ALT-002",
    defaults={
        "agent": agent,
        "provider": provider,
        "alert_type": "VELOCITY_ANOMALY",
        "severity": "HIGH",
        "confidence": 87.0,
        "title": "Unusual transaction velocity detected",
        "explanation": (
            "Several high-value cash-out transactions were "
            "recorded in a short period."
        ),
        "recommended_action": (
            "Review the flagged transactions and contact the agent."
        ),
        "status": "INVESTIGATING",
    },
)


alert3, _ = Alert.objects.update_or_create(
    alert_code="ALT-003",
    defaults={
        "agent": agent,
        "provider": provider,
        "alert_type": "REPEATED_AMOUNT",
        "severity": "MEDIUM",
        "confidence": 76.5,
        "title": "Repeated transaction amount pattern",
        "explanation": (
            "Multiple transactions with similar amounts were detected."
        ),
        "recommended_action": (
            "Verify whether the transactions represent genuine activity."
        ),
        "status": "RESOLVED",
        "resolved_at": timezone.now(),
    },
)


# --------------------------------------------------
# Forecast
# --------------------------------------------------

LiquidityForecast.objects.create(
    agent=agent,
    provider=provider,
    forecast_type="PROVIDER_BALANCE",
    forecast_hours=2,
    current_balance=Decimal("12000.00"),
    predicted_demand=Decimal("18000.00"),
    projected_balance=Decimal("-6000.00"),
    safety_threshold=Decimal("10000.00"),
    shortage_probability=96.0,
    confidence=91.0,
    estimated_shortage_at=timezone.now(),
    explanation=(
        "Based on recent cash-out activity, the provider balance "
        "is likely to fall below the safety threshold."
    ),
)


# --------------------------------------------------
# Validation metrics
# --------------------------------------------------

metrics = [
    {
        "metric_type": "FORECAST_MAE",
        "value": 4.8,
        "unit": "%",
        "description": "Average forecast prediction error.",
    },
    {
        "metric_type": "SHORTAGE_LEAD_TIME",
        "value": 2.4,
        "unit": "hours",
        "description": "Average warning time before liquidity shortage.",
    },
    {
        "metric_type": "ANOMALY_PRECISION",
        "value": 91.5,
        "unit": "%",
        "description": "Percentage of flagged anomalies that were correct.",
    },
    {
        "metric_type": "ANOMALY_RECALL",
        "value": 88.2,
        "unit": "%",
        "description": "Percentage of true anomalies successfully detected.",
    },
    {
        "metric_type": "FALSE_POSITIVE_RATE",
        "value": 6.3,
        "unit": "%",
        "description": "Percentage of normal records incorrectly flagged.",
    },
    {
        "metric_type": "EXPLANATION_COVERAGE",
        "value": 97.0,
        "unit": "%",
        "description": "Alerts containing a human-readable explanation.",
    },
    {
        "metric_type": "API_LATENCY",
        "value": 128,
        "unit": "ms",
        "description": "Average backend API response time.",
    },
    {
        "metric_type": "ALERT_OWNERSHIP",
        "value": 84.0,
        "unit": "%",
        "description": "Percentage of alerts assigned to an owner.",
    },
]

for item in metrics:
    ValidationMetric.objects.create(**item)


print("Sample AgentPulse data created successfully.")