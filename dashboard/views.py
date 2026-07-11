from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from agents.models import Agent, AgentProviderBalance, Provider
from alerts.models import Alert
from transactions.models import Transaction


@login_required
def dashboard_home(request):
    profile = getattr(request.user, "profile", None)
    role = profile.role if profile else "AGENT"

    agents_queryset = (
        Agent.objects.select_related("area")
        .prefetch_related(
            Prefetch(
                "provider_balances",
                queryset=AgentProviderBalance.objects.select_related(
                    "provider"
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

    transaction_queryset = Transaction.objects.all()

    provider_queryset = Provider.objects.filter(is_active=True)

    assignment_missing = False

    if role == "AGENT":
        if profile and profile.assigned_agent_id:
            agents_queryset = agents_queryset.filter(
                pk=profile.assigned_agent_id
            )

            active_alerts_queryset = active_alerts_queryset.filter(
                agent_id=profile.assigned_agent_id
            )

            transaction_queryset = transaction_queryset.filter(
                agent_id=profile.assigned_agent_id
            )

            provider_queryset = provider_queryset.filter(
                agent_balances__agent_id=profile.assigned_agent_id
            ).distinct()
        else:
            agents_queryset = agents_queryset.none()
            active_alerts_queryset = active_alerts_queryset.none()
            transaction_queryset = transaction_queryset.none()
            provider_queryset = provider_queryset.none()
            assignment_missing = True

    elif role == "FIELD_OFFICER":
        if profile and profile.assigned_area_id:
            agents_queryset = agents_queryset.filter(
                area_id=profile.assigned_area_id
            )

            active_alerts_queryset = active_alerts_queryset.filter(
                agent__area_id=profile.assigned_area_id
            )

            transaction_queryset = transaction_queryset.filter(
                agent__area_id=profile.assigned_area_id
            )

            provider_queryset = provider_queryset.filter(
                agent_balances__agent__area_id=profile.assigned_area_id
            ).distinct()
        else:
            agents_queryset = agents_queryset.none()
            active_alerts_queryset = active_alerts_queryset.none()
            transaction_queryset = transaction_queryset.none()
            provider_queryset = provider_queryset.none()
            assignment_missing = True

    elif role == "OPERATIONS":
        if profile and profile.assigned_area_id:
            agents_queryset = agents_queryset.filter(
                area_id=profile.assigned_area_id
            )

            active_alerts_queryset = active_alerts_queryset.filter(
                agent__area_id=profile.assigned_area_id
            )

            transaction_queryset = transaction_queryset.filter(
                agent__area_id=profile.assigned_area_id
            )

        if profile and profile.assigned_provider_id:
            active_alerts_queryset = active_alerts_queryset.filter(
                provider_id=profile.assigned_provider_id
            )

            transaction_queryset = transaction_queryset.filter(
                provider_id=profile.assigned_provider_id
            )

            provider_queryset = provider_queryset.filter(
                pk=profile.assigned_provider_id
            )

    elif role == "RISK_REVIEWER":
        active_alerts_queryset = active_alerts_queryset.filter(
            alert_type__in=[
                "ANOMALY",
                "UNUSUAL_ACTIVITY",
                "DATA_QUALITY",
            ]
        )

        if profile and profile.assigned_provider_id:
            active_alerts_queryset = active_alerts_queryset.filter(
                provider_id=profile.assigned_provider_id
            )

            transaction_queryset = transaction_queryset.filter(
                provider_id=profile.assigned_provider_id
            )

            provider_queryset = provider_queryset.filter(
                pk=profile.assigned_provider_id
            )

    last_24_hours = timezone.now() - timedelta(hours=24)

    transaction_summary = (
        transaction_queryset.filter(
            occurred_at__gte=last_24_hours,
            status="SUCCESS",
        )
        .aggregate(
            total_volume=Sum("amount"),
            total_transactions=Count("id"),
            cash_in_volume=Sum(
                "amount",
                filter=Q(transaction_type="CASH_IN"),
            ),
            cash_out_volume=Sum(
                "amount",
                filter=Q(transaction_type="CASH_OUT"),
            ),
        )
    )

    provider_summary = (
        provider_queryset.annotate(
            total_balance=Sum(
                "agent_balances__current_balance",
                filter=Q(
                    agent_balances__agent__in=agents_queryset
                ),
            )
        )
        .order_by("name")
    )

    dashboard_titles = {
        "ADMIN": "Administrator Dashboard",
        "AGENT": "Agent Dashboard",
        "FIELD_OFFICER": "Field Officer Dashboard",
        "OPERATIONS": "Operations Dashboard",
        "RISK_REVIEWER": "Risk Review Dashboard",
    }

    dashboard_descriptions = {
        "ADMIN": "Monitor all agents, providers, alerts and system activity.",
        "AGENT": "Monitor your outlet balances, transactions and alerts.",
        "FIELD_OFFICER": "Monitor agents and alerts within your assigned area.",
        "OPERATIONS": "Monitor operational liquidity and assigned cases.",
        "RISK_REVIEWER": "Review unusual activity and data-quality alerts.",
    }

    context = {
        "agents": agents_queryset[:10],
        "active_alerts": active_alerts_queryset[:8],
        "total_agents": agents_queryset.count(),
        "critical_alerts": active_alerts_queryset.filter(
            severity="CRITICAL"
        ).count(),
        "high_alerts": active_alerts_queryset.filter(
            severity="HIGH"
        ).count(),
        "provider_count": provider_queryset.count(),
        "provider_summary": provider_summary,
        "total_volume": transaction_summary["total_volume"] or 0,
        "total_transactions": (
            transaction_summary["total_transactions"] or 0
        ),
        "cash_in_volume": (
            transaction_summary["cash_in_volume"] or 0
        ),
        "cash_out_volume": (
            transaction_summary["cash_out_volume"] or 0
        ),
        "dashboard_title": dashboard_titles.get(
            role,
            "Dashboard",
        ),
        "dashboard_description": dashboard_descriptions.get(
            role,
            "Monitor operational activity.",
        ),
        "current_role": role,
        "assignment_missing": assignment_missing,
    }

    return render(
        request,
        "dashboard/overview.html",
        context,
    )