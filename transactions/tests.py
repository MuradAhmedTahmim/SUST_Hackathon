from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from agents.models import Agent, Area, AgentProviderBalance, Provider
from alerts.models import Alert, Notification
from analytics.models import LiquidityForecast
from transactions.models import Transaction
from transactions.views import run_transaction_ai


class TransactionWorkflowTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username="workflow-user",
			password="secret123",
		)
		self.area = Area.objects.create(name="Gulshan", district="Dhaka")
		self.agent = Agent.objects.create(
			agent_code="AGT-500",
			outlet_name="Workflow Outlet",
			area=self.area,
			physical_cash=Decimal("25000.00"),
			safety_cash_threshold=Decimal("10000.00"),
		)
		self.provider = Provider.objects.create(
			name="bKash",
			code="BKASH-WORKFLOW",
			is_active=True,
		)
		AgentProviderBalance.objects.create(
			agent=self.agent,
			provider=self.provider,
			current_balance=Decimal("20000.00"),
			safety_threshold=Decimal("10000.00"),
			data_timestamp=timezone.now(),
			data_status="FRESH",
		)

	def test_successful_transaction_creates_notification(self):
		transaction = Transaction.objects.create(
			transaction_reference="TXN-WORKFLOW-001",
			agent=self.agent,
			provider=self.provider,
			transaction_type="CASH_OUT",
			amount=Decimal("1500.00"),
			status="SUCCESS",
			occurred_at=timezone.now(),
			synthetic_customer_id="CUS-WORKFLOW-001",
			is_injected_anomaly=False,
		)

		result = run_transaction_ai(transaction, recipient=self.user)

		self.assertTrue(result["liquidity_checked"])
		self.assertTrue(result["notification_created"])
		self.assertEqual(Notification.objects.count(), 1)
		notification = Notification.objects.first()
		self.assertEqual(notification.transaction, transaction)
		self.assertEqual(notification.recipient, self.user)
		self.assertIn("transaction", notification.message.lower())

	def test_large_cash_out_triggers_ai_workflow(self):
		transaction = Transaction.objects.create(
			transaction_reference="TXN-HIGH-RISK-001",
			agent=self.agent,
			provider=self.provider,
			transaction_type="CASH_OUT",
			amount=Decimal("19200.00"),
			status="SUCCESS",
			occurred_at=timezone.now(),
			synthetic_customer_id="CUS-HIGH-RISK-001",
			is_injected_anomaly=False,
		)

		result = run_transaction_ai(transaction, recipient=self.user)

		transaction.refresh_from_db()

		self.assertTrue(result["anomaly_checked"])
		self.assertTrue(result["is_anomaly"])
		self.assertTrue(result["liquidity_checked"])
		self.assertTrue(result["notification_created"])
		self.assertTrue(transaction.is_injected_anomaly)
		self.assertEqual(LiquidityForecast.objects.count(), 1)
		self.assertEqual(Alert.objects.count(), 1)
		self.assertEqual(Notification.objects.count(), 1)
		self.assertIn(transaction, Transaction.objects.all())
