from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from analytics.ai_explainer import answer_question, build_ai_summary

from .models import Alert, AlertHistory

User = get_user_model()


@login_required
def alert_list(request):
    alerts = Alert.objects.select_related(
        "agent",
        "provider",
        "owner",
    ).order_by("-created_at")

    return render(
        request,
        "alerts/alert_list.html",
        {
            "alerts": alerts,
        },
    )


@login_required
def alert_detail(request, pk):
    alert = get_object_or_404(
        Alert.objects.select_related(
            "agent",
            "provider",
            "owner",
        ),
        pk=pk,
    )

    question = request.GET.get("question", "").strip()
    language = request.GET.get("lang", "en")
    ai_summary = build_ai_summary(alert, language=language)
    ai_answer = None

    if question:
        ai_answer = answer_question(alert, question)

    return render(
        request,
        "alerts/alert_detail.html",
        {
            "alert": alert,
            "ai_summary": ai_summary,
            "ai_answer": ai_answer,
            "question": question,
            "status_choices": Alert.STATUS_CHOICES,
            "staff_users": User.objects.filter(is_active=True).order_by("username"),
        },
    )


@login_required
def update_alert_status(request, pk):
    if request.method != "POST":
        return redirect("alerts:alert_detail", pk=pk)

    alert = get_object_or_404(Alert, pk=pk)
    new_status = request.POST.get("status", "").strip().upper()
    note = request.POST.get("note", "").strip()
    owner_id = request.POST.get("owner_id", "").strip()
    assigned_to_id = request.POST.get("assigned_to_id", "").strip()

    if new_status not in dict(Alert.STATUS_CHOICES):
        messages.error(request, "Please select a valid alert status.")
        return redirect("alerts:alert_detail", pk=pk)

    old_status = alert.status
    alert.status = new_status

    if owner_id:
        alert.owner = User.objects.filter(pk=owner_id).first()

    if assigned_to_id:
        alert.assigned_to = User.objects.filter(pk=assigned_to_id).first()

    if new_status in {"RESOLVED", "CLOSED", "FALSE_POSITIVE"}:
        alert.resolved_at = timezone.now()
    elif old_status in {"RESOLVED", "CLOSED", "FALSE_POSITIVE"} and new_status != old_status:
        alert.resolved_at = None

    alert.save()

    AlertHistory.objects.create(
        alert=alert,
        actor=request.user,
        old_status=old_status,
        new_status=new_status,
        note=note or "Status and assignment updated through the review workflow.",
    )

    messages.success(request, f"Alert status updated to {alert.get_status_display()}.")
    return redirect("alerts:alert_detail", pk=pk)