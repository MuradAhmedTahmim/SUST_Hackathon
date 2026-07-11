from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Alert, AlertEvidence, AlertHistory


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
    )

    inlines = [
        AlertEvidenceInline,
        AlertHistoryInline,
    ]


admin.site.register(AlertEvidence)
admin.site.register(AlertHistory)