from .models import Alert


def unread_alert_count(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"unread_alert_count": 0}

    count = Alert.objects.filter(
        status__in=["NEW", "ASSIGNED", "ACKNOWLEDGED", "INVESTIGATING", "ESCALATED"]
    ).count()

    return {"unread_alert_count": count}
