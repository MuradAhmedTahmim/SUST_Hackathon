from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from agents.models import Agent, Provider


class Alert(models.Model):
    ALERT_TYPES = [
        ("LIQUIDITY_PRESSURE", "Liquidity Pressure"),
        ("VELOCITY_ANOMALY", "Velocity Anomaly"),
        ("REPEATED_AMOUNT", "Repeated Amount"),
        ("DATA_QUALITY", "Data Quality"),
    ]

    SEVERITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    STATUS_CHOICES = [
        ("NEW", "New"),
        ("ASSIGNED", "Assigned"),
        ("ACKNOWLEDGED", "Acknowledged"),
        ("INVESTIGATING", "Investigating"),
        ("ESCALATED", "Escalated"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
        ("FALSE_POSITIVE", "False Positive"),
    ]

    alert_code = models.CharField(max_length=40, unique=True)
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    provider = models.ForeignKey(
        Provider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    alert_type = models.CharField(
        max_length=40,
        choices=ALERT_TYPES,
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
    )
    confidence = models.FloatField(default=0)
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    recommended_action = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_alerts",
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="NEW",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.alert_code


class AlertEvidence(models.Model):
    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name="evidence",
    )
    label = models.CharField(max_length=150)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class AlertHistory(models.Model):
    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name="history",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    old_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    LEVEL_CHOICES = [
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    alert = models.ForeignKey(
        Alert,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default="INFO",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title