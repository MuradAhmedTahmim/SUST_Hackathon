from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

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

    return render(
        request,
        "alerts/alert_detail.html",
        {
            "alert": alert,
        },
    )