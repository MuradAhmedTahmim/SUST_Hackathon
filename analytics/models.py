from django.db import models

# Create your models here.
from django.db import models


class LiquidityForecast(models.Model):
    FORECAST_TYPE_CHOICES = [
        ("PROVIDER_BALANCE", "Provider Balance"),
        ("PHYSICAL_CASH", "Physical Cash"),
    ]

    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.CASCADE,
        related_name="forecasts",
    )

    provider = models.ForeignKey(
        "agents.Provider",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forecasts",
    )

    forecast_type = models.CharField(
        max_length=30,
        choices=FORECAST_TYPE_CHOICES,
        default="PROVIDER_BALANCE",
    )

    forecast_hours = models.PositiveIntegerField(
        default=2,
    )

    current_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    predicted_demand = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    projected_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    safety_threshold = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    shortage_probability = models.FloatField(
        default=0,
        help_text="Store probability as a value between 0 and 100.",
    )

    confidence = models.FloatField(
        default=0,
        help_text="Store confidence as a value between 0 and 100.",
    )

    estimated_shortage_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    explanation = models.TextField(
        blank=True,
    )

    generated_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        provider_name = (
            self.provider.name
            if self.provider
            else "Physical cash"
        )

        return (
            f"{self.agent.agent_code} - "
            f"{provider_name} forecast"
        )


class ValidationMetric(models.Model):
    METRIC_TYPES = [
        ("FORECAST_MAE", "Forecast MAE"),
        ("SHORTAGE_LEAD_TIME", "Shortage Lead Time"),
        ("ANOMALY_PRECISION", "Anomaly Precision"),
        ("ANOMALY_RECALL", "Anomaly Recall"),
        ("FALSE_POSITIVE_RATE", "False Positive Rate"),
        ("EXPLANATION_COVERAGE", "Explanation Coverage"),
        ("API_LATENCY", "API Latency"),
        ("ALERT_OWNERSHIP", "Alert Ownership"),
    ]

    metric_type = models.CharField(
        max_length=40,
        choices=METRIC_TYPES,
    )

    value = models.FloatField()

    unit = models.CharField(
        max_length=30,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    calculated_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-calculated_at"]

    def __str__(self):
        return (
            f"{self.get_metric_type_display()}: "
            f"{self.value} {self.unit}"
        )