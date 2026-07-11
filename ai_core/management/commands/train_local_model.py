import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from analytics.models import LiquidityForecast
from transactions.models import Transaction

MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models"
MODEL_PATH = MODEL_DIR / "local_forecast_model.json"


def sigmoid(x):
    from math import exp
    return 1.0 / (1.0 + exp(-x))


class Command(BaseCommand):
    help = "Generate a simple local forecast model using summary transaction metrics."

    def handle(self, *args, **options):
        self.stdout.write("Training local forecast model…")
        transactions = Transaction.objects.filter(status="SUCCESS")

        if not transactions.exists():
            self.stdout.write(self.style.ERROR("No successful transactions found."))
            return

        grouped = {}
        for tx in transactions.order_by("occurred_at"):
            grouped.setdefault((tx.agent_id, tx.provider_id), []).append(tx)

        samples = []
        for (agent_id, provider_id), txs in grouped.items():
            if len(txs) < 4:
                continue

            cash_in = sum(t.amount for t in txs if t.transaction_type == "CASH_IN")
            cash_out = sum(t.amount for t in txs if t.transaction_type == "CASH_OUT")
            transactions_count = len(txs)
            avg_amount = float(sum(t.amount for t in txs) / transactions_count)
            provider_balance = txs[-1].agent.provider_balances.filter(provider_id=provider_id).first()
            if not provider_balance:
                continue

            current_balance = float(provider_balance.current_balance)
            safety_threshold = float(provider_balance.safety_threshold)
            projected_balance = current_balance - float(max(cash_out - cash_in, 0) / 2)
            shortage_probability = max(min((safety_threshold - projected_balance) / safety_threshold, 1.0), 0.0)
            label = 1 if shortage_probability >= 0.5 else 0

            samples.append({
                "features": [
                    current_balance,
                    float(cash_in),
                    float(cash_out),
                    transactions_count,
                    avg_amount,
                    safety_threshold,
                ],
                "label": label,
            })

        if not samples:
            self.stdout.write(self.style.ERROR("No valid training samples were created."))
            return

        totals = [0.0] * len(samples[0]["features"])
        counts = [0] * len(samples[0]["features"])
        for sample in samples:
            for i, value in enumerate(sample["features"]):
                totals[i] += value
                counts[i] += 1
        means = [totals[i] / counts[i] for i in range(len(totals))]

        variances = [0.0] * len(samples[0]["features"])
        for sample in samples:
            for i, value in enumerate(sample["features"]):
                variances[i] += (value - means[i]) ** 2
        scales = [ (variances[i] / max(counts[i] - 1, 1)) ** 0.5 for i in range(len(variances)) ]
        scales = [scale if scale > 0 else 1.0 for scale in scales]

        # Simple logistic regression using gradient descent
        weights = [0.0] * len(means)
        bias = 0.0
        learning_rate = 0.1
        for epoch in range(200):
            grad_w = [0.0] * len(weights)
            grad_b = 0.0
            for sample in samples:
                x = [
                    (value - means[i]) / scales[i]
                    for i, value in enumerate(sample["features"])
                ]
                z = bias + sum(w * xi for w, xi in zip(weights, x))
                pred = sigmoid(z)
                error = pred - sample["label"]
                for i in range(len(weights)):
                    grad_w[i] += error * x[i]
                grad_b += error
            for i in range(len(weights)):
                weights[i] -= learning_rate * grad_w[i] / len(samples)
            bias -= learning_rate * grad_b / len(samples)

        model_data = {
            "scaler_mean": means,
            "scaler_scale": scales,
            "coef": weights,
            "intercept": bias,
        }

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, "w", encoding="utf-8") as f:
            json.dump(model_data, f)

        self.stdout.write(self.style.SUCCESS(f"Local model trained and saved: {MODEL_PATH}"))
        self.stdout.write(self.style.SUCCESS(f"Training samples: {len(samples)}"))
