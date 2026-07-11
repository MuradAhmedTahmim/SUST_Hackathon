from dataclasses import dataclass
from statistics import mean, pstdev


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