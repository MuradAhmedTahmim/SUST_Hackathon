from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings
from sklearn.ensemble import IsolationForest

from transactions.models import Transaction


def train_model():
    transactions = Transaction.objects.filter(
        status="SUCCESS"
    ).values(
        "amount",
        "transaction_type",
        "occurred_at",
    )

    data = list(transactions)

    if len(data) < 20:
        return {
            "success": False,
            "message": (
                "Not enough successful transactions. "
                "Run python manage.py seed_data first."
            ),
        }

    dataframe = pd.DataFrame(data)

    dataframe["amount"] = dataframe["amount"].astype(float)
    dataframe["hour"] = dataframe["occurred_at"].dt.hour
    dataframe["is_cash_out"] = (
        dataframe["transaction_type"] == "CASH_OUT"
    ).astype(int)

    features = dataframe[
        [
            "amount",
            "hour",
            "is_cash_out",
        ]
    ]

    model = IsolationForest(
        contamination=0.08,
        random_state=42,
    )

    model.fit(features)

    model_directory = Path(settings.BASE_DIR) / "trained_models"
    model_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = model_directory / "anomaly_model.joblib"

    joblib.dump(
        model,
        model_path,
    )

    return {
        "success": True,
        "message": (
            f"Model trained using {len(data)} transactions "
            f"and saved to {model_path}."
        ),
    }