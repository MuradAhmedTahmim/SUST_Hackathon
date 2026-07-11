import random
import uuid
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from agents.models import (
    Agent,
    AgentProviderBalance,
    Area,
    Provider,
)
from transactions.models import Transaction


class Command(BaseCommand):
    help = "Generate synthetic hackathon demonstration data"

    def handle(self, *args, **options):
        area, _ = Area.objects.get_or_create(
            name="Sylhet City",
            district="Sylhet",
        )

        providers = []

        for name, code in [
            ("bKash", "BKASH"),
            ("Nagad", "NAGAD"),
            ("Rocket", "ROCKET"),
        ]:
            provider, _ = Provider.objects.get_or_create(
                name=name,
                code=code,
            )
            providers.append(provider)

        agent, _ = Agent.objects.get_or_create(
            agent_code="AGT-001",
            defaults={
                "outlet_name": "Zindabazar Digital Point",
                "area": area,
                "physical_cash": 42000,
                "safety_cash_threshold": 15000,
            },
        )

        provider_balances = {
            "BKASH": 18000,
            "NAGAD": 55000,
            "ROCKET": 31000,
        }

        for provider in providers:
            AgentProviderBalance.objects.update_or_create(
                agent=agent,
                provider=provider,
                defaults={
                    "current_balance": provider_balances[
                        provider.code
                    ],
                    "safety_threshold": 15000,
                    "data_timestamp": timezone.now(),
                    "data_status": "FRESH",
                },
            )

        Transaction.objects.filter(agent=agent).delete()

        for hour in range(24):
            for _ in range(random.randint(3, 8)):
                provider = random.choice(providers)

                Transaction.objects.create(
                    transaction_reference=(
                        f"TXN-{uuid.uuid4().hex[:12]}"
                    ),
                    agent=agent,
                    provider=provider,
                    transaction_type=random.choice([
                        "CASH_IN",
                        "CASH_OUT",
                    ]),
                    amount=random.randint(500, 15000),
                    status="SUCCESS",
                    occurred_at=(
                        timezone.now()
                        - timedelta(
                            hours=hour,
                            minutes=random.randint(0, 59),
                        )
                    ),
                    synthetic_customer_id=(
                        f"CUS-{random.randint(1000, 9999)}"
                    ),
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data generated successfully."
            )
        )