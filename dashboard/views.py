from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from agents.models import (
    Agent,
    AgentProviderBalance,
    Provider,
)
from alerts.models import Alert
from transactions.models import Transaction


@login_required
def dashboard_home(request):
    agents_queryset = (
        Agent.objects.select_related("area")
        .prefetch_related(
            Prefetch(
                "provider_balances",
                queryset=(
                    AgentProviderBalance.objects
                    .select_related("provider")
                ),
            )
        )
    )

    active_alerts_queryset = (
        Alert.objects.exclude(
            status__in=[
                "RESOLVED",
                "CLOSED",
                "FALSE_POSITIVE",
            ]
        )
        .select_related(
            "agent",
            "provider",
            "owner",
        )
        .order_by("-created_at")
    )

    last_24_hours = (
        timezone.now()
        - timedelta(hours=24)
    )

    transaction_summary = (
        Transaction.objects.filter(
            occurred_at__gte=last_24_hours,
            status="SUCCESS",
        )
        .aggregate(
            total_volume=Sum("amount"),
            total_transactions=Count("id"),
            cash_in_volume=Sum(
                "amount",
                filter=Q(
                    transaction_type="CASH_IN"
                ),
            ),
            cash_out_volume=Sum(
                "amount",
                filter=Q(
                    transaction_type="CASH_OUT"
                ),
            ),
        )
    )

    provider_summary = (
        Provider.objects.filter(
            is_active=True
        )
        .annotate(
            total_balance=Sum(
                "agentproviderbalance__current_balance"
            )
        )
        .order_by("name")
    )

    context = {
        "agents": agents_queryset[:10],
        "active_alerts": active_alerts_queryset[:8],
        "total_agents": agents_queryset.count(),
        "critical_alerts": (
            active_alerts_queryset.filter(
                severity="CRITICAL"
            ).count()
        ),
        "high_alerts": (
            active_alerts_queryset.filter(
                severity="HIGH"
            ).count()
        ),
        "provider_count": Provider.objects.filter(
            is_active=True
        ).count(),
        "provider_summary": provider_summary,
        "total_volume": (
            transaction_summary["total_volume"]
            or 0
        ),
        "total_transactions": (
            transaction_summary["total_transactions"]
            or 0
        ),
        "cash_in_volume": (
            transaction_summary["cash_in_volume"]
            or 0
        ),
        "cash_out_volume": (
            transaction_summary["cash_out_volume"]
            or 0
        ),
    }

    return render(
        request,
        "dashboard/overview.html",
        context,
    )