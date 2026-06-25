"""
behavioral.py — Redrob behavioral signal scoring.

Key principle from the spec and JD:
"A perfect-on-paper candidate who hasn't logged in for 6 months and has a
5% recruiter response rate is, for hiring purposes, not actually available."

Behavioral signals act as a MULTIPLIER on technical score (0.65–1.05),
not an additive component. A great candidate who is inactive gets
meaningfully penalized but is not fully excluded unless signals are
catastrophically bad.

The 23 signals are documented in redrob_signals_doc.md.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any


def _parse_date(date_str: str | None) -> date | None:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def _recency_score(last_active_date: str | None) -> float:
    """
    Score 0.0–1.0 based on how recently the candidate was active.
    - Active in last 30 days → 1.0
    - Active in last 90 days → 0.85
    - Active in last 180 days → 0.65
    - Active in last 365 days → 0.45
    - >365 days inactive → 0.20
    """
    last = _parse_date(last_active_date)
    if not last:
        return 0.30

    today = date.today()
    days_inactive = (today - last).days

    if days_inactive <= 30:
        return 1.0
    elif days_inactive <= 60:
        return 0.92
    elif days_inactive <= 90:
        return 0.85
    elif days_inactive <= 180:
        return 0.65
    elif days_inactive <= 365:
        return 0.45
    else:
        return 0.20


def _availability_score(signals: dict) -> float:
    """
    Composite availability score based on engagement signals.
    Returns 0.0–1.0.
    """
    # 1. Open to work (binary but important)
    open_to_work = signals.get("open_to_work_flag", False)
    otw_score = 1.0 if open_to_work else 0.60

    # 2. Recruiter response rate (0.0–1.0)
    # Low response rate = candidate is not engaging, effectively not available
    rrr = signals.get("recruiter_response_rate", 0.5)
    if rrr is None:
        rrr = 0.5
    rrr_score = 0.3 + 0.7 * rrr  # range: 0.3 – 1.0

    # 3. Interview completion rate (0.0–1.0)
    # Low rate = flaky / not serious about changing roles
    icr = signals.get("interview_completion_rate", 0.5)
    if icr is None:
        icr = 0.5
    icr_score = 0.4 + 0.6 * icr  # range: 0.4 – 1.0

    # 4. Applications submitted (0–∞): actively applying → positive signal
    apps = signals.get("applications_submitted_30d", 0) or 0
    app_score = min(1.0, 0.5 + apps * 0.1) if apps > 0 else 0.6

    # 5. Notice period penalty (JD: sub-30 days preferred, 30+ "bar gets higher")
    notice = signals.get("notice_period_days", 60) or 60
    if notice <= 0:
        notice_score = 1.0  # immediately available
    elif notice <= 30:
        notice_score = 1.0
    elif notice <= 60:
        notice_score = 0.90
    elif notice <= 90:
        notice_score = 0.80
    else:
        notice_score = 0.70  # 90+ days is a significant friction

    # Weighted combination
    availability = (
        0.30 * otw_score
        + 0.30 * rrr_score
        + 0.20 * icr_score
        + 0.10 * app_score
        + 0.10 * notice_score
    )

    return availability


def _engagement_quality_score(signals: dict) -> float:
    """
    Quality of platform engagement — indicates active job searching and
    visible profile.
    """
    # Profile completeness
    completeness = signals.get("profile_completeness_score", 50.0) or 50.0
    comp_score = min(completeness / 100.0, 1.0)

    # Saved by recruiters in last 30 days (strong signal of market demand)
    saved = signals.get("saved_by_recruiters_30d", 0) or 0
    saved_score = min(saved / 10.0, 1.0)

    # Search appearances (are they indexed well / getting visibility?)
    search = signals.get("search_appearance_30d", 0) or 0
    search_score = min(search / 500.0, 1.0)

    # Verified contact info (basic trust signal)
    verified_email = signals.get("verified_email", False)
    verified_phone = signals.get("verified_phone", False)
    verified_score = (0.5 * verified_email + 0.5 * verified_phone)

    return (
        0.30 * comp_score
        + 0.30 * saved_score
        + 0.20 * search_score
        + 0.20 * verified_score
    )


def score_behavioral(candidate: dict[str, Any]) -> tuple[float, str]:
    """
    Main entry point for behavioral signal scoring.

    Returns (multiplier: 0.65–1.05, explanation: str)

    Note: this returns a MULTIPLIER, not a raw 0-1 score.
    The caller should multiply this against the technical base score.
    But we return it normalized 0–1 here; the weighting in rank.py
    applies it as a multiplier component.
    """
    signals = candidate.get("redrob_signals", {}) or {}

    last_active = signals.get("last_active_date")

    recency = _recency_score(last_active)
    availability = _availability_score(signals)
    engagement = _engagement_quality_score(signals)

    # Composite behavioral score
    score = (
        0.40 * recency
        + 0.40 * availability
        + 0.20 * engagement
    )

    # Offer acceptance rate (if available — not all have history)
    oar = signals.get("offer_acceptance_rate", -1)
    if oar is not None and oar >= 0:
        # High acceptance rate → reliable hire
        # Low acceptance → serial job-offer-getter who doesn't convert
        oar_adj = (oar - 0.5) * 0.05  # -0.025 to +0.025 adjustment
        score = min(1.0, max(0.0, score + oar_adj))

    # Build explanation
    rrr = signals.get("recruiter_response_rate", None)
    notice = signals.get("notice_period_days", None)
    otw = signals.get("open_to_work_flag", False)
    days_since_active = ""
    if last_active:
        last = _parse_date(last_active)
        if last:
            days_since_active = f"{(date.today() - last).days}d-ago"

    explanation_parts = []
    if days_since_active:
        explanation_parts.append(f"last-active={days_since_active}")
    if rrr is not None:
        explanation_parts.append(f"response-rate={rrr:.2f}")
    if not otw:
        explanation_parts.append("not-open-to-work")
    if notice and notice > 60:
        explanation_parts.append(f"notice={notice}d")

    return max(0.0, min(1.0, score)), "; ".join(explanation_parts) if explanation_parts else "signals-ok"
