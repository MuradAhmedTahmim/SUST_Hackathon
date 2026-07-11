import uuid

from alerts.models import Alert, AlertEvidence


def create_liquidity_alert(
    agent,
    provider,
    forecast,
):
    if forecast.shortage_probability < 0.5:
        return None

    if forecast.shortage_probability >= 0.9:
        severity = "CRITICAL"
    elif forecast.shortage_probability >= 0.7:
        severity = "HIGH"
    else:
        severity = "MEDIUM"

    alert = Alert.objects.create(
        alert_code=f"ALT-{uuid.uuid4().hex[:8].upper()}",
        agent=agent,
        provider=provider,
        alert_type="LIQUIDITY_PRESSURE",
        severity=severity,
        confidence=forecast.confidence,
        title=f"{provider.name} liquidity pressure",
        explanation=(
            f"The projected provider balance is "
            f"৳{forecast.projected_balance:,.2f}. "
            "The estimate is advisory and requires "
            "human review."
        ),
        recommended_action=(
            "Verify the current provider balance and "
            "contact the assigned field officer."
        ),
    )

    AlertEvidence.objects.bulk_create([
        AlertEvidence(
            alert=alert,
            label="Current balance",
            value=f"৳{forecast.current_balance:,.2f}",
        ),
        AlertEvidence(
            alert=alert,
            label="Predicted demand",
            value=f"৳{forecast.predicted_demand:,.2f}",
        ),
        AlertEvidence(
            alert=alert,
            label="Confidence",
            value=f"{forecast.confidence * 100:.0f}%",
        ),
    ])

    return alert