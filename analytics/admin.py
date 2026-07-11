from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import LiquidityForecast, ValidationMetric


@admin.register(LiquidityForecast)
class LiquidityForecastAdmin(admin.ModelAdmin):
    list_display = (
        "agent",
        "provider",
        "forecast_type",
        "forecast_hours",
        "current_balance",
        "projected_balance",
        "shortage_probability",
        "confidence",
        "generated_at",
    )

    list_filter = (
        "forecast_type",
        "provider",
        "generated_at",
    )

    search_fields = (
        "agent__agent_code",
        "agent__outlet_name",
        "provider__name",
        "explanation",
    )

    autocomplete_fields = (
        "agent",
        "provider",
    )

    readonly_fields = (
        "generated_at",
    )

    date_hierarchy = "generated_at"


@admin.register(ValidationMetric)
class ValidationMetricAdmin(admin.ModelAdmin):
    list_display = (
        "metric_type",
        "value",
        "unit",
        "calculated_at",
    )

    list_filter = (
        "metric_type",
        "calculated_at",
    )

    search_fields = (
        "description",
    )

    readonly_fields = (
        "calculated_at",
    )