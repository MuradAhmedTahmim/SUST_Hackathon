from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from analytics.ai_explainer import answer_question, build_ai_summary

from .models import Alert


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
        },
    )