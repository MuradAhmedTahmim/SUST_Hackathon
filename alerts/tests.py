from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from agents.models import Agent, Area, Provider
from alerts.context_processors import unread_alert_count
from alerts.models import Alert
from analytics.models import LiquidityForecast
from analytics.views import create_liquidity_alert


class AlertNotificationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="notifier",
            password="secret123",
        )
        self.area = Area.objects.create(name="Gulshan")
        self.agent = Agent.objects.create(
            agent_code="AGT-100",
            outlet_name="Outlet 100",
            area=self.area,
        )
        self.provider = Provider.objects.create(
            name="Nagad",
            code="NAGAD",
        )
        self.factory = RequestFactory()

    def test_high_risk_forecast_creates_new_alert(self):
        forecast = LiquidityForecast.objects.create(
            agent=self.agent,
            provider=self.provider,
            forecast_type="PROVIDER_BALANCE",
            forecast_hours=2,
            current_balance=Decimal("8000"),
            predicted_demand=Decimal("5000"),
            projected_balance=Decimal("3000"),
            safety_threshold=Decimal("5000"),
            shortage_probability=75,
            confidence=0.85,
            explanation="Projected balance may fall below safety threshold",
            estimated_shortage_at=timezone.now(),
        )

        alert = create_liquidity_alert(forecast=forecast)

        self.assertIsNotNone(alert)
        self.assertEqual(alert.status, "NEW")
        self.assertEqual(alert.severity, "HIGH")
        self.assertIn("liquidity", alert.title.lower())

    def test_context_processor_returns_number_of_new_alerts(self):
        Alert.objects.create(
            alert_code="ALT-001",
            agent=self.agent,
            provider=self.provider,
            alert_type="LIQUIDITY_PRESSURE",
            severity="HIGH",
            confidence=0.9,
            title="Possible Nagad liquidity shortage",
            explanation="Projected balance may fall below safety threshold",
            recommended_action="Review immediately",
            status="NEW",
        )

        request = self.factory.get("/")
        request.user = self.user

        self.assertEqual(
            unread_alert_count(request),
            {"unread_alert_count": 1},
        )
