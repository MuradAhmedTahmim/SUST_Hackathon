from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "transaction_reference",
            "agent",
            "provider",
            "transaction_type",
            "amount",
            "status",
            "occurred_at",
            "synthetic_customer_id",
            "is_injected_anomaly",
        ]
        widgets = {
            "occurred_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.occurred_at:
            self.initial["occurred_at"] = self.instance.occurred_at.strftime("%Y-%m-%dT%H:%M")
