"""
role_fit.py — Title and career role-fit scoring.

THE KEY MODULE: This is what prevents the keyword-stuffer trap.
The JD spec explicitly says: "A candidate whose title is 'Marketing Manager'
is not a fit, no matter how perfect their skill list looks."

This module scores role fit based on:
1. Current title classification (primary signal)
2. Career title trajectory (have they ever held an ML/AI/data role?)
3. Career progression direction (moving toward or away from ML/AI?)

Score is 0.0–1.0. This acts as a gating multiplier on the final score,
not just an additive component. A fundamentally wrong-title candidate
cannot score above ~0.3 total regardless of skills.
"""

from __future__ import annotations
import re
from typing import Any


# ─── Title taxonomies ────────────────────────────────────────────────────────

# Tier 1: Directly relevant titles — strong match
TIER1_TITLES = {
    "ml engineer", "machine learning engineer", "senior ml engineer",
    "staff ml engineer", "principal ml engineer", "lead ml engineer",
    "ai engineer", "senior ai engineer", "staff ai engineer",
    "applied ml engineer", "applied ai engineer",
    "nlp engineer", "nlp scientist", "search engineer",
    "retrieval engineer", "ranking engineer", "recommendation systems engineer",
    "recommendation engineer", "search relevance engineer",
    "applied scientist", "research engineer", "ai research engineer",
    "data scientist", "senior data scientist", "staff data scientist",
    "principal data scientist", "lead data scientist",
    "ml research engineer", "research scientist",
    "inference engineer", "model optimization engineer",
    "vector search engineer", "embedding engineer",
    "junior ml engineer",
}

# Tier 2: Adjacent titles — partial match, can score well with strong career evidence
TIER2_TITLES = {
    "data engineer", "senior data engineer", "staff data engineer",
    "backend engineer", "senior backend engineer",
    "software engineer", "senior software engineer",
    "full stack engineer", "full stack developer",
    "platform engineer", "infrastructure engineer",
    "ml platform engineer", "mlops engineer",
    "devops engineer", "site reliability engineer",
    "python developer", "python engineer",
    "ai researcher", "research analyst",
    "cloud engineer", "cloud architect",
    "solutions architect",  # only counts if AI/ML focused (handled in career boost)
    "technical lead", "tech lead",
    "product engineer",
    "qa engineer",  # weak adjacency
}

# Tier 3: Engineering-but-wrong-domain — very weak match
TIER3_TITLES = {
    "frontend engineer", "frontend developer",
    "mobile developer", "ios developer", "android developer",
    "java developer", ".net developer", "c# developer",
    "embedded engineer", "firmware engineer",
    "network engineer", "security engineer",
    "mechanical engineer", "civil engineer",
    "electrical engineer",
    "database administrator", "dba",
    "business intelligence engineer", "bi engineer",
    "bi developer",
    "java engineer",
}

# Disqualifying titles — strong negative signal per JD
DISQUALIFYING_TITLES = {
    "hr manager", "human resources manager", "hr business partner",
    "talent acquisition", "recruiter", "technical recruiter",
    "marketing manager", "content writer", "content manager",
    "copywriter", "seo specialist", "brand manager",
    "graphic designer", "ui designer", "ux designer",
    "accountant", "financial analyst", "finance manager",
    "business analyst",  # weak if no ML pivot in career
    "operations manager", "operations director",
    "project manager", "program manager",
    "product manager",  # unless AI/ML PM — handled below
    "sales executive", "sales manager", "account executive",
    "account manager",
    "customer support", "customer success",
    "supply chain manager", "logistics manager",
}

