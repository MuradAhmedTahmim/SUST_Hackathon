from __future__ import annotations

import os
from typing import Any

try:
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None


def _build_fallback_summary(alert: Any, language: str = "en") -> dict[str, Any]:
    provider_name = alert.provider.name if alert.provider else "the provider"
    confidence_percent = int(round(alert.confidence * 100)) if alert.confidence else 0

    english = (
        f"{provider_name} is showing elevated liquidity risk. "
        f"The alert is based on the current balance trend and the recent transaction pattern. "
        f"This is not proof of fraud and should be reviewed by an operations officer."
    )

    bangla = (
        f"{provider_name}-এ উচ্চতর লিকুইডিটি ঝুঁকি দেখা যাচ্ছে। "
        f"এই অ্যালার্টটি বর্তমান ব্যালেন্স প্রবণতা ও সাম্প্রতিক লেনদেনের ধরণ অনুযায়ী তৈরি করা হয়েছে। "
        f"এটি কোনো প্রতারণার প্রমাণ নয়; একজন অপারেশন অফিসার পর্যালোচনা করবেন।"
    )

    recommended_action = (
        "Verify the current provider balance, review recent transactions, "
        "and escalate to a risk analyst if the pattern persists."
    )

    return {
        "english": english,
        "bangla": bangla,
        "recommended_action": recommended_action,
        "confidence": confidence_percent,
        "supporting_evidence": [
            "Current alert severity",
            "Recent transaction pattern",
            "Balance trend against safety threshold",
        ],
        "false_positive_reason": "The signal may be a normal demand spike if recent activity is seasonal or expected.",
    }


def _call_openai(prompt: str) -> str | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            temperature=0.2,
        )
        return getattr(response, "output_text", None) or None
    except Exception:  # pragma: no cover - network/SDK failure fallback
        return None


def build_ai_summary(alert: Any, language: str = "en") -> dict[str, Any]:
    summary = _build_fallback_summary(alert, language=language)
    prompt = (
        f"Explain this alert in a safe and human-readable way for an operations team. "
        f"Alert title: {alert.title}. Severity: {alert.severity}. "
        f"Explanation: {alert.explanation}."
    )

    if language == "bn":
        prompt += " Respond in Bengali."
    else:
        prompt += " Respond in English."

    ai_response = _call_openai(prompt)
    if ai_response:
        summary["english" if language != "bn" else "bangla"] = ai_response.strip()

    return summary


def answer_question(alert: Any, question: str) -> str:
    normalized = question.strip().lower()

    if "fraud" in normalized:
        return (
            "This alert is not proof of fraud. It indicates unusual activity that should be reviewed by a human operator."
        )

    if "bangla" in normalized:
        return build_ai_summary(alert, language="bn")["bangla"]

    if "what should i do" in normalized or "next step" in normalized:
        return build_ai_summary(alert)["recommended_action"]

    return build_ai_summary(alert)["english"]
