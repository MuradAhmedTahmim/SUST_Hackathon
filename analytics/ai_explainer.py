from __future__ import annotations

from typing import Any


def _generate_summary_text(alert: Any, language: str = "en") -> str:
    provider_name = alert.provider.name if alert.provider else "the provider"
    severity = alert.severity.lower()
    confidence_percent = int(round(alert.confidence * 100)) if alert.confidence else 0
    explanation = alert.explanation or "No detailed explanation is available."

    if language == "bn":
        return (
            f"{provider_name}-এ একটি {severity} লিকুইডিটি অ্যালার্ট তৈরি হয়েছে। "
            f"এই সিগন্যালটি {confidence_percent}% আত্মবিশ্বাস সহ ব্যালেন্স প্রবণতা এবং সাম্প্রতিক লেনদেন কার্যকলাপের উপর ভিত্তি করে। "
            f"বিবরণ: {explanation}"
        )

    return (
        f"A {severity} liquidity alert was generated for {provider_name}. "
        f"The system is {confidence_percent}% confident and based this on current balance trends and recent transaction behavior. "
        f"Explanation: {explanation}"
    )


def _generate_recommended_action(alert: Any) -> str:
    if alert.severity == "CRITICAL":
        return (
            "Contact the responsible operations officer immediately, verify the current provider balance, "
            "and arrange emergency liquidity support if required."
        )

    if alert.severity == "HIGH":
        return (
            "Review the provider balance and recent transactions, then schedule support within the next 4 hours."
        )

    return (
        "Monitor the position closely and verify the latest balance data before taking further action."
    )


def build_ai_summary(alert: Any, language: str = "en") -> dict[str, Any]:
    provider_name = alert.provider.name if alert.provider else "the provider"
    confidence_percent = int(round(alert.confidence * 100)) if alert.confidence else 0

    return {
        "english": _generate_summary_text(alert, language="en"),
        "bangla": _generate_summary_text(alert, language="bn"),
        "recommended_action": _generate_recommended_action(alert),
        "confidence": confidence_percent,
        "supporting_evidence": [
            "Alert severity",
            "Provider balance trend",
            "Recent transaction pattern",
        ],
        "false_positive_reason": (
            "The movement may reflect genuine demand or normal transactional variation, "
            "so please verify with the agent and provider data."
        ),
    }


def answer_question(alert: Any, question: str) -> str:
    normalized = question.strip().lower()

    if "fraud" in normalized:
        return (
            "This alert is not proof of fraud. It highlights unusual liquidity behavior that needs human review."
        )

    if "bangla" in normalized:
        return build_ai_summary(alert, language="bn")["bangla"]

    if "what should i do" in normalized or "next step" in normalized:
        return build_ai_summary(alert)["recommended_action"]

    if "confidence" in normalized or "certain" in normalized:
        return (
            f"The alert confidence is {build_ai_summary(alert)[ 'confidence']}%. "
            "Use this as an advisory signal, not definitive proof."
        )

    return build_ai_summary(alert)["english"]