# Keywords that signal ML/AI substance in job descriptions
CAREER_AI_KEYWORDS = [
    r"\bembedding[s]?\b", r"\bvector\b", r"\bfaiss\b", r"\bpinecone\b",
    r"\bweaviate\b", r"\bqdrant\b", r"\bmilvus\b", r"\bopensearch\b",
    r"\belasticsearch\b", r"\bsemantic search\b", r"\bhybrid search\b",
    r"\bsentence.transformer", r"\bbge\b", r"\be5\b",
    r"\breranking\b", r"\breranka?\b", r"\bRAG\b", r"\bretrieval.augmented",
    r"\blangchain\b", r"\bllm\b", r"\bfine.tun", r"\bloRA\b",
    r"\btransformer\b", r"\bbert\b", r"\bgpt\b", r"\bllama\b",
    r"\bretriev", r"\brank", r"\brecommend",
    r"\bndcg\b", r"\bmrr\b", r"\bmap score\b",
    r"\bml pipeline\b", r"\bmodel.serv", r"\binference",
    r"\bpytorch\b", r"\btensorflow\b", r"\bscikit", r"\bxgboost\b",
    r"\bfeature engineer", r"\bmlflow\b", r"\bkubeflow\b",
    r"\bdata science\b", r"\bneural network", r"\bdeep learning\b",
    r"\bnlp\b", r"\bnatural language",
]

CAREER_AI_COMPILED = [re.compile(p, re.IGNORECASE) for p in CAREER_AI_KEYWORDS]

# Consulting-only firms (JD says "never worked at a product company" is a disqualifier)
PURE_CONSULTING_FIRMS = {
    "tcs", "tata consultancy", "infosys", "wipro", "accenture",
    "cognizant", "capgemini", "hcl", "tech mahindra", "mphasis",
    "hexaware", "l&t infotech", "ltimindtree", "mindtree",
    "persistent systems", "niit technologies", "mastech", "zensar",
    "syntel", "kpit", "cyient", "birlasoft",
}


def _normalize_title(title: str) -> str:
    """Lowercase, strip, remove common modifiers for matching."""
    t = title.lower().strip()
    # Remove common seniority prefixes/suffixes for base matching
    t = re.sub(r"\b(junior|senior|staff|principal|lead|associate|founding|sr\.|jr\.)\s*", "", t)
    t = t.strip()
    return t


def _classify_title(title: str) -> tuple[str, float]:
    """
    Returns (tier_label, base_score) for a given job title.
    base_score: 0.0–1.0
    """
    raw = title.lower().strip()
    norm = _normalize_title(title)

    # Check each tier
    if norm in TIER1_TITLES or raw in TIER1_TITLES:
        return ("tier1", 1.0)

    # Fuzzy tier1: contains key phrases
    for pattern in ["ml engineer", "machine learning", "ai engineer", "nlp engineer",
                     "search engineer", "recommendation", "retrieval", "ranking engineer",
                     "applied scientist", "data scientist", "research engineer",
                     "vector search", "nlp scientist"]:
        if pattern in raw:
            return ("tier1", 1.0)

    if norm in TIER2_TITLES or raw in TIER2_TITLES:
        return ("tier2", 0.55)

    if norm in TIER3_TITLES or raw in TIER3_TITLES:
        return ("tier3", 0.2)

    # Check disqualifying
    for dq_title in DISQUALIFYING_TITLES:
        if dq_title in raw:
            return ("disqualified", 0.08)

    # Fallback: unknown title — treat as tier2 but low end
    return ("unknown", 0.35)


def _career_ai_evidence_score(career_history: list[dict]) -> float:
    """
    Score 0.0–1.0 based on how much ML/AI work evidence is in career descriptions.
    Each job description is searched for AI/ML keywords.
    """
    if not career_history:
        return 0.0

    total_weighted_hits = 0.0
    total_months = 0

    for job in career_history:
        desc = job.get("description", "")
        dur = job.get("duration_months", 0) or 0

        # Count distinct keyword matches in this description
        hits = sum(1 for p in CAREER_AI_COMPILED if p.search(desc))

        # Recency weighting: current role gets 2x, others 1x
        recency = 2.0 if job.get("is_current", False) else 1.0

        # Weight by duration (longer tenure = more real experience)
        dur_weight = min(dur / 24.0, 2.0)  # cap at 2x for 24+ months

        total_weighted_hits += hits * recency * max(dur_weight, 0.5)
        total_months += dur

    # Normalize: 15+ keyword-weighted hits across career → max score
    score = min(total_weighted_hits / 20.0, 1.0)
    return score


