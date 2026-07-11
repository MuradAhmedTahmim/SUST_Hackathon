from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [
    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),
    path(
        "profile/edit/",
        views.profile_edit_view,
        name="profile_edit",
    ),
    path(
        "settings/",
        views.settings_view,
        name="settings",
    ),
    path(
        "register/",
        views.register_view,
        name="register",
    ),
    path(
        "assign-groups/",
        views.assign_groups_view,
        name="assign_groups",
    ),
    path(
        "forgot-password/",
        views.forgot_password_otp,
        name="forgot_password_otp",
    ),
    path(
        "verify-password-otp/",
        views.verify_password_otp,
        name="verify_password_otp",
    ),
    path(
        "reset-password-otp/",
        views.reset_password_with_otp,
        name="reset_password_with_otp",
    ),
]
