from django.shortcuts import render

# Create your views here.
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from agents.models import Agent, AgentProviderBalance, Provider
from alerts.services import create_liquidity_alert
from transactions.models import Transaction

from .forecasting import forecast_liquidity
from .models import LiquidityForecast, ValidationMetric


DATA_CONFIDENCE = {
    "FRESH": 90,
    "DELAYED": 60,
    "MISSING": 20,
    "CONFLICTING": 35,
    "RECOVERED": 75,
}


@login_required
def forecast_dashboard(request):
    forecasts = LiquidityForecast.objects.select_related(
        "agent",
        "provider",
    )[:100]

    return render(
        request,
        "analytics/forecast_dashboard.html",
        {
            "forecasts": forecasts,
            "agents": Agent.objects.all(),
        },
    )


@login_required
def run_agent_forecast(request, agent_id):
    if request.method != "POST":
        return redirect(
            "agents:agent_detail",
            agent_id=agent_id,
        )

    agent = get_object_or_404(
        Agent,
        pk=agent_id,
    )

    forecast_hours_raw = request.POST.get(
        "forecast_hours",
        "2",
    )

    try:
        forecast_hours = int(forecast_hours_raw)
    except ValueError:
        forecast_hours = 2

    forecast_hours = min(
        max(forecast_hours, 1),
        24,
    )

    period_start = timezone.now() - timedelta(hours=2)

    balances = (
        AgentProviderBalance.objects.filter(agent=agent)
        .select_related("provider")
    )

    created_count = 0

    for balance in balances:
        successful_transactions = Transaction.objects.filter(
            agent=agent,
            provider=balance.provider,
            status="SUCCESS",
            occurred_at__gte=period_start,
        )

        cash_out_total = (
            successful_transactions.filter(
                transaction_type="CASH_OUT"
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        cash_in_total = (
            successful_transactions.filter(
                transaction_type="CASH_IN"
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        net_depletion_two_hours = max(
            cash_out_total - cash_in_total,
            Decimal("0.00"),
        )

        hourly_depletion = (
            net_depletion_two_hours / Decimal("2")
        )

        predicted_demand = (
            hourly_depletion
            * Decimal(str(forecast_hours))
        )

        projected_balance = (
            balance.current_balance
            - predicted_demand
        )

        forecast_result = forecast_liquidity(
            current_balance=float(balance.current_balance),
            average_depletion_per_hour=float(hourly_depletion),
            forecast_hours=forecast_hours,
            safety_threshold=float(balance.safety_threshold),
            data_status=balance.data_status,
        )

        shortage_probability = forecast_result.shortage_probability
        confidence = forecast_result.confidence
        estimated_shortage_at = forecast_result.estimated_shortage_at

        explanation = (
            f"{balance.provider.name} currently has "
            f"৳{balance.current_balance:,.2f}. "
            f"Estimated demand for the next "
            f"{forecast_hours} hour(s) is "
            f"৳{predicted_demand:,.2f}. "
            f"Projected balance is "
            f"৳{projected_balance:,.2f}. "
            f"Data status is "
            f"{balance.get_data_status_display()}."
        )

        forecast = LiquidityForecast.objects.create(
            agent=agent,
            provider=balance.provider,
            forecast_type="PROVIDER_BALANCE",
            forecast_hours=forecast_hours,
            current_balance=balance.current_balance,
            predicted_demand=predicted_demand,
            projected_balance=projected_balance,
            safety_threshold=balance.safety_threshold,
            shortage_probability=shortage_probability,
            confidence=confidence,
            estimated_shortage_at=estimated_shortage_at,
            explanation=explanation,
        )

        created_count += 1

        if shortage_probability >= 0.5:
            create_liquidity_alert(
                agent=agent,
                provider=balance.provider,
                forecast=forecast,
            )

    messages.success(
        request,
        f"{created_count} provider forecast(s) generated.",
    )

    return redirect(
        "agents:agent_detail",
        agent_id=agent.id,
    )


@login_required
def anomaly_review(request):
    anomalous_transactions = (
        Transaction.objects.filter(
            Q(is_injected_anomaly=True)
        )
        .select_related("agent", "provider")
        .order_by("-occurred_at")[:100]
    )

    return render(
        request,
        "analytics/anomaly_review.html",
        {
            "transactions": anomalous_transactions,
        },
    )


@login_required
def metrics_dashboard(request):
    latest_metrics = {}

    for metric_type, _ in ValidationMetric.METRIC_TYPES:
        latest_metric = (
            ValidationMetric.objects.filter(
                metric_type=metric_type
            )
            .order_by("-calculated_at")
            .first()
        )

        if latest_metric:
            latest_metrics[metric_type] = latest_metric

    alert_statistics = Alert.objects.aggregate(
        total=Count("id"),
        critical=Count(
            "id",
            filter=Q(severity="CRITICAL"),
        ),
        resolved=Count(
            "id",
            filter=Q(status="RESOLVED"),
        ),
        average_confidence=Avg("confidence"),
    )

    return render(
        request,
        "analytics/metrics.html",
        {
            "latest_metrics": latest_metrics,
            "alert_statistics": alert_statistics,
        },
    )


@login_required
def data_quality_dashboard(request):
    balances = AgentProviderBalance.objects.select_related(
        "agent",
        "provider",
    ).order_by(
        "data_status",
        "-data_timestamp",
    )

    status_counts = balances.values(
        "data_status"
    ).annotate(
        total=Count("id")
    )

    return render(
        request,
        "analytics/data_quality.html",
        {
            "balances": balances,
            "status_counts": status_counts,
        },
    )