from decimal import Decimal

from django.db import models


class Provider(models.Model):
    name = models.CharField(
        max_length=80,
        unique=True,
    )

    code = models.CharField(
        max_length=20,
        unique=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(
        max_length=100,
    )

    district = models.CharField(
        max_length=100,
        blank=True,
    )

    def __str__(self):
        return self.name


class Agent(models.Model):
    agent_code = models.CharField(
        max_length=40,
        unique=True,
    )

    outlet_name = models.CharField(
        max_length=150,
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    physical_cash = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    safety_cash_threshold = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=10000,
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.agent_code} - {self.outlet_name}"

    @property
    def cash_status(self):
        if (
            self.physical_cash
            < self.safety_cash_threshold * Decimal("0.5")
        ):
            return "CRITICAL"

        if self.physical_cash < self.safety_cash_threshold:
            return "LOW"

        return "SAFE"


class AgentProviderBalance(models.Model):
    DATA_STATUS_CHOICES = [
        ("FRESH", "Fresh"),
        ("DELAYED", "Delayed"),
        ("MISSING", "Missing"),
        ("CONFLICTING", "Conflicting"),
    ]

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="provider_balances",
    )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="agent_balances",
    )

    current_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    safety_threshold = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=10000,
    )

    data_timestamp = models.DateTimeField()

    data_status = models.CharField(
        max_length=20,
        choices=DATA_STATUS_CHOICES,
        default="FRESH",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["agent", "provider"],
                name="unique_agent_provider_balance",
            )
        ]

    def __str__(self):
        return f"{self.agent} - {self.provider}"