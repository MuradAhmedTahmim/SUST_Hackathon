import json
from pathlib import Path
from math import exp

MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "local_forecast_model.json"


class StandardScalerApprox:
    def __init__(self, mean, scale):
        self.mean_ = mean
        self.scale_ = scale

    def transform(self, X):
        transformed = []
        for row in X:
            transformed.append([
                (x - mean) / scale if scale != 0 else 0.0
                for x, mean, scale in zip(row, self.mean_, self.scale_)
            ])
        return transformed


class LocalForecastModel:
    def __init__(self):
        self.model_data = None
        self.scaler = None
        self._load_model()

    def _load_model(self):
        if not MODEL_PATH.exists():
            return

        with open(MODEL_PATH, "r", encoding="utf-8") as f:
            self.model_data = json.load(f)

        self.scaler = StandardScalerApprox(
            self.model_data["scaler_mean"],
            self.model_data["scaler_scale"],
        )

    def is_ready(self) -> bool:
        return self.model_data is not None and self.scaler is not None

    def predict_probability(self, features):
        if not self.is_ready():
            return None

        x = self.scaler.transform([features])[0]
        logit = sum(
            coef * val
            for coef, val in zip(self.model_data["coef"], x)
        ) + self.model_data["intercept"]
        return 1.0 / (1.0 + exp(-logit))


local_forecast_model = LocalForecastModel()
