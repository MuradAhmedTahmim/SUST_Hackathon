from datetime import timedelta
from decimal import Decimal
from statistics import mean, pstdev
from dataclasses import dataclass


@dataclass
class AnomalyResult:
    is_unusual: bool
    score: float
    reason: str
    evidence: dict
    severity: str = "low"
    requires_human_review: bool = False
    possible_normal_explanation: str = ""


def detect_velocity_anomaly(
    current_count: int,
    historical_counts: list[int],
) -> AnomalyResult:
    if len(historical_counts) < 5:
        return AnomalyResult(
            is_unusual=False,
            score=0,
            reason="Not enough historical information.",
            evidence={
                "message": "At least five historical periods are required."
            },
        )

    average = mean(historical_counts)
    deviation = pstdev(historical_counts)
    threshold = average + (3 * deviation)

    if current_count > threshold:
        ratio = current_count / max(average, 1)
        score = min(100, 50 + ratio * 10)

        return AnomalyResult(
            is_unusual=True,
            score=round(score, 2),
            reason=(
                "Transaction activity is significantly "
                "higher than the normal pattern."
            ),
            evidence={
                "current_transaction_count": current_count,
                "historical_average": round(average, 2),
                "review_threshold": round(threshold, 2),
            },
        )

    return AnomalyResult(
        is_unusual=False,
        score=0,
        reason="Activity is within the expected range.",
        evidence={
            "current_transaction_count": current_count,
            "historical_average": round(average, 2),
        },
    )


def detect_repeated_amount_anomaly(transactions, window_minutes: int = 15) -> AnomalyResult:
    if len(transactions) < 4:
        return AnomalyResult(False, 0, "Not enough transactions to evaluate repeated amounts.", {}, severity="low", requires_human_review=False)

    sorted_transactions = sorted(transactions, key=lambda tx: tx.occurred_at)
    recent = [tx for tx in sorted_transactions if tx.occurred_at >= sorted_transactions[-1].occurred_at - timedelta(minutes=window_minutes)]

    if len(recent) < 4:
        return AnomalyResult(False, 0, "Not enough recent transactions to evaluate repeated amounts.", {}, severity="low", requires_human_review=False)

    amounts = [float(tx.amount) for tx in recent]
    average_amount = mean(amounts)
    near_equal = [amount for amount in amounts if abs(amount - average_amount) <= average_amount * 0.05]

    if len(near_equal) >= 4:
        time_span = int((sorted_transactions[-1].occurred_at - sorted_transactions[0].occurred_at).total_seconds() // 60)
        evidence = {
            "transaction_count": str(len(recent)),
            "time_window_minutes": str(max(window_minutes, time_span)),
            "minimum_amount": str(int(min(amounts))),
            "maximum_amount": str(int(max(amounts))),
            "average_amount": str(int(average_amount)),
        }
        return AnomalyResult(
            True,
            0.84,
            "Unusual activity requiring review.",
            evidence,
            severity="high",
            requires_human_review=True,
            possible_normal_explanation="High seasonal demand or a legitimate cash-out spike may also explain this pattern.",
        )

    return AnomalyResult(False, 0, "Transaction amounts were not consistently similar.", {}, severity="low", requires_human_review=False)


def detect_velocity_spike(transactions, window_minutes: int = 20, baseline_per_hour: int = 5) -> AnomalyResult:
    if len(transactions) < 3:
        return AnomalyResult(False, 0, "Not enough transactions for velocity analysis.", {}, severity="low", requires_human_review=False)

    recent = [tx for tx in transactions if tx.occurred_at >= transactions[-1].occurred_at - timedelta(minutes=window_minutes)]
    if len(recent) < 3:
        return AnomalyResult(False, 0, "Not enough recent transactions for velocity analysis.", {}, severity="low", requires_human_review=False)

    current_rate = len(recent) / (window_minutes / 60)
    if current_rate >= baseline_per_hour * 2.5:
        return AnomalyResult(
            True,
            0.80,
            "The transaction volume rose sharply within a short period.",
            {
                "transaction_count": len(recent),
                "time_window_minutes": window_minutes,
                "current_rate_per_hour": round(current_rate, 1),
                "baseline_per_hour": baseline_per_hour,
            },
            severity="medium",
            requires_human_review=True,
            possible_normal_explanation="A legitimate seasonal rush or known promotion could explain the spike.",
        )

    return AnomalyResult(False, 0, "Transaction velocity is within the expected range.", {}, severity="low", requires_human_review=False)