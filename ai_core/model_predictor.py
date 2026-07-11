from pathlib import Path

from django.conf import settings

try:
    import joblib  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional training dependency
    joblib = None

try:
    import pandas as pd  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional training dependency
    pd = None


MODEL_PATH = (
    Path(settings.BASE_DIR)
    / "trained_models"
    / "anomaly_model.joblib"
)


def predict_transaction_anomaly(transaction):
    if joblib is None or pd is None:
        is_anomaly = (
            transaction.transaction_type == "CASH_OUT"
            and float(transaction.amount) >= 18000
        )
        return {
            "success": True,
            "is_anomaly": is_anomaly,
            "anomaly_score": 0.85 if is_anomaly else 0.15,
            "message": "Heuristic anomaly fallback used because the trained model dependencies are unavailable.",
        }

    if not MODEL_PATH.exists():
        is_anomaly = (
            transaction.transaction_type == "CASH_OUT"
            and float(transaction.amount) >= 18000
        )
        return {
            "success": True,
            "is_anomaly": is_anomaly,
            "anomaly_score": 0.8 if is_anomaly else 0.2,
            "message": "Heuristic anomaly fallback used because the trained model has not been saved yet.",
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