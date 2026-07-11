from dataclasses import dataclass
from statistics import mean, pstdev
from decimal import Decimal


@dataclass
class AnomalyResult:
    is_unusual: bool
    score: float
    reason: str
    evidence: list[str]


def detect_velocity_anomaly(
    current_count: int,
    historical_counts: list[int],
) -> AnomalyResult:
    if len(historical_counts) < 5:
        return AnomalyResult(
            is_unusual=False,
            score=0,
            reason="Not enough historical information.",
            evidence=[
                "At least five historical periods are required."
            ],
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
            evidence=[
                f"Current transaction count: {current_count}",
                f"Historical average: {average:.2f}",
                f"Review threshold: {threshold:.2f}",
            ],
        )

    return AnomalyResult(
        is_unusual=False,
        score=0,
        reason="Activity is within the expected range.",
        evidence=[
            f"Current transaction count: {current_count}",
            f"Historical average: {average:.2f}",
        ],
    )


def detect_repeated_amount_anomaly(transactions, window_minutes: int = 15) -> AnomalyResult:
    if len(transactions) < 4:
        return AnomalyResult(False, 0, "Not enough transactions to evaluate repeated amounts.", [])

    sorted_transactions = sorted(transactions, key=lambda tx: tx.occurred_at)
    recent = [tx for tx in sorted_transactions if tx.occurred_at >= sorted_transactions[-1].occurred_at - timedelta(minutes=window_minutes)]

    if len(recent) < 4:
        return AnomalyResult(False, 0, "Not enough recent transactions to evaluate repeated amounts.", [])

    amounts = [float(tx.amount) for tx in recent]
    average_amount = mean(amounts)
    near_equal = [amount for amount in amounts if abs(amount - average_amount) <= average_amount * 0.05]

    if len(near_equal) >= 4:
        return AnomalyResult(
            True,
            84.0,
            "Several similar cash-out amounts occurred within a short period.",
            [
                f"Transactions: {len(recent)}",
                f"Amount range: ৳{min(amounts):,.0f}–৳{max(amounts):,.0f}",
                f"Average amount: ৳{average_amount:,.0f}",
                f"Confidence: 82%",
            ],
        )

    return AnomalyResult(False, 0, "Transaction amounts were not consistently similar.", [])


def detect_velocity_spike(transactions, window_minutes: int = 20, baseline_per_hour: int = 5) -> AnomalyResult:
    if len(transactions) < 3:
        return AnomalyResult(False, 0, "Not enough transactions for velocity analysis.", [])

    recent = [tx for tx in transactions if tx.occurred_at >= transactions[-1].occurred_at - timedelta(minutes=window_minutes)]
    if len(recent) < 3:
        return AnomalyResult(False, 0, "Not enough recent transactions for velocity analysis.", [])

    current_rate = len(recent) / (window_minutes / 60)
    if current_rate >= baseline_per_hour * 2.5:
        return AnomalyResult(
            True,
            80.0,
            "The transaction volume rose sharply within a short period.",
            [
                f"Current volume: {len(recent)} transactions in {window_minutes} minutes",
                f"Baseline: {baseline_per_hour} per hour",
                f"Current rate: {current_rate:.1f} per hour",
                f"Confidence: 80%",
            ],
        )

    return AnomalyResult(False, 0, "Transaction velocity is within the expected range.", [])