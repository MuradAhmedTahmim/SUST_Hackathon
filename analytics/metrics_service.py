from datetime import timedelta
from statistics import mean

from django.db.models import Sum
from django.utils import timezone

from alerts.models import Alert, AlertHistory
from analytics.models import LiquidityForecast, ValidationMetric
from transactions.models import Transaction


def _is_likely_anomaly(transaction):
    return transaction.transaction_type == "CASH_OUT" and float(transaction.amount) >= 20000


def calculate_workflow_metrics():
    forecasts = list(LiquidityForecast.objects.all())
    alerts = list(Alert.objects.all())

    lead_times = []
    for forecast in forecasts:
        if forecast.estimated_shortage_at and forecast.generated_at:
            lead_times.append(
                max(
                    (forecast.estimated_shortage_at - forecast.generated_at).total_seconds() / 60,
                    0,
                )
            )

    acknowledged_alerts = []
    for alert in alerts:
        history = alert.history.order_by("created_at")
        ack = history.filter(new_status="ACKNOWLEDGED").first()
        if ack:
            acknowledged_alerts.append(
                max((ack.created_at - alert.created_at).total_seconds() / 60, 0)
            )

    explained_alerts = [
        alert
        for alert in alerts
        if alert.explanation and alert.recommended_action
    ]

    return {
        "lead_time": round(mean(lead_times), 1) if lead_times else 0,
        "anomalies_detected": Transaction.objects.filter(is_injected_anomaly=True).count(),
        "explained_alerts": round((len(explained_alerts) / len(alerts) * 100), 1) if alerts else 0,
        "ack_time": round(mean(acknowledged_alerts), 1) if acknowledged_alerts else 0,
    }


def calculate_validation_metrics():
    forecasts = list(LiquidityForecast.objects.all())
    forecast_errors = []
    for forecast in LiquidityForecast.objects.select_related("agent", "provider"):
        window_end = forecast.generated_at + timedelta(hours=forecast.forecast_hours)
        actual_transactions = Transaction.objects.filter(
            agent=forecast.agent,
            provider=forecast.provider,
            status="SUCCESS",
            occurred_at__gt=forecast.generated_at,
            occurred_at__lte=window_end,
        )
        actual_demand = actual_transactions.filter(transaction_type="CASH_OUT").aggregate(total_amount=Sum("amount"))["total_amount"] or 0
        actual_cash_in = actual_transactions.filter(transaction_type="CASH_IN").aggregate(total_amount=Sum("amount"))["total_amount"] or 0
        actual_net_demand = float(actual_demand - actual_cash_in)
        forecast_errors.append(abs(float(forecast.predicted_demand) - actual_net_demand))

    flagged_transactions = Transaction.objects.filter(is_injected_anomaly=True)
    normal_transactions = Transaction.objects.filter(is_injected_anomaly=False)

    true_positive = sum(1 for tx in flagged_transactions if _is_likely_anomaly(tx))
    false_positive = flagged_transactions.count() - true_positive
    normal_flagged = false_positive

    total_flagged = flagged_transactions.count() or 1
    total_normal = normal_transactions.count() or 1

    return {
        "FORECAST_MAE": (round(mean(forecast_errors), 2), "amount", "Average absolute demand error" ) if forecast_errors else (0, "amount", "Average absolute demand error"),
        "ANOMALY_PRECISION": (round(true_positive / total_flagged * 100, 1), "%", "Correct anomaly flags over all flagged transactions"),
        "FALSE_POSITIVE_RATE": (round(normal_flagged / total_normal * 100, 1), "%", "Normal transactions incorrectly flagged"),
        "EXPLANATION_COVERAGE": (round((Alert.objects.exclude(explanation="").exclude(recommended_action="").count() / max(Alert.objects.count(), 1)) * 100, 1), "%", "Alerts with explanation and recommended action"),
        "SHORTAGE_LEAD_TIME": (round(mean([
            max((f.estimated_shortage_at - f.generated_at).total_seconds() / 3600, 0)
            for f in forecasts
            if f.estimated_shortage_at
        ]), 2) if any(f.estimated_shortage_at for f in forecasts) else 0, "hours", "Average warning time before shortage"),
        "API_LATENCY": (0.0, "ms", "Not measured in this demo environment"),
        "ALERT_OWNERSHIP": (round((Alert.objects.filter(owner__isnull=False).count() / max(Alert.objects.count(), 1)) * 100, 1), "%", "Alerts with a named owner"),
    }


def refresh_validation_metric_rows():
    metrics = calculate_validation_metrics()
    for metric_type, (value, unit, description) in metrics.items():
        ValidationMetric.objects.update_or_create(
            metric_type=metric_type,
            defaults={
                "value": value,
                "unit": unit,
                "description": description,
            },
        )
    return metrics
