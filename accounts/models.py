import random
from django.utils import timezone
from django.conf import settings
from django.db import models



class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("ADMIN", "Administrator"),
        ("AGENT", "Agent"),
        ("FIELD_OFFICER", "Field Officer"),
        ("OPERATIONS", "Operations"),
        ("RISK_REVIEWER", "Risk Reviewer"),
    ]

    LANGUAGE_CHOICES = [
        ("EN", "English"),
        ("BN", "Bengali"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default="AGENT",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    assigned_provider = models.ForeignKey(
        "agents.Provider",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_user_profiles",
    )

    assigned_area = models.ForeignKey(
        "agents.Area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_user_profiles",
    )

    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default="EN",
    )

    receive_critical_alerts = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class OTPRecord(models.Model):
    PURPOSE_CHOICES = [
        ("REGISTRATION", "Registration"),
        ("PASSWORD_RESET", "Password Reset"),
    ]

    email = models.EmailField()
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="PASSWORD_RESET")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP({self.purpose}) for {self.email}"

    @staticmethod
    def generate(email, purpose="PASSWORD_RESET", expiry_minutes=10):
        """Delete old records for this email+purpose and create a fresh OTP."""
        OTPRecord.objects.filter(email=email, purpose=purpose, is_used=False).delete()
        code = f"{random.randint(100000, 999999)}"
        expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
        return OTPRecord.objects.create(
            email=email, code=code, purpose=purpose, expires_at=expires_at
        )

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at