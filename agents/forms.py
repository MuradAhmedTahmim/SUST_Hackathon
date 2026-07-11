from django import forms
from .models import Agent


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = [
            "agent_code",
            "outlet_name",
            "area",
            "physical_cash",
            "safety_cash_threshold",
            "latitude",
            "longitude",
        ]
