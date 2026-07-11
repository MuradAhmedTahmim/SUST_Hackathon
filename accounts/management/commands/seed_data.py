"""
Management command to populate the database with realistic demo data.
Usage: python manage.py seed_data
"""
import random
import uuid
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from agents.models import Agent, AgentProviderBalance, Area, Provider
from alerts.models import Alert, AlertEvidence, AlertHistory
from transactions.models import Transaction


class Command(BaseCommand):
    help = "Seed the database with realistic demo data for all modules."

    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding database …\n")

        providers = self._create_providers()
        areas = self._create_areas()
        agents = self._create_agents(areas)
        self._create_provider_balances(agents, providers)
        transactions = self._create_transactions(agents, providers)
        self._create_alerts(agents, providers, transactions)

        self.stdout.write(self.style.SUCCESS("\n✅  Seed complete!"))

    # ------------------------------------------------------------------
    # Providers
    # ------------------------------------------------------------------
    def _create_providers(self):
        data = [
            ("bKash", "BKASH"),
            ("Nagad", "NAGAD"),
            ("Rocket", "ROCKET"),
            ("Upay", "UPAY"),
            ("SureCash", "SURECASH"),
        ]
        objs = []
        for name, code in data:
            obj, created = Provider.objects.get_or_create(
                code=code, defaults={"name": name, "is_active": True}
            )
            objs.append(obj)
            tag = "created" if created else "exists"
            self.stdout.write(f"  Provider {name} … {tag}")
        return objs

    # ------------------------------------------------------------------
    # Areas
    # ------------------------------------------------------------------
    def _create_areas(self):
        data = [
            ("Gulshan", "Dhaka"),
            ("Banani", "Dhaka"),
            ("Uttara", "Dhaka"),
            ("Mirpur", "Dhaka"),
            ("Dhanmondi", "Dhaka"),
            ("Motijheel", "Dhaka"),
            ("Agrabad", "Chittagong"),
            ("Nasirabad", "Chittagong"),
            ("Halishahar", "Chittagong"),
            ("Kazir Dewri", "Chittagong"),
            ("Shahjalal Upashahar", "Sylhet"),
            ("Zindabazar", "Sylhet"),
            ("Sonadanga", "Khulna"),
            ("Daulatpur", "Khulna"),
            ("Godnail", "Narayanganj"),
        ]
        objs = []
        for name, district in data:
            obj, created = Area.objects.get_or_create(
                name=name, defaults={"district": district}
            )
            objs.append(obj)
        self.stdout.write(f"  Areas … {len(objs)} ready")
        return objs

    # ------------------------------------------------------------------
    # Agents
    # ------------------------------------------------------------------
    def _create_agents(self, areas):
        outlets = [
            "Dhaka Central Mobile",
            "Gulshan Plaza Counter",
            "Banani Supermarket",
            "Uttara Sector-7 Shop",
            "Mirpur DOHS Booth",
            "Dhanmondi Mart",
            "Motijheel Express",
            "Agrabad Trade Hub",
            "Nasirabad Corner",
            "Halishahar Mini Mart",
            "Kazir Dewri Point",
            "Sylhet City Kiosk",
            "Zindabazar Cash Point",
            "Sonadanga Bazaar",
            "Daulatpur Digital Hub",
            "Godnail Service Center",
            "Uttara Rajuk Counter",
            "Mirpur-10 Cash Hub",
            "Banani Road-11 Booth",
            "Motijheel VIP Counter",
        ]
        objs = []
        for i, name in enumerate(outlets):
            code = f"AG-{1001 + i}"
            area = areas[i % len(areas)]
            cash = Decimal(random.randint(2000, 120000))
            threshold = Decimal(random.choice([10000, 15000, 20000, 25000]))
            lat = Decimal(f"{random.uniform(22.3, 24.9):.7f}")
            lng = Decimal(f"{random.uniform(88.5, 91.8):.7f}")
            obj, created = Agent.objects.get_or_create(
                agent_code=code,
                defaults={
                    "outlet_name": name,
                    "area": area,
                    "physical_cash": cash,
                    "safety_cash_threshold": threshold,
                    "latitude": lat,
                    "longitude": lng,
                },
            )
            objs.append(obj)
        self.stdout.write(f"  Agents … {len(objs)} ready")
        return objs

    # ------------------------------------------------------------------
    # Provider Balances
    # ------------------------------------------------------------------
    def _create_provider_balances(self, agents, providers):
        now = timezone.now()
        count = 0
        for agent in agents:
            # Each agent gets 2-4 random provider balances
            selected = random.sample(providers, k=random.randint(2, min(4, len(providers))))
            for provider in selected:
                balance = Decimal(random.randint(5000, 80000))
                threshold = Decimal(random.choice([8000, 10000, 15000]))
                hours_ago = random.randint(0, 48)
                status = random.choices(
                    ["FRESH", "DELAYED", "MISSING", "CONFLICTING"],
                    weights=[60, 20, 10, 10],
                    k=1,
                )[0]
                _, created = AgentProviderBalance.objects.get_or_create(
                    agent=agent,
                    provider=provider,
                    defaults={
                        "current_balance": balance,
                        "safety_threshold": threshold,
                        "data_timestamp": now - timedelta(hours=hours_ago),
                        "data_status": status,
                    },
                )
                if created:
                    count += 1
        self.stdout.write(f"  Provider balances … {count} created")

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------
    def _create_transactions(self, agents, providers):
        now = timezone.now()
        objs = []
        customer_pool = [f"CUST-{random.randint(10000, 99999)}" for _ in range(50)]

        for i in range(200):
            agent = random.choice(agents)
            provider = random.choice(providers)
            tx_type = random.choice(["CASH_IN", "CASH_OUT"])
            status = random.choices(
                ["SUCCESS", "FAILED", "PENDING"], weights=[80, 12, 8], k=1
            )[0]
            amount = Decimal(random.choice([100, 200, 500, 1000, 2000, 5000, 10000, 15000, 25000]))
            hours_ago = random.randint(0, 720)  # up to 30 days ago
            is_anomaly = random.random() < 0.08  # ~8 % anomalies
            ref = f"TXN-{uuid.uuid4().hex[:10].upper()}"
            customer = random.choice(customer_pool)

            obj, created = Transaction.objects.get_or_create(
                transaction_reference=ref,
                defaults={
                    "agent": agent,
                    "provider": provider,
                    "transaction_type": tx_type,
                    "amount": amount,
                    "status": status,
                    "occurred_at": now - timedelta(hours=hours_ago),
                    "synthetic_customer_id": customer,
                    "is_injected_anomaly": is_anomaly,
                },
            )
            objs.append(obj)
        self.stdout.write(f"  Transactions … {len(objs)} ready")
        return objs

    # ------------------------------------------------------------------
    # Alerts + Evidence + History
    # ------------------------------------------------------------------
    def _create_alerts(self, agents, providers, transactions):
        now = timezone.now()
        alert_templates = [
            {
                "type": "LIQUIDITY_PRESSURE",
                "severity": "CRITICAL",
                "title": "Cash dangerously low at {agent}",
                "explanation": "Physical cash balance has dropped below 50% of the safety threshold. The agent may be unable to serve cash-out requests.",
                "action": "Dispatch emergency cash replenishment. Contact the area supervisor immediately.",
            },
            {
                "type": "LIQUIDITY_PRESSURE",
                "severity": "HIGH",
                "title": "Cash below safety threshold at {agent}",
                "explanation": "The agent's physical cash is below the configured safety threshold, indicating potential service disruption.",
                "action": "Schedule a cash replenishment within the next 4 hours.",
            },
            {
                "type": "VELOCITY_ANOMALY",
                "severity": "HIGH",
                "title": "Unusual transaction velocity detected at {agent}",
                "explanation": "Transaction frequency is 3.2x above the 7-day rolling average for this time window. This may indicate structuring or smurfing activity.",
                "action": "Review recent transaction log. If pattern persists, escalate to compliance.",
            },
            {
                "type": "VELOCITY_ANOMALY",
                "severity": "MEDIUM",
                "title": "Moderate velocity spike at {agent}",
                "explanation": "Transaction rate is 1.8x the expected baseline. Pattern is within monitoring thresholds but warrants observation.",
                "action": "Monitor for the next 2 hours. No immediate action required.",
            },
            {
                "type": "REPEATED_AMOUNT",
                "severity": "HIGH",
                "title": "Repeated identical amounts at {agent}",
                "explanation": "Multiple transactions of exactly ৳{amount} within a 30-minute window from different customer IDs. Potential structuring activity.",
                "action": "Flag for compliance review. Cross-reference customer IDs for links.",
            },
            {
                "type": "REPEATED_AMOUNT",
                "severity": "MEDIUM",
                "title": "Duplicate amount pattern at {agent}",
                "explanation": "Three transactions of ৳{amount} from the same customer within 2 hours. May be legitimate but flagged for review.",
                "action": "Verify with the agent whether this is normal business activity.",
            },
            {
                "type": "DATA_QUALITY",
                "severity": "LOW",
                "title": "Stale balance data for {provider} at {agent}",
                "explanation": "Balance data for {provider} has not been refreshed for over 24 hours. The displayed balance may be inaccurate.",
                "action": "Check API connectivity to {provider}. Trigger a manual data refresh.",
            },
            {
                "type": "DATA_QUALITY",
                "severity": "MEDIUM",
                "title": "Conflicting balance reported for {provider} at {agent}",
                "explanation": "The provider API and reconciliation file report different balances. Discrepancy: ৳{amount}.",
                "action": "Run a full reconciliation for this agent-provider pair.",
            },
            {
                "type": "LIQUIDITY_PRESSURE",
                "severity": "MEDIUM",
                "title": "Provider float running low for {provider} at {agent}",
                "explanation": "The {provider} float balance is approaching the safety threshold. Cash-in operations may be affected soon.",
                "action": "Initiate a float top-up request to {provider}.",
            },
            {
                "type": "VELOCITY_ANOMALY",
                "severity": "CRITICAL",
                "title": "Extreme transaction burst at {agent}",
                "explanation": "Over 40 transactions processed in the last 15 minutes — 8x above the expected rate. Strong indicator of potential fraud or system error.",
                "action": "Immediately suspend agent transactions and initiate investigation.",
            },
        ]

        statuses_pool = ["NEW", "ASSIGNED", "ACKNOWLEDGED", "INVESTIGATING", "ESCALATED", "RESOLVED", "CLOSED", "FALSE_POSITIVE"]
        count = 0

        for i, tmpl in enumerate(alert_templates * 3):  # 30 alerts total
            agent = random.choice(agents)
            provider = random.choice(providers)
            amount = random.choice([5000, 10000, 15000, 25000])
            status = random.choices(
                statuses_pool,
                weights=[25, 15, 10, 10, 5, 15, 10, 10],
                k=1,
            )[0]
            confidence = round(random.uniform(0.55, 0.99), 2)
            hours_ago = random.randint(0, 336)  # up to 14 days

            title = tmpl["title"].format(agent=agent.outlet_name, provider=provider.name, amount=amount)
            explanation = tmpl["explanation"].format(agent=agent.outlet_name, provider=provider.name, amount=amount)
            action = tmpl["action"].format(agent=agent.outlet_name, provider=provider.name, amount=amount)

            code = f"ALT-{uuid.uuid4().hex[:8].upper()}"
            resolved_at = None
            if status in ("RESOLVED", "CLOSED", "FALSE_POSITIVE"):
                resolved_at = now - timedelta(hours=max(0, hours_ago - random.randint(1, 24)))

            alert, created = Alert.objects.get_or_create(
                alert_code=code,
                defaults={
                    "agent": agent,
                    "provider": provider,
                    "alert_type": tmpl["type"],
                    "severity": tmpl["severity"],
                    "confidence": confidence,
                    "title": title,
                    "explanation": explanation,
                    "recommended_action": action,
                    "status": status,
                    "resolved_at": resolved_at,
                },
            )

            if created:
                count += 1
                # Add 1-3 pieces of evidence
                evidence_options = [
                    ("Transaction count (1h)", str(random.randint(5, 60))),
                    ("Average amount", f"৳{random.randint(1000, 20000):,}"),
                    ("Peak hour", f"{random.randint(8, 22)}:00"),
                    ("Cash balance at trigger", f"৳{random.randint(1000, 50000):,}"),
                    ("Provider balance", f"৳{random.randint(2000, 40000):,}"),
                    ("Affected customer IDs", str(random.randint(1, 12))),
                    ("Data freshness", f"{random.randint(1, 72)} hours stale"),
                    ("Velocity ratio", f"{round(random.uniform(1.2, 8.5), 1)}x baseline"),
                ]
                for label, value in random.sample(evidence_options, k=random.randint(2, 4)):
                    AlertEvidence.objects.create(alert=alert, label=label, value=value)

                # Add 1-2 history entries
                AlertHistory.objects.create(
                    alert=alert,
                    old_status="",
                    new_status="NEW",
                    note="Alert auto-generated by the detection engine.",
                )
                if status != "NEW":
                    AlertHistory.objects.create(
                        alert=alert,
                        old_status="NEW",
                        new_status=status,
                        note=f"Status updated to {status}.",
                    )

        self.stdout.write(f"  Alerts … {count} created (with evidence & history)")
