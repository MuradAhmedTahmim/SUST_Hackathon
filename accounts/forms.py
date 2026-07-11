from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


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
        return user


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


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
