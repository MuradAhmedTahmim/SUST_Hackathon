from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from agents.models import Agent, Area, Provider
from alerts.context_processors import unread_alert_count
from alerts.models import Alert, AlertHistory
from analytics.ai_explainer import answer_question, build_ai_summary
from analytics.forecasting import forecast_liquidity
from analytics.models import LiquidityForecast
from alerts.services import create_liquidity_alert


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

        alert = create_liquidity_alert(
            agent=self.agent,
            provider=self.provider,
            forecast=forecast,
        )

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

    def test_forecast_returns_probability_in_zero_to_one_range(self):
        forecast = forecast_liquidity(
            current_balance=18000,
            average_depletion_per_hour=800,
            forecast_hours=2,
            safety_threshold=10000,
            data_status="FRESH",
        )

        self.assertGreaterEqual(forecast.shortage_probability, 0)
        self.assertLessEqual(forecast.shortage_probability, 1)
        self.assertGreater(forecast.confidence, 0)

    def test_ai_summary_contains_explainable_risk_summary(self):
        alert = Alert.objects.create(
            alert_code="ALT-002",
            agent=self.agent,
            provider=self.provider,
            alert_type="LIQUIDITY_PRESSURE",
            severity="HIGH",
            confidence=0.84,
            title="Possible Nagad liquidity shortage",
            explanation="Projected balance may fall below safety threshold",
            recommended_action="Review immediately",
            status="NEW",
        )

        summary = build_ai_summary(alert, language="en")

        self.assertIn("liquidity", summary["english"].lower())
        self.assertIn("review", summary["recommended_action"].lower())
        self.assertEqual(summary["confidence"], 84)

    def test_ai_question_answer_avoids_false_claims(self):
        alert = Alert.objects.create(
            alert_code="ALT-003",
            agent=self.agent,
            provider=self.provider,
            alert_type="LIQUIDITY_PRESSURE",
            severity="HIGH",
            confidence=0.84,
            title="Possible Nagad liquidity shortage",
            explanation="Projected balance may fall below safety threshold",
            recommended_action="Review immediately",
            status="NEW",
        )

        answer = answer_question(alert, "Is this confirmed fraud?")

        self.assertIn("not proof of fraud", answer.lower())

    def test_duplicate_alerts_are_not_created_for_active_warning(self):
        forecast = LiquidityForecast.objects.create(
            agent=self.agent,
            provider=self.provider,
            forecast_type="PROVIDER_BALANCE",
            forecast_hours=2,
            current_balance=Decimal("18000"),
            predicted_demand=Decimal("8000"),
            projected_balance=Decimal("10000"),
            safety_threshold=Decimal("10000"),
            shortage_probability=0.84,
            confidence=0.88,
            explanation="Projected balance may fall below safety threshold",
            estimated_shortage_at=timezone.now(),
        )

        create_liquidity_alert(
            agent=self.agent,
            provider=self.provider,
            forecast=forecast,
        )
        duplicate = create_liquidity_alert(
            agent=self.agent,
            provider=self.provider,
            forecast=forecast,
        )

        self.assertEqual(Alert.objects.count(), 1)
        self.assertEqual(duplicate.id, Alert.objects.get().id)

    def test_alert_status_updates_create_history_entry(self):
        alert = Alert.objects.create(
            alert_code="ALT-004",
            agent=self.agent,
            provider=self.provider,
            alert_type="LIQUIDITY_PRESSURE",
            severity="HIGH",
            confidence=0.84,
            title="Possible Nagad liquidity shortage",
            explanation="Projected balance may fall below safety threshold",
            recommended_action="Review immediately",
            status="NEW",
        )

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("alerts:update_alert_status", args=[alert.pk]),
            {
                "status": "ACKNOWLEDGED",
                "note": "Review started by the analyst.",
            },
        )

        alert.refresh_from_db()
        history = AlertHistory.objects.filter(alert=alert).first()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(alert.status, "ACKNOWLEDGED")
        self.assertIsNotNone(history)
        self.assertEqual(history.new_status, "ACKNOWLEDGED")
        self.assertIn("analyst", history.note.lower())
