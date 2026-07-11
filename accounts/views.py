from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render

from .forms import (
    UserForm,
    UserManagementForm,
    UserProfileForm,
    UserRegisterForm,
)
from .models import OTPRecord, UserProfile

User = get_user_model()


# ---------------------------------------------------------------------------
# Profile views
# ---------------------------------------------------------------------------

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"profile": profile})


@login_required
def settings_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        language = request.POST.get("preferred_language", "EN")
        receive_alerts = request.POST.get("receive_critical_alerts") == "on"

        valid_languages = {choice[0] for choice in UserProfile.LANGUAGE_CHOICES}
        if language not in valid_languages:
            messages.error(request, "Invalid language selection.")
            return redirect("accounts:settings")

        profile.preferred_language = language
        profile.receive_critical_alerts = receive_alerts
        profile.save(update_fields=["preferred_language", "receive_critical_alerts", "updated_at"])

        messages.success(request, "Settings updated successfully.")
        return redirect("accounts:settings")

    return render(request, "accounts/settings.html", {"profile": profile})


@login_required
def profile_edit_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("accounts:profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    return render(
        request,
        "accounts/profile_edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def assign_groups_view(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to assign groups.")
        return redirect("dashboard:home")

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(request, "The selected user does not exist.")
            return redirect("accounts:assign_groups")

        form = UserManagementForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Permissions updated for {target_user.username}.")
            return redirect("accounts:assign_groups")
    else:
        form = UserManagementForm()

    users = User.objects.order_by("username")
    return render(
        request,
        "accounts/assign_groups.html",
        {"form": form, "users": users},
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome to AgentPulse, {user.username}! Your account has been registered.",
            )
            return redirect("dashboard:home")
    else:
        form = UserRegisterForm()

    return render(request, "registration/register.html", {"form": form})


# ---------------------------------------------------------------------------
# OTP-based Forgot Password
# ---------------------------------------------------------------------------

def _send_otp_email(email, otp_code):
    """Send the 6-digit OTP to the given email address."""
    subject = "Your AgentPulse Password Reset OTP"
    message = (
        f"Hello,\n\n"
        f"You requested a password reset for your AgentPulse AI account.\n\n"
        f"Your One-Time Password (OTP) is:\n\n"
        f"    {otp_code}\n\n"
        f"This code expires in 10 minutes. Do not share it with anyone.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"— The AgentPulse AI Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def forgot_password_otp(request):
    """Step 1 – User enters their registered email address."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        # Always say "check your email" so we don't leak whether the account exists.
        if User.objects.filter(email__iexact=email).exists():
            otp = OTPRecord.generate(email=email, purpose="PASSWORD_RESET", expiry_minutes=10)
            try:
                _send_otp_email(email, otp.code)
            except Exception:
                messages.error(request, "Failed to send OTP email. Please try again later.")
                return redirect("accounts:forgot_password_otp")

        messages.success(
            request,
            "If that email is registered, we've sent a 6-digit OTP. Check your inbox.",
        )
        # Store email in session so verify step knows who to look up
        request.session["otp_email"] = email
        return redirect("accounts:verify_password_otp")

    return render(request, "registration/forgot_password_otp.html")


def verify_password_otp(request):
    """Step 2 – User enters the 6-digit OTP they received."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    email = request.session.get("otp_email", "")
    if not email:
        messages.error(request, "Session expired. Please start again.")
        return redirect("accounts:forgot_password_otp")

    if request.method == "POST":
        entered = request.POST.get("otp", "").strip()

        otp_record = (
            OTPRecord.objects
            .filter(email__iexact=email, purpose="PASSWORD_RESET", is_used=False)
            .order_by("-created_at")
            .first()
        )

        if otp_record and otp_record.is_valid() and otp_record.code == entered:
            otp_record.is_used = True
            otp_record.save(update_fields=["is_used"])
            # Mark in session that OTP was verified, allow password reset
            request.session["otp_verified"] = True
            return redirect("accounts:reset_password_with_otp")
        else:
            messages.error(request, "Invalid or expired OTP. Please try again.")

    return render(request, "registration/verify_password_otp.html", {"email": email})


def reset_password_with_otp(request):
    """Step 3 – User sets a new password after successful OTP verification."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    email = request.session.get("otp_email", "")
    verified = request.session.get("otp_verified", False)

    if not email or not verified:
        messages.error(request, "Unauthorised. Please complete the OTP verification first.")
        return redirect("accounts:forgot_password_otp")

    if request.method == "POST":
        password1 = request.POST.get("new_password1", "")
        password2 = request.POST.get("new_password2", "")

        if not password1 or len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
        elif password1 != password2:
            messages.error(request, "Passwords do not match.")
        else:
            try:
                user = User.objects.get(email__iexact=email)
                user.set_password(password1)
                user.save()
                # Clear session flags
                request.session.pop("otp_email", None)
                request.session.pop("otp_verified", None)
                messages.success(
                    request,
                    "Your password has been reset successfully. Please sign in.",
                )
                return redirect("login")
            except User.DoesNotExist:
                messages.error(request, "User not found. Please start again.")
                return redirect("accounts:forgot_password_otp")

    return render(request, "registration/reset_password_with_otp.html")
