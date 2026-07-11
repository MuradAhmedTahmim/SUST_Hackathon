import uuid

from alerts.models import Alert, AlertEvidence


def _normalize_probability(value):
    if value is None:
        return 0.0

    value = float(value)

    if value > 1:
        return max(min(value / 100.0, 1.0), 0.0)

    return max(min(value, 1.0), 0.0)


def create_liquidity_alert(
    agent,
    provider,
    forecast,
):
    existing_alert = Alert.objects.filter(
        agent=agent,
        provider=provider,
        alert_type="LIQUIDITY_PRESSURE",
        status__in=[
            "NEW",
            "ASSIGNED",
            "ACKNOWLEDGED",
            "INVESTIGATING",
            "ESCALATED",
        ],
    ).first()

    if existing_alert:
        return existing_alert

    shortage_probability = _normalize_probability(
        forecast.shortage_probability
    )

    if shortage_probability < 0.5:
        return None

    if shortage_probability >= 0.9:
        severity = "CRITICAL"
    elif shortage_probability >= 0.6:
        severity = "HIGH"
    else:
        severity = "MEDIUM"

    title = (
        "Possible Nagad liquidity shortage"
        if provider.name and provider.name.lower() == "nagad"
        else f"{provider.name} liquidity pressure"
    )

    alert = Alert.objects.create(
        alert_code=f"ALT-{uuid.uuid4().hex[:8].upper()}",
        agent=agent,
        provider=provider,
        alert_type="LIQUIDITY_PRESSURE",
        severity=severity,
        confidence=forecast.confidence,
        title=title,
        explanation=(
            f"The projected provider balance is "
            f"৳{forecast.projected_balance:,.2f}. "
            "The estimate is advisory and requires "
            "human review."
        ),
        recommended_action=(
            "Verify the latest provider balance and contact the "
            "authorized field officer to arrange approved liquidity support."
        ),
        status="NEW",
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
            label="Projected balance",
            value=f"৳{forecast.projected_balance:,.2f}",
        ),
        AlertEvidence(
            alert=alert,
            label="Confidence",
            value=f"{forecast.confidence * 100:.0f}%",
        ),
    ])

    return alert