from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from agents.models import Agent, Provider
from ai_core.engine import analyse_agent_provider
from ai_core.model_predictor import predict_transaction_anomaly

from .forms import TransactionForm
from .models import Transaction


def run_transaction_ai(transaction):
    """
    Run anomaly prediction and liquidity analysis for a transaction.

    AI errors are returned instead of stopping the transaction from
    being created or updated.
    """
    results = {
        "anomaly_checked": False,
        "is_anomaly": False,
        "liquidity_checked": False,
        "errors": [],
    }

    # Only successful transactions should influence AI analysis.
    if transaction.status != "SUCCESS":
        return results

    # --------------------------------------------------
    # Local ML anomaly detection
    # --------------------------------------------------
    try:
        anomaly_result = predict_transaction_anomaly(transaction)

        if anomaly_result.get("success"):
            is_anomaly = bool(
                anomaly_result.get("is_anomaly", False)
            )

            transaction.is_injected_anomaly = is_anomaly
            transaction.save(
                update_fields=["is_injected_anomaly"]
            )

            results["anomaly_checked"] = True
            results["is_anomaly"] = is_anomaly

        else:
            results["errors"].append(
                anomaly_result.get(
                    "message",
                    "The anomaly model could not analyse the transaction.",
                )
            )

    except Exception as error:
        results["errors"].append(
            f"Anomaly analysis failed: {error}"
        )

    # --------------------------------------------------
    # Liquidity forecast and alert generation
    # --------------------------------------------------
    try:
        liquidity_result = analyse_agent_provider(
            agent=transaction.agent,
            provider=transaction.provider,
        )

        if liquidity_result.get("success"):
            results["liquidity_checked"] = True
        else:
            results["errors"].append(
                liquidity_result.get(
                    "message",
                    "Liquidity analysis could not be completed.",
                )
            )

    except Exception as error:
        results["errors"].append(
            f"Liquidity analysis failed: {error}"
        )

    return results


@login_required
def transaction_list(request):
    search_query = request.GET.get("q", "").strip()
    agent_id = request.GET.get("agent", "").strip()
    provider_id = request.GET.get("provider", "").strip()
    transaction_type = request.GET.get("type", "").strip()
    status = request.GET.get("status", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    transactions = (
        Transaction.objects.select_related(
            "agent",
            "provider",
        )
        .order_by("-occurred_at")
    )

    if search_query:
        transactions = transactions.filter(
            Q(
                transaction_reference__icontains=search_query
            )
            | Q(
                agent__agent_code__icontains=search_query
            )
            | Q(
                agent__outlet_name__icontains=search_query
            )
            | Q(
                synthetic_customer_id__icontains=search_query
            )
        )

    if agent_id:
        transactions = transactions.filter(
            agent_id=agent_id
        )

    if provider_id:
        transactions = transactions.filter(
            provider_id=provider_id
        )

    if transaction_type:
        transactions = transactions.filter(
            transaction_type=transaction_type
        )

    if status:
        transactions = transactions.filter(
            status=status
        )

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
        total_amount=Sum("amount")
    )

    result_count = transactions.count()

    context = {
        "transactions": transactions[:200],
        "agents": Agent.objects.order_by(
            "agent_code"
        ),
        "providers": Provider.objects.filter(
            is_active=True
        ).order_by("name"),
        "transaction_types": Transaction.TRANSACTION_TYPES,
        "transaction_statuses": Transaction.STATUS_CHOICES,
        "total_amount": totals["total_amount"] or 0,
        "result_count": result_count,
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
        Transaction.objects.select_related(
            "agent",
            "provider",
        ),
        pk=pk,
    )

    return render(
        request,
        "transactions/transaction_detail.html",
        {
            "transaction": transaction,
        },
    )


@login_required
def transaction_create(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save()

            ai_result = run_transaction_ai(
                transaction
            )

            success_message = (
                f"Transaction "
                f"{transaction.transaction_reference} "
                "created successfully."
            )

            if ai_result["is_anomaly"]:
                success_message += (
                    " The AI model flagged it as an anomaly."
                )

            if ai_result["liquidity_checked"]:
                success_message += (
                    " Liquidity forecasting was updated."
                )

            messages.success(
                request,
                success_message,
            )

            for error_message in ai_result["errors"]:
                messages.warning(
                    request,
                    error_message,
                )

            return redirect(
                "transactions:transaction_detail",
                pk=transaction.pk,
            )

    else:
        form = TransactionForm()

    return render(
        request,
        "transactions/transaction_form.html",
        {
            "form": form,
            "action": "Create",
        },
    )


@login_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
    )

    if request.method == "POST":
        form = TransactionForm(
            request.POST,
            instance=transaction,
        )

        if form.is_valid():
            transaction = form.save()

            ai_result = run_transaction_ai(
                transaction
            )

            success_message = (
                f"Transaction "
                f"{transaction.transaction_reference} "
                "updated successfully."
            )

            if ai_result["is_anomaly"]:
                success_message += (
                    " The AI model flagged it as an anomaly."
                )

            if ai_result["liquidity_checked"]:
                success_message += (
                    " Liquidity forecasting was updated."
                )

            messages.success(
                request,
                success_message,
            )

            for error_message in ai_result["errors"]:
                messages.warning(
                    request,
                    error_message,
                )

            return redirect(
                "transactions:transaction_detail",
                pk=transaction.pk,
            )

    else:
        form = TransactionForm(
            instance=transaction
        )

    return render(
        request,
        "transactions/transaction_form.html",
        {
            "form": form,
            "transaction": transaction,
            "action": "Edit",
        },
    )


@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
    )

    if request.method == "POST":
        reference = transaction.transaction_reference
        transaction.delete()

        messages.success(
            request,
            f"Transaction {reference} deleted successfully.",
        )

        return redirect(
            "transactions:transaction_list"
        )

    return render(
        request,
        "transactions/transaction_confirm_delete.html",
        {
            "transaction": transaction,
        },
    )