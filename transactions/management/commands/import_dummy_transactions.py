from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from agents.models import Agent, Provider
from transactions.models import Transaction


dummy_transactions = [
    {
        "agent": "Agent-001",
        "amount": 12500,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-06-12 09:15:00",
    },
    {
        "agent": "Agent-002",
        "amount": 7800,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-06-13 11:30:00",
    },
    {
        "agent": "Agent-003",
        "amount": 15200,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-06-14 14:20:00",
    },
    {
        "agent": "Agent-001",
        "amount": 4300,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-06-15 16:45:00",
    },
    {
        "agent": "Agent-004",
        "amount": 22000,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-06-16 10:10:00",
    },
    {
        "agent": "Agent-002",
        "amount": 9600,
        "transaction_type": "cash_out",
        "status": "pending",
        "date": "2026-06-17 12:40:00",
    },
    {
        "agent": "Agent-005",
        "amount": 18500,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-06-18 15:05:00",
    },
    {
        "agent": "Agent-003",
        "amount": 6300,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-06-19 17:25:00",
    },
    {
        "agent": "Agent-001",
        "amount": 11800,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-06-20 08:50:00",
    },
    {
        "agent": "Agent-004",
        "amount": 14000,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-06-21 13:15:00",
    },
    {
        "agent": "Agent-005",
        "amount": 27500,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-06-22 09:35:00",
    },
    {
        "agent": "Agent-002",
        "amount": 5200,
        "transaction_type": "cash_out",
        "status": "failed",
        "date": "2026-06-23 11:55:00",
    },
    {
        "agent": "Agent-003",
        "amount": 16800,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-06-24 14:10:00",
    },
    {
        "agent": "Agent-001",
        "amount": 8900,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-06-25 16:30:00",
    },
    {
        "agent": "Agent-004",
        "amount": 31000,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-06-26 10:25:00",
    },
    {
        "agent": "Agent-005",
        "amount": 12500,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-06-27 12:15:00",
    },
    {
        "agent": "Agent-002",
        "amount": 19800,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-06-28 15:40:00",
    },
    {
        "agent": "Agent-003",
        "amount": 7400,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-06-29 18:05:00",
    },
    {
        "agent": "Agent-001",
        "amount": 23500,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-06-30 09:45:00",
    },
    {
        "agent": "Agent-004",
        "amount": 10200,
        "transaction_type": "cash_out",
        "status": "pending",
        "date": "2026-07-01 13:20:00",
    },
    {
        "agent": "Agent-005",
        "amount": 33000,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-07-02 10:05:00",
    },
    {
        "agent": "Agent-002",
        "amount": 15500,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-07-03 12:50:00",
    },
    {
        "agent": "Agent-003",
        "amount": 21400,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-07-04 14:35:00",
    },
    {
        "agent": "Agent-001",
        "amount": 6800,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-07-05 17:10:00",
    },
    {
        "agent": "Agent-004",
        "amount": 29500,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-07-06 08:40:00",
    },
    {
        "agent": "Agent-005",
        "amount": 17200,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-07-07 11:25:00",
    },
    {
        "agent": "Agent-002",
        "amount": 24600,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-07-08 15:15:00",
    },
    {
        "agent": "Agent-003",
        "amount": 9500,
        "transaction_type": "cash_out",
        "status": "failed",
        "date": "2026-07-09 16:55:00",
    },
    {
        "agent": "Agent-001",
        "amount": 36000,
        "transaction_type": "cash_in",
        "status": "completed",
        "date": "2026-07-10 10:30:00",
    },
    {
        "agent": "Agent-004",
        "amount": 19800,
        "transaction_type": "cash_out",
        "status": "completed",
        "date": "2026-07-11 14:20:00",
    },
]


transaction_type_map = {
    "cash_in": "CASH_IN",
    "cash_out": "CASH_OUT",
}

status_map = {
    "completed": "SUCCESS",
    "pending": "PENDING",
    "failed": "FAILED",
}


class Command(BaseCommand):
    help = "Import the provided dummy transaction dataset into the database."

    def handle(self, *args, **options):
        provider = Provider.objects.filter(code="BKASH").first()

        if not provider:
            provider = Provider.objects.create(
                name="bKash",
                code="BKASH",
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS("Created provider BKASH."))

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for index, item in enumerate(dummy_transactions, start=1):
            agent = Agent.objects.filter(agent_code=item["agent"]).first()

            if not agent:
                agent = Agent.objects.create(
                    agent_code=item["agent"],
                    outlet_name=item["agent"],
                    physical_cash=Decimal("0"),
                    safety_cash_threshold=Decimal("10000"),
                )
                self.stdout.write(
                    self.style.WARNING(
                        f"Created placeholder agent {item['agent']}"
                    )
                )

            occurred_at = parse_datetime(item["date"].replace(" ", "T"))
            if occurred_at is None:
                self.stdout.write(
                    self.style.ERROR(
                        f"Skipped item {index}: invalid date {item['date']}"
                    )
                )
                skipped_count += 1
                continue

            if timezone.is_naive(occurred_at):
                occurred_at = timezone.make_aware(
                    occurred_at,
                    timezone.get_current_timezone(),
                )

            transaction_reference = f"DUMMY-TXN-{index:03d}"
            transaction, created = Transaction.objects.update_or_create(
                transaction_reference=transaction_reference,
                defaults={
                    "agent": agent,
                    "provider": provider,
                    "amount": Decimal(str(item["amount"])),
                    "transaction_type": transaction_type_map[item["transaction_type"]],
                    "status": status_map[item["status"]],
                    "occurred_at": occurred_at,
                    "synthetic_customer_id": f"DUMMY-CUSTOMER-{(index % 10) + 1:03d}",
                    "is_injected_anomaly": False,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    f"Created: {transaction_reference} for {agent.agent_code}"
                )
            else:
                updated_count += 1
                self.stdout.write(
                    f"Updated: {transaction_reference} for {agent.agent_code}"
                )

        self.stdout.write("\nFinished importing transactions.")
        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Updated: {updated_count}")
        self.stdout.write(f"Skipped: {skipped_count}")
