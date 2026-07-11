from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "phone",
        "assigned_agent",
        "assigned_provider",
        "assigned_area",
        "preferred_language",
        "receive_critical_alerts",
    )

    list_filter = (
    "role",
    "preferred_language",
    "receive_critical_alerts",
    "assigned_agent",
    "assigned_provider",
    "assigned_area",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone",
    )