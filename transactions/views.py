from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.dateparse import parse_date

from agents.models import Agent, Provider
from .models import Transaction
from .forms import TransactionForm


@login_required
def transaction_list(request):
    search_query = request.GET.get("q", "").strip()
    agent_id = request.GET.get("agent", "").strip()
    provider_id = request.GET.get("provider", "").strip()
    transaction_type = request.GET.get("type", "").strip()
    status = request.GET.get("status", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    transactions = Transaction.objects.select_related(
        "agent",
        "provider",
    )

    if search_query:
        transactions = transactions.filter(
            Q(transaction_reference__icontains=search_query)
            | Q(agent__agent_code__icontains=search_query)
            | Q(agent__outlet_name__icontains=search_query)
            | Q(synthetic_customer_id__icontains=search_query)
        )

    if agent_id:
        transactions = transactions.filter(agent_id=agent_id)

    if provider_id:
        transactions = transactions.filter(
            provider_id=provider_id
        )

    if transaction_type:
        transactions = transactions.filter(
            transaction_type=transaction_type
        )

    if status:
        transactions = transactions.filter(status=status)

    parsed_date_from = parse_date(date_from)
    parsed_date_to = parse_date(date_to)

    if parsed_date_from:
        transactions = transactions.filter(
            occurred_at__date__gte=parsed_date_from
        )

    if parsed_date_to:
        transactions = transactions.filter(
            occurred_at__date__lte=parsed_date_to
        )

    totals = transactions.aggregate(
        total_amount=Sum("amount"),
    )

    context = {
        "transactions": transactions[:200],
        "agents": Agent.objects.all(),
        "providers": Provider.objects.filter(is_active=True),
        "transaction_types": Transaction.TRANSACTION_TYPES,
        "transaction_statuses": Transaction.STATUS_CHOICES,
        "total_amount": totals["total_amount"] or 0,
        "result_count": transactions.count(),
        "filters": {
            "q": search_query,
            "agent": agent_id,
            "provider": provider_id,
            "type": transaction_type,
            "status": status,
            "date_from": date_from,
            "date_to": date_to,
        },
    }

    return render(
        request,
        "transactions/transaction_list.html",
        context,
    )


@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(
        Transaction.objects.select_related("agent", "provider"),
        pk=pk
    )
    return render(
        request,
        "transactions/transaction_detail.html",
        {"transaction": transaction}
    )


@login_required
def transaction_create(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            tx = form.save()
            messages.success(request, f"Transaction {tx.transaction_reference} created successfully.")
            return redirect("transactions:transaction_detail", pk=tx.pk)
    else:
        form = TransactionForm()
    return render(request, "transactions/transaction_form.html", {"form": form, "action": "Create"})


@login_required
def transaction_edit(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=tx)
        if form.is_valid():
            tx = form.save()
            messages.success(request, f"Transaction {tx.transaction_reference} updated successfully.")
            return redirect("transactions:transaction_detail", pk=tx.pk)
    else:
        form = TransactionForm(instance=tx)
    return render(request, "transactions/transaction_form.html", {"form": form, "transaction": tx, "action": "Edit"})


@login_required
def transaction_delete(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        ref = tx.transaction_reference
        tx.delete()
        messages.success(request, f"Transaction {ref} deleted successfully.")
        return redirect("transactions:transaction_list")
    return render(request, "transactions/transaction_confirm_delete.html", {"transaction": tx})