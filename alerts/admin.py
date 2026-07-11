from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Alert, AlertEvidence, AlertHistory, Notification


class AlertEvidenceInline(admin.TabularInline):
    model = AlertEvidence
    extra = 0


class AlertHistoryInline(admin.TabularInline):
    model = AlertHistory
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        "alert_code",
        "title",
        "agent",
        "provider",
        "severity",
        "status",
        "owner",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "alert_type",
        "severity",
        "status",
        "provider",
    )

    search_fields = (
        "alert_code",
        "title",
        "agent__agent_code",
        "agent__outlet_name",
        "owner__username",
        "assigned_to__username",
    )

    inlines = [
        AlertEvidenceInline,
        AlertHistoryInline,
    ]


admin.site.register(AlertEvidence)
admin.site.register(AlertHistory)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "recipient",
        "alert",
        "transaction",
        "level",
        "is_read",
        "created_at",
    )

    list_filter = (
        "level",
        "is_read",
        "created_at",
    )

    search_fields = (
        "title",
        "message",
        "recipient__username",
        "transaction__transaction_reference",
        "alert__alert_code",
    )