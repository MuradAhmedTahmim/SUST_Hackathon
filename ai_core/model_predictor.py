from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings


MODEL_PATH = (
    Path(settings.BASE_DIR)
    / "trained_models"
    / "anomaly_model.joblib"
)


def predict_transaction_anomaly(transaction):
    if not MODEL_PATH.exists():
        return {
            "success": False,
            "message": "The anomaly model has not been trained yet.",
        }

    model = joblib.load(MODEL_PATH)

    features = pd.DataFrame(
        [
            {
                "amount": float(transaction.amount),
                "hour": transaction.occurred_at.hour,
                "is_cash_out": (
                    1
                    if transaction.transaction_type == "CASH_OUT"
                    else 0
                ),
            }
        ]
    )

    prediction = model.predict(features)[0]
    anomaly_score = model.decision_function(features)[0]

    is_anomaly = prediction == -1

    return {
        "success": True,
        "is_anomaly": is_anomaly,
        "anomaly_score": float(anomaly_score),
    }