def _career_title_trajectory(career_history: list[dict]) -> float:
    """
    Returns a trajectory score 0.0–1.0.
    Did this person ever hold an ML/AI role in their history?
    Are they moving toward or away from ML/AI?
    """
    if not career_history:
        return 0.0

    # Sort by start date to get trajectory direction
    sorted_jobs = sorted(career_history, key=lambda j: j.get("start_date", ""))

    tier1_count = 0
    tier2_count = 0
    most_recent_tier = None

    for i, job in enumerate(sorted_jobs):
        tier, _ = _classify_title(job.get("title", ""))
        if tier == "tier1":
            tier1_count += 1
        elif tier == "tier2":
            tier2_count += 1
        if i == len(sorted_jobs) - 1:  # most recent
            most_recent_tier = tier

    # Strong signal: most recent role is tier1
    if most_recent_tier == "tier1":
        return min(0.5 + tier1_count * 0.15, 1.0)

    # Moderate: has had tier1 roles before, now in tier2
    if tier1_count > 0 and most_recent_tier == "tier2":
        return 0.45

    # Some tier1 history, now in wrong-tier role
    if tier1_count > 0:
        return 0.3

    # Only tier2, never tier1 — possible transition candidate
    if tier2_count >= 2 and most_recent_tier == "tier2":
        return 0.2

    return 0.05


def _is_pure_consulting_career(career_history: list[dict]) -> bool:
    """Returns True if candidate's ENTIRE career is at pure consulting/services firms."""
    if not career_history:
        return False
    for job in career_history:
        company = job.get("company", "").lower().strip()
        if not any(c in company for c in PURE_CONSULTING_FIRMS):
            return False  # Found at least one non-consulting company
    return True


def score_role_fit(candidate: dict[str, Any]) -> tuple[float, str]:
    """
    Main entry point for role fit scoring.

    Returns (score: 0.0–1.0, explanation: str)
    """
    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", [])

    current_title = profile.get("current_title", "")
    yoe = profile.get("years_of_experience", 0) or 0

    title_tier, title_score = _classify_title(current_title)

    # Career evidence: AI keywords in job descriptions
    career_ai = _career_ai_evidence_score(career_history)

    # Career title trajectory
    trajectory = _career_title_trajectory(career_history)

    # Compose the role fit score
    if title_tier == "tier1":
        # Direct match: title is the primary signal; career_ai is a confirmation boost
        score = 0.70 + 0.20 * career_ai + 0.10 * trajectory
    elif title_tier == "tier2":
        # Adjacent: need strong career evidence to overcome title gap
        score = 0.35 + 0.35 * career_ai + 0.20 * trajectory
        # Extra boost if career shows strong AI trajectory
        if career_ai > 0.6:
            score = min(score + 0.10, 0.85)
    elif title_tier == "tier3":
        # Wrong domain engineering: only career history can save them
        score = 0.05 + 0.25 * career_ai + 0.15 * trajectory
    elif title_tier == "disqualified":
        # HR, Marketing, etc.: hard ceiling even with AI skills
        score = 0.03 + 0.12 * career_ai + 0.05 * trajectory
        score = min(score, 0.25)  # hard cap
    else:
        # Unknown title
        score = 0.20 + 0.35 * career_ai + 0.15 * trajectory

    # Pure consulting penalty (JD explicitly mentions this)
    if _is_pure_consulting_career(career_history):
        score *= 0.75

    # YoE range: JD wants 5–9 years
    # Small bonus for 5–9 YoE, slight penalty for <3 or >15
    if 5.0 <= yoe <= 9.0:
        yoe_factor = 1.0
    elif 3.0 <= yoe < 5.0:
        yoe_factor = 0.90
    elif 9.0 < yoe <= 12.0:
        yoe_factor = 0.95
    elif yoe > 12.0:
        yoe_factor = 0.85  # senior but may be over-seniored
    elif yoe < 3.0:
        yoe_factor = 0.75
    else:
        yoe_factor = 1.0

    score *= yoe_factor
    score = max(0.0, min(1.0, score))

    # Build explanation
    reasoning_parts = [f"{current_title} ({yoe:.1f}yr)"]
    if title_tier == "tier1":
        reasoning_parts.append("direct-role-match")
    elif title_tier == "tier2":
        reasoning_parts.append(f"adjacent-title; career-AI-evidence={career_ai:.2f}")
    elif title_tier == "disqualified":
        reasoning_parts.append("title-mismatch[HARD]")
    else:
        reasoning_parts.append(f"title-tier={title_tier}; career-AI={career_ai:.2f}")

    return score, "; ".join(reasoning_parts)
