from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Agent, AgentProviderBalance, Area, Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    search_fields = (
        "company_name",
        "email",
    )


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = (
        "agent_code",
        "outlet_name",
        "area",
        "physical_cash",
    )
    search_fields = (
        "agent_code",
        "outlet_name",
    )


admin.site.register(Area)
admin.site.register(AgentProviderBalance)