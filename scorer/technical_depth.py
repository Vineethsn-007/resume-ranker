"""
technical_depth.py — Evidence-backed skill scoring with honeypot detection.

The spec says: "expert proficiency in 10 skills with 0 years used" is a
honeypot pattern. This module scores skills based on EVIDENCE, not presence.

Key insight: a skill is only valuable if it's corroborated by at least one of:
  - Meaningful duration_months (>=6 months of actual use)
  - Real endorsements (>= 5, suggesting peer validation)
  - A matching term in career history descriptions
  - An assessment score on the Redrob platform

Raw skill count (the trap the sample submission fell into) is NOT used.
"""

from __future__ import annotations
import math
import re
from typing import Any


# ─── Skill relevance taxonomy ─────────────────────────────────────────────────

# Weight 1.0: Core JD requirements (must-have from "Things you absolutely need")
CORE_SKILLS = {
    # Embeddings & retrieval
    "sentence transformers", "sentence-transformers",
    "embeddings", "text embeddings",
    "openai embeddings",
    "bge", "e5",
    "faiss", "pinecone", "weaviate", "qdrant", "milvus",
    "opensearch", "elasticsearch", "vector search", "vector database",
    "hybrid search", "semantic search",
    # Ranking & retrieval systems
    "ranking", "information retrieval", "search relevance",
    "learning to rank", "ltr", "bm25", "colbert", "reranking",
    # LLMs
    "llm", "large language model", "rag",
    "langchain", "llamaindex",
    "fine-tuning", "fine-tuning llms", "lora", "qlora", "peft",
    # Eval frameworks
    "ndcg", "mrr", "map", "ranking evaluation",
    "a/b testing", "ab testing",
    # ML fundamentals
    "pytorch", "tensorflow", "scikit-learn", "xgboost",
    "ml pipeline", "mlops", "mlflow", "kubeflow",
    "python", "deep learning", "neural networks",
    # NLP
    "nlp", "natural language processing", "bert", "transformers",
    "text classification", "named entity recognition", "ner",
    "question answering", "text generation",
    # Recommendation
    "recommendation systems", "collaborative filtering",
    "matrix factorization",
}

# Weight 0.6: Nice-to-have (from "Things we'd like you to have")
SECONDARY_SKILLS = {
    "distributed systems", "kafka", "spark", "airflow",
    "kubernetes", "docker", "aws", "gcp", "azure",
    "redis", "postgresql", "sql",
    "prompt engineering", "llama", "mistral", "gemini",
    "graph neural networks", "gnn",
    "data engineering", "feature engineering",
    "model serving", "triton", "onnx", "tensorrt",
    "computer vision",  # note: JD doesn't want pure CV, but it's a skill
    "time series", "forecasting",
    "speech recognition",  # JD notes CV/speech/robotics as a negative for *primary* expertise
    "open source", "git", "ci/cd",
}

# Weight 0.15: Irrelevant to the JD — present but don't count
IRRELEVANT_SKILLS = {
    "hr management", "recruitment", "seo", "marketing",
    "accounting", "financial modeling", "excel",
    "graphic design", "photoshop", "figma",
    "autocad", "solidworks",
    "content writing", "copywriting",
    "customer service", "crm",
    "react", "angular", "vue", "tailwind", "css", "html",
    "java", ".net", "c#", "c++", "go", "rust",  # engineering but not ML
    "ios", "android", "swift", "kotlin",
    "sales", "negotiation", "cold calling",
}


def _get_skill_weight(skill_name: str) -> float:
    """Return relevance weight for a skill name."""
    name = skill_name.lower().strip()

    # Check irrelevant first (fast path)
    if name in IRRELEVANT_SKILLS:
        return 0.1

    # Check core
    if name in CORE_SKILLS:
        return 1.0
    for core in CORE_SKILLS:
        if core in name or name in core:
            return 1.0

    # Check secondary
    if name in SECONDARY_SKILLS:
        return 0.6
    for sec in SECONDARY_SKILLS:
        if sec in name or name in sec:
            return 0.6

    # Unknown skill — mild positive
    return 0.25


def _proficiency_value(proficiency: str) -> float:
    """Convert proficiency string to numeric value."""
    return {
        "beginner": 0.25,
        "intermediate": 0.55,
        "advanced": 0.85,
        "expert": 1.0,
    }.get(proficiency.lower(), 0.3)


def _skill_evidence_score(skill: dict, career_descs: str) -> float:
    """
    Score a single skill entry based on evidence, NOT raw presence.

    Honeypot pattern: expert + 0 duration + 0 endorsements → penalize
    Good signal: reasonable duration + endorsements + career match
    """
    proficiency = skill.get("proficiency", "beginner")
    endorsements = skill.get("endorsements", 0) or 0
    duration = skill.get("duration_months", 0) or 0
    name = skill.get("name", "")
    name_lower = name.lower().strip()

    prof_val = _proficiency_value(proficiency)

    # ── Honeypot detection ─────────────────────────────────────────────────
    # Flag: expert/advanced with BOTH duration=0 AND endorsements=0
    # This is literally the honeypot pattern from the spec
    if proficiency in ("expert", "advanced") and duration == 0 and endorsements == 0:
        return 0.05  # near-zero evidence despite high claimed proficiency

    # ── Evidence factors ────────────────────────────────────────────────────

    # Duration factor: 0 months → low; 12+ months → full credit
    if duration == 0:
        dur_factor = 0.1
    elif duration < 6:
        dur_factor = 0.35
    elif duration < 12:
        dur_factor = 0.60
    elif duration < 24:
        dur_factor = 0.80
    elif duration < 48:
        dur_factor = 0.95
    else:
        dur_factor = 1.0

    # Endorsement factor: 0 = unvalidated, 10+ = well-validated
    if endorsements == 0:
        end_factor = 0.3
    elif endorsements < 5:
        end_factor = 0.55
    elif endorsements < 15:
        end_factor = 0.80
    elif endorsements < 30:
        end_factor = 0.95
    else:
        end_factor = 1.0

    # Career description corroboration
    career_hit = 0.0
    if name_lower and career_descs:
        # Check if skill name (or synonym) appears in career descriptions
        escaped = re.escape(name_lower)
        if re.search(escaped, career_descs, re.IGNORECASE):
            career_hit = 0.3

    # Combine evidence: weighted average of duration, endorsements, career
    evidence = 0.50 * dur_factor + 0.30 * end_factor + 0.20 * (career_hit / 0.3 if career_hit else 0)

    # Final skill score: proficiency × evidence (can't claim expert credit without evidence)
    return prof_val * evidence


def _check_skill_plausibility(skills: list[dict], yoe: float) -> float:
    """
    Plausibility multiplier for the overall skill set.
    Detects: claiming expert in many skills with 0 duration (honeypot pattern).

    Returns 0.4–1.0 (penalty applied to overall skill score).
    """
    if not skills:
        return 1.0

    suspicious = 0
    for s in skills:
        prof = s.get("proficiency", "")
        dur = s.get("duration_months", 0) or 0
        end = s.get("endorsements", 0) or 0
        if prof in ("expert", "advanced") and dur == 0 and end == 0:
            suspicious += 1

    ratio = suspicious / len(skills) if skills else 0

    # High ratio of suspicious skills → honeypot signal
    if ratio > 0.6:
        return 0.35
    elif ratio > 0.4:
        return 0.60
    elif ratio > 0.2:
        return 0.85
    return 1.0


def _assessment_score(redrob_signals: dict) -> float:
    """
    Score from Redrob platform skill assessments.
    These are third-party validated scores, so they count as strong evidence.
    Returns 0.0–1.0
    """
    assessments = redrob_signals.get("skill_assessment_scores", {}) or {}
    if not assessments:
        return 0.0

    # Only count assessments for relevant skills
    relevant_scores = []
    for skill_name, score in assessments.items():
        weight = _get_skill_weight(skill_name)
        if weight >= 0.6:  # core or secondary skills only
            relevant_scores.append(score * weight)

    if not relevant_scores:
        return 0.0

    return min(sum(relevant_scores) / (len(relevant_scores) * 100.0), 1.0)


def score_technical_depth(candidate: dict[str, Any]) -> tuple[float, str]:
    """
    Main entry point for technical depth scoring.
    Returns (score: 0.0–1.0, explanation: str)
    """
    skills = candidate.get("skills", []) or []
    career_history = candidate.get("career_history", []) or []
    redrob_signals = candidate.get("redrob_signals", {}) or {}
    profile = candidate.get("profile", {})
    yoe = profile.get("years_of_experience", 0) or 0

    # Build combined career description text for corroboration
    career_descs = " ".join(
        j.get("description", "") for j in career_history
    ).lower()

    # Plausibility check
    plausibility = _check_skill_plausibility(skills, yoe)

    # Score each skill
    core_scores = []
    secondary_scores = []
    total_weighted = 0.0
    core_skill_hits = []

    for skill in skills:
        name = skill.get("name", "")
        weight = _get_skill_weight(name)
        if weight < 0.2:
            continue  # Skip irrelevant skills entirely

        evidence_score = _skill_evidence_score(skill, career_descs)
        contribution = weight * evidence_score

        if weight >= 0.8:
            core_scores.append(contribution)
            if evidence_score > 0.3:
                core_skill_hits.append(name)
        elif weight >= 0.5:
            secondary_scores.append(contribution)

        total_weighted += contribution

    # Core skill bonus: having many strongly-evidenced core skills is the goal
    core_count = len(core_scores)
    secondary_count = len(secondary_scores)

    # Assessment boost
    assessment_boost = _assessment_score(redrob_signals) * 0.15

    # GitHub activity: a proxy for real engineering work
    github = redrob_signals.get("github_activity_score", -1)
    github_boost = 0.0
    if github > 0:
        github_boost = min(github / 100.0 * 0.1, 0.10)

    # Base score: normalize weighted sum
    # 5 well-evidenced core skills → score ~0.7; 8+ → 0.9
    base = min(total_weighted / 8.0, 0.85)

    # Plausibility penalty
    base *= plausibility

    # Add assessment and GitHub boosts
    score = min(base + assessment_boost + github_boost, 1.0)

    # Build explanation
    top_skills = core_skill_hits[:3] if core_skill_hits else []
    explanation_parts = [
        f"core-skills-evidenced={core_count}",
    ]
    if top_skills:
        explanation_parts.append("top: " + ", ".join(top_skills))
    if plausibility < 0.8:
        explanation_parts.append(f"plausibility-penalty={plausibility:.2f}")
    if assessment_boost > 0.02:
        explanation_parts.append(f"assessment-boost={assessment_boost:.2f}")

    return max(0.0, score), "; ".join(explanation_parts)
