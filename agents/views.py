from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .forms import AgentForm

from alerts.models import Alert
from transactions.models import Transaction

from .models import Agent, AgentProviderBalance, Area, Provider
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from ai_core.engine import analyse_agent_provider
from ai_core.engine import analyse_agent_provider
from .models import Agent, Provider

@login_required
def agent_list(request):
    search_query = request.GET.get("q", "").strip()
    area_id = request.GET.get("area", "").strip()
    provider_id = request.GET.get("provider", "").strip()
    cash_status = request.GET.get("cash_status", "").strip()

    agents = Agent.objects.select_related(
        "area"
    ).prefetch_related(
        Prefetch(
            "provider_balances",
            queryset=AgentProviderBalance.objects.select_related(
                "provider"
            ),
        )
    )

    if search_query:
        agents = agents.filter(
            Q(agent_code__icontains=search_query)
            | Q(outlet_name__icontains=search_query)
            | Q(owner_name__icontains=search_query)
            | Q(phone__icontains=search_query)
        )

    if area_id:
        agents = agents.filter(area_id=area_id)

    if provider_id:
        agents = agents.filter(
            provider_balances__provider_id=provider_id
        ).distinct()

    agents = list(agents)

    if cash_status:
        agents = [
            agent
            for agent in agents
            if agent.cash_status == cash_status
        ]

    context = {
        "agents": agents,
        "areas": Area.objects.all(),
        "providers": Provider.objects.filter(is_active=True),
        "search_query": search_query,
        "selected_area": area_id,
        "selected_provider": provider_id,
        "selected_cash_status": cash_status,
    }

    return render(
        request,
        "agents/agent_list.html",
        context,
    )


@login_required
def agent_detail(request, agent_id):
    agent = get_object_or_404(
        Agent.objects.select_related(
            "area"
        ).prefetch_related(
            Prefetch(
                "provider_balances",
                queryset=AgentProviderBalance.objects.select_related(
                    "provider"
                ),
            )
        ),
        pk=agent_id,
    )

    recent_transactions = (
        Transaction.objects.filter(agent=agent)
        .select_related("provider")
        .order_by("-occurred_at")[:20]
    )

    active_alerts = (
        Alert.objects.filter(agent=agent)
        .exclude(status__in=["RESOLVED", "CLOSED"])
        .select_related("provider", "owner")
        .order_by("-created_at")[:10]
    )

    context = {
        "agent": agent,
        "recent_transactions": recent_transactions,
        "active_alerts": active_alerts,
    }

    return render(
        request,
        "agents/agent_detail.html",
        context,
    )


@login_required
def agent_create(request):
    if request.method == "POST":
        form = AgentForm(request.POST)
        if form.is_valid():
            agent = form.save()
            messages.success(request, f"Agent {agent.outlet_name} created successfully.")
            return redirect("agents:agent_detail", agent_id=agent.id)
    else:
        form = AgentForm()
    return render(request, "agents/agent_form.html", {"form": form, "action": "Create"})


@login_required
def agent_edit(request, agent_id):
    agent = get_object_or_404(Agent, pk=agent_id)
    if request.method == "POST":
        form = AgentForm(request.POST, instance=agent)
        if form.is_valid():
            agent = form.save()
            messages.success(request, f"Agent {agent.outlet_name} updated successfully.")
            return redirect("agents:agent_detail", agent_id=agent.id)
    else:
        form = AgentForm(instance=agent)
    return render(request, "agents/agent_form.html", {"form": form, "agent": agent, "action": "Edit"})


@login_required
def agent_delete(request, agent_id):
    agent = get_object_or_404(Agent, pk=agent_id)
    if request.method == "POST":
        outlet_name = agent.outlet_name
        agent.delete()
        messages.success(request, f"Agent {outlet_name} deleted successfully.")
        return redirect("agents:agent_list")
    return render(request, "agents/agent_confirm_delete.html", {"agent": agent})


@login_required
def run_ai_analysis(request, agent_id, provider_id):
    if request.method != "POST":
        messages.error(
            request,
            "Invalid request method.",
        )
        return redirect(
            "agents:detail",
            pk=agent_id,
        )

    agent = get_object_or_404(
        Agent,
        pk=agent_id,
    )

    provider = get_object_or_404(
        Provider,
        pk=provider_id,
    )

    result = analyse_agent_provider(
        agent=agent,
        provider=provider,
    )

    if result["success"]:
        messages.success(
            request,
            "AI analysis completed successfully.",
        )
    else:
        messages.error(
            request,
            result["message"],
        )

    return redirect(
        "agents:detail",
        pk=agent.pk,
    )