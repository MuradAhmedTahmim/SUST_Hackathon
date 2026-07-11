import uuid

from django.conf import settings
from django.core.mail import send_mail

from alerts.models import Alert, AlertEvidence, Notification


def determine_alert_owner(alert):
    if alert.alert_type == "ANOMALY":
        return None

    if alert.provider:
        return None

    if alert.agent and alert.agent.area:
        return None

    return None


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


def create_combined_liquidity_alert(agent, provider, forecast, anomaly):
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
    if shortage_probability < 0.75:
        return None

    title = f"Liquidity pressure with unusual activity: {provider.name}"
    explanation = (
        "Shared physical cash is falling rapidly while unusual activity "
        "is appearing in repeated, near-identical provider cash-outs. "
        "The activity may reflect legitimate demand, so human review is required."
    )

    alert = Alert.objects.create(
        alert_code=f"ALT-{uuid.uuid4().hex[:8].upper()}",
        agent=agent,
        provider=provider,
        alert_type="LIQUIDITY_PRESSURE",
        severity="HIGH" if shortage_probability < 0.9 else "CRITICAL",
        confidence=max(forecast.confidence, anomaly.score),
        title=title,
        explanation=explanation,
        recommended_action=(
            "Contact the agent, verify the latest cash position, "
            "and review the highlighted transactions before taking action."
        ),
        status="NEW",
    )

    evidence_items = [
        ("Current balance", f"৳{forecast.current_balance:,.2f}"),
        ("Predicted demand", f"৳{forecast.predicted_demand:,.2f}"),
        ("Projected balance", f"৳{forecast.projected_balance:,.2f}"),
        ("Anomaly score", f"{anomaly.score:.0%}"),
        ("Anomaly reason", anomaly.reason),
    ]

    AlertEvidence.objects.bulk_create([
        AlertEvidence(alert=alert, label=label, value=value)
        for label, value in evidence_items
    ])

    return alert


def create_notification(
    *,
    title,
    message,
    level="INFO",
    recipient=None,
    alert=None,
    transaction=None,
):
    notification = Notification.objects.create(
        recipient=recipient,
        alert=alert,
        transaction=transaction,
        level=level,
        title=title,
        message=message,
    )

    recipient_email = getattr(recipient, "email", "") if recipient else ""
    if not recipient_email and alert and alert.owner:
        recipient_email = alert.owner.email or ""

    if recipient_email and level in {"HIGH", "CRITICAL"}:
        send_mail(
            subject=title,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[recipient_email],
            fail_silently=True,
        )

    return notification