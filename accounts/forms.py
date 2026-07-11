from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission, User
from .models import UserProfile


ROLE_GROUP_MAP = {
    "ADMIN": "Administrator",
    "AGENT": "Agent",
    "FIELD_OFFICER": "Field Officer",
    "OPERATIONS": "Operations",
    "RISK_REVIEWER": "Risk Reviewer",
}


def assign_role_group(user, role_key):
    role_name = ROLE_GROUP_MAP.get(role_key)
    if not role_name:
        return

    user.groups.clear()
    group, _ = Group.objects.get_or_create(name=role_name)
    user.groups.add(group)


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True, initial="AGENT")
    preferred_language = forms.ChoiceField(choices=UserProfile.LANGUAGE_CHOICES, required=True, initial="EN")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get("phone", "")
            profile.role = self.cleaned_data.get("role", "AGENT")
            profile.preferred_language = self.cleaned_data.get("preferred_language", "EN")
            profile.save()
            assign_role_group(user, profile.role)
        return user


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class UserManagementForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Groups",
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.order_by("content_type__app_label", "codename"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Direct permissions",
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "groups",
            "user_permissions",
        ]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "phone",
            "assigned_provider",
            "assigned_area",
            "preferred_language",
            "receive_critical_alerts",
        ]
