from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone


@dataclass
class ForecastResult:
    current_balance: float
    predicted_demand: float
    projected_balance: float
    shortage_probability: float
    estimated_shortage_at: object
    confidence: float


def calculate_confidence(data_status: str) -> float:
    factors = {
        "FRESH": 0.90,
        "DELAYED": 0.60,
        "MISSING": 0.20,
        "CONFLICTING": 0.35,
    }

    return factors.get(data_status, 0.50)


def forecast_liquidity(
    current_balance: float,
    average_depletion_per_hour: float,
    forecast_hours: int,
    safety_threshold: float,
    data_status: str = "FRESH",
) -> ForecastResult:
    average_depletion_per_hour = max(
        average_depletion_per_hour,
        0,
    )

    predicted_demand = (
        average_depletion_per_hour * forecast_hours
    )

    projected_balance = (
        current_balance - predicted_demand
    )

    estimated_shortage_at = None

    if average_depletion_per_hour > 0:
        usable_balance = max(
            current_balance - safety_threshold,
            0,
        )

        hours_remaining = (
            usable_balance / average_depletion_per_hour
        )

        estimated_shortage_at = (
            timezone.now() + timedelta(hours=hours_remaining)
        )

    deficit = max(
        safety_threshold - projected_balance,
        0,
    )

    shortage_probability = min(
        deficit / max(safety_threshold, 1),
        1,
    )

    confidence = calculate_confidence(data_status)

    return ForecastResult(
        current_balance=round(current_balance, 2),
        predicted_demand=round(predicted_demand, 2),
        projected_balance=round(projected_balance, 2),
        shortage_probability=round(
            shortage_probability,
            4,
        ),
        estimated_shortage_at=estimated_shortage_at,
        confidence=confidence,
    )