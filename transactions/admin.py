from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_reference",
        "agent",
        "provider",
        "transaction_type",
        "amount",
        "status",
        "occurred_at",
    )

    list_filter = (
        "provider",
        "transaction_type",
        "status",
        "is_injected_anomaly",
    )

    search_fields = (
        "transaction_reference",
        "agent__agent_code",
        "agent__outlet_name",
        "synthetic_customer_id",
    )