from django.db import models

from agents.models import Agent, Provider


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("CASH_IN", "Cash In"),
        ("CASH_OUT", "Cash Out"),
    ]

    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("PENDING", "Pending"),
    ]

    transaction_reference = models.CharField(
        max_length=80,
        unique=True,
    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SUCCESS",
    )

    occurred_at = models.DateTimeField()

    synthetic_customer_id = models.CharField(
        max_length=80,
        blank=True,
    )

    is_injected_anomaly = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.transaction_reference