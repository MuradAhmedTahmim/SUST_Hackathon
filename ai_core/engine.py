from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Sum
from django.utils import timezone

from alerts.models import Alert
from analytics.models import LiquidityForecast
from transactions.models import Transaction


def analyse_agent_provider(agent, provider):
    balance_record = agent.provider_balances.filter(
        provider=provider
    ).first()

    if not balance_record:
        return {
            "success": False,
            "message": "This agent has no balance for the selected provider.",
        }

    now = timezone.now()
    two_hours_ago = now - timedelta(hours=2)

    transactions = Transaction.objects.filter(
        agent=agent,
        provider=provider,
        status="SUCCESS",
        occurred_at__gte=two_hours_ago,
    )

    cash_in = transactions.filter(
        transaction_type="CASH_IN"
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    cash_out = transactions.filter(
        transaction_type="CASH_OUT"
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    predicted_demand = max(
        cash_out - cash_in,
        Decimal("0"),
    )

    projected_balance = (
        balance_record.current_balance - predicted_demand
    )

    safety_threshold = balance_record.safety_threshold

    shortage_amount = max(
        safety_threshold - projected_balance,
        Decimal("0"),
    )

    shortage_probability = calculate_shortage_probability(
        projected_balance,
        safety_threshold,
    )

    confidence = calculate_confidence(
        transactions.count()
    )

    explanation = (
        f"Current balance is {balance_record.current_balance}. "
        f"Cash-in during the last 2 hours was {cash_in}. "
        f"Cash-out during the last 2 hours was {cash_out}. "
        f"Projected balance is {projected_balance}. "
        f"Safety threshold is {safety_threshold}."
    )

    if shortage_amount > 0:
        recommended_amount = shortage_amount * Decimal("1.20")

        recommendation = (
            f"Transfer approximately {recommended_amount:.2f} "
            f"to the {provider.name} balance."
        )
    else:
        recommendation = (
            f"No immediate {provider.name} transfer is required."
        )

    forecast = LiquidityForecast.objects.create(
        agent=agent,
        provider=provider,
        forecast_type="PROVIDER_BALANCE",
        forecast_hours=2,
        current_balance=balance_record.current_balance,
        predicted_demand=predicted_demand,
        projected_balance=projected_balance,
        safety_threshold=safety_threshold,
        shortage_probability=shortage_probability,
        confidence=confidence,
        estimated_shortage_at=(
            now + timedelta(hours=2)
            if projected_balance < safety_threshold
            else None
        ),
        explanation=explanation,
    )

    anomalies = detect_anomalies(
        agent,
        provider,
    )

    alert = None

    if shortage_probability >= 50:
        alert = create_alert(
            agent=agent,
            provider=provider,
            forecast=forecast,
            explanation=explanation,
            recommendation=recommendation,
        )

    return {
        "success": True,
        "forecast": forecast,
        "alert": alert,
        "anomalies": anomalies,
        "recommendation": recommendation,
    }


def calculate_shortage_probability(
    projected_balance,
    safety_threshold,
):
    if safety_threshold <= 0:
        return 0.0

    if projected_balance <= 0:
        return 98.0

    if projected_balance < safety_threshold:
        shortage_ratio = (
            safety_threshold - projected_balance
        ) / safety_threshold

        probability = (
            Decimal("65")
            + shortage_ratio * Decimal("30")
        )

        return float(
            min(probability, Decimal("95"))
        )

    return 15.0


def calculate_confidence(transaction_count):
    if transaction_count >= 20:
        return 95.0

    if transaction_count >= 10:
        return 88.0

    if transaction_count >= 5:
        return 78.0

    if transaction_count >= 1:
        return 65.0

    return 40.0


def detect_anomalies(agent, provider):
    transactions = Transaction.objects.filter(
        agent=agent,
        provider=provider,
        status="SUCCESS",
    ).order_by("-occurred_at")[:100]

    average_amount = transactions.aggregate(
        average=Avg("amount")
    )["average"] or Decimal("0")

    flagged_transactions = []

    for transaction in transactions[:20]:
        if (
            average_amount > 0
            and transaction.amount >= average_amount * Decimal("3")
        ):
            transaction.is_injected_anomaly = True
            transaction.save(
                update_fields=["is_injected_anomaly"]
            )

            flagged_transactions.append(transaction)

    return flagged_transactions


def create_alert(
    agent,
    provider,
    forecast,
    explanation,
    recommendation,
):
    if forecast.shortage_probability >= 85:
        severity = "CRITICAL"
    elif forecast.shortage_probability >= 70:
        severity = "HIGH"
    else:
        severity = "MEDIUM"

    alert_code = (
        f"AI-{agent.agent_code}-"
        f"{timezone.now().strftime('%Y%m%d%H%M%S')}"
    )

    return Alert.objects.create(
        alert_code=alert_code,
        agent=agent,
        provider=provider,
        alert_type="LIQUIDITY_PRESSURE",
        severity=severity,
        confidence=forecast.confidence,
        title=f"{provider.name} liquidity risk detected",
        explanation=explanation,
        recommended_action=recommendation,
        status="NEW",
    )