#!/usr/bin/env python3
"""
rank.py — Redrob Intelligent Candidate Ranking Challenge

Main ranking script. Produces a valid submission CSV.

Usage:
    python rank.py --candidates ./data/candidates.jsonl --out ./submission.csv
    python rank.py --candidates ./data/sample_candidates.json --out ./sample_out.csv --format json

Architecture:
    Five-component scoring pipeline:
    1. Role fit (35%):     Title gate + career trajectory. THE primary signal.
                           Prevents keyword-stuffer trap.
    2. Technical depth (30%): Evidence-backed skill scoring with honeypot detection.
    3. Career substance (20%): Career description NLP. Catches Tier-5 hidden gems.
    4. Behavioral (10%):  Redrob engagement/availability multiplier.
    5. Education (5%):    Degree relevance and institution tier.

    Total score = weighted sum, then tie-break by candidate_id ascending.

Compute constraints:
    - No network calls (zero external API calls in this file)
    - CPU only (no .cuda(), no GPU libs)
    - Target: <5 min, <8 GB RAM on 100K candidates
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

from scorer.role_fit import score_role_fit
from scorer.technical_depth import score_technical_depth
from scorer.career_substance import score_career_substance
from scorer.behavioral import score_behavioral

# ─── Component weights ───────────────────────────────────────────────────────
WEIGHTS = {
    "role_fit":        0.35,
    "technical_depth": 0.30,
    "career_substance": 0.20,
    "behavioral":      0.10,
    "education":       0.05,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"

# ─── Education scoring ───────────────────────────────────────────────────────

RELEVANT_FIELDS = {
    "computer science", "cs", "information technology", "it",
    "artificial intelligence", "machine learning", "data science",
    "statistics", "mathematics", "math", "electrical engineering",
    "electronics", "computational linguistics", "nlp",
    "software engineering", "information systems",
}

DEGREE_TIERS = {
    # PhDs count heavily for research signal (but JD wants production — net neutral)
    "ph.d": 0.85, "phd": 0.85, "doctorate": 0.85,
    # Masters are strong
    "m.tech": 1.0, "m.e.": 1.0, "m.s.": 1.0, "ms": 0.95, "m.sc.": 0.90,
    "mca": 0.85, "m.c.a.": 0.85, "pgdm": 0.75,
    # Bachelors
    "b.tech": 0.80, "b.e.": 0.80, "be": 0.75, "b.s.": 0.75,
    "bsc": 0.70, "b.sc.": 0.70, "bca": 0.65, "b.c.a.": 0.65,
}

INSTITUTION_TIER_SCORES = {
    "tier_1": 1.0,
    "tier_2": 0.80,
    "tier_3": 0.60,
    "tier_4": 0.40,
    "unknown": 0.50,
}


def score_education(candidate: dict[str, Any]) -> float:
    """Score 0.0–1.0 based on education relevance and quality."""
    education = candidate.get("education", []) or []
    if not education:
        return 0.30  # no education info — slight penalty vs unknown

    best_score = 0.0

    for edu in education:
        field = (edu.get("field_of_study") or "").lower()
        degree = (edu.get("degree") or "").lower()
        tier = edu.get("tier", "unknown")

        # Field relevance
        field_score = 0.3  # default: unrelated
        for rel in RELEVANT_FIELDS:
            if rel in field:
                field_score = 1.0
                break

        # Degree tier
        degree_score = 0.5  # default
        for deg_key, deg_val in DEGREE_TIERS.items():
            if deg_key in degree:
                degree_score = deg_val
                break

        # Institution tier
        inst_score = INSTITUTION_TIER_SCORES.get(tier, 0.50)

        # Combine
        edu_score = 0.40 * field_score + 0.30 * degree_score + 0.30 * inst_score
        best_score = max(best_score, edu_score)

    return best_score


# ─── Reasoning generation ─────────────────────────────────────────────────────

def _generate_reasoning(
    candidate: dict[str, Any],
    scores: dict[str, float],
    total_score: float,
    rank: int,
) -> str:
    """
    Generate a specific, non-templated reasoning string referencing
    actual facts from the candidate's profile.

    Stage 4 checks: no hallucinated skills, no identical strings,
    tone should match rank (rank 90+ should sound marginal).
    """
    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", []) or []
    skills = candidate.get("skills", []) or []
    signals = candidate.get("redrob_signals", {}) or {}

    title = profile.get("current_title", "Unknown")
    yoe = profile.get("years_of_experience", 0) or 0
    company = profile.get("current_company", "")

    # Get top evidenced skills (only mention skills that have real evidence)
    real_skills = []
    for s in skills:
        name = s.get("name", "")
        dur = s.get("duration_months", 0) or 0
        end = s.get("endorsements", 0) or 0
        prof = s.get("proficiency", "")
        # Only mention if there's real evidence
        if (dur >= 6 or end >= 5) and prof in ("advanced", "expert"):
            real_skills.append(name)

    # Get most relevant career role (highest AI signal)
    from scorer.role_fit import _classify_title, CAREER_AI_COMPILED
    best_job = None
    best_job_score = 0
    for job in career_history:
        desc = job.get("description", "")
        hits = sum(1 for p in CAREER_AI_COMPILED if p.search(desc))
        tier, _ = _classify_title(job.get("title", ""))
        job_score = hits + (10 if tier == "tier1" else 0)
        if job_score > best_job_score:
            best_job_score = job_score
            best_job = job

    # Signals
    rrr = signals.get("recruiter_response_rate")
    notice = signals.get("notice_period_days")
    open_work = signals.get("open_to_work_flag", False)
    last_active = signals.get("last_active_date", "")
    github = signals.get("github_activity_score", -1)

    # ── Tier-appropriate tone ────────────────────────────────────────────────
    parts = []

    if rank <= 10:
        # Top 10: specific, enthusiastic, detailed
        parts.append(f"{title} with {yoe:.1f}yrs total experience")
        if company:
            parts.append(f"currently at {company}")
        if real_skills:
            parts.append("strong evidenced skills: " + ", ".join(real_skills[:3]))
        if best_job and best_job_score > 5:
            job_title = best_job.get("title", "")
            job_co = best_job.get("company", "")
            parts.append(f"relevant role as {job_title} at {job_co}")
        if github > 30:
            parts.append(f"active GitHub contributor (score {github:.0f})")
        if rrr is not None and rrr >= 0.6:
            parts.append(f"responsive ({rrr:.0%} response rate)")
        if notice is not None and notice <= 30:
            parts.append(f"available quickly (notice {notice}d)")

    elif rank <= 30:
        # Top 30: positive with caveats noted
        parts.append(f"{title} ({yoe:.1f}yr)")
        if real_skills:
            parts.append("key skills: " + ", ".join(real_skills[:2]))
        if best_job and best_job_score > 3:
            parts.append(f"relevant background at {best_job.get('company', '')}")
        if rrr is not None and rrr < 0.4:
            parts.append(f"lower response rate ({rrr:.0%}) is a concern")
        if notice is not None and notice > 60:
            parts.append(f"notice period {notice}d (above preferred range)")

    elif rank <= 60:
        # Mid-tier: neutral with specific strengths and concerns
        parts.append(f"{title} ({yoe:.1f}yr)")
        strengths = []
        concerns = []

        if scores.get("role_fit", 0) < 0.5:
            concerns.append("title-role gap")
        if real_skills:
            strengths.append(", ".join(real_skills[:2]))
        if rrr is not None and rrr < 0.3:
            concerns.append(f"low response rate ({rrr:.0%})")
        if not open_work:
            concerns.append("not marked open-to-work")

        if strengths:
            parts.append("strengths: " + "; ".join(strengths))
        if concerns:
            parts.append("concerns: " + "; ".join(concerns))

    else:
        # Bottom 40: honest about why they rank low
        parts.append(f"{title} ({yoe:.1f}yr) — ranked low")
        reasons = []

        if scores.get("role_fit", 0) < 0.3:
            reasons.append(f"title mismatch ('{title}' is not an AI/ML engineering role)")
        if scores.get("technical_depth", 0) < 0.3:
            reasons.append("limited evidenced technical skills for this JD")
        if scores.get("behavioral", 0) < 0.4:
            if rrr is not None:
                reasons.append(f"low availability signals (response rate {rrr:.0%})")
            if last_active:
                reasons.append(f"inactive since {last_active[:10]}")
        if not reasons:
            reasons.append("adjacent profile but below threshold for top 60")

        parts.append("; ".join(reasons))

    return " | ".join(p for p in parts if p)


# ─── Main scoring function ────────────────────────────────────────────────────

def score_candidate(candidate: dict[str, Any]) -> tuple[float, dict[str, float]]:
    """
    Compute the composite ranking score for one candidate.
    Returns (total_score: float, component_scores: dict)
    """
    role_fit_score, _ = score_role_fit(candidate)
    tech_score, _ = score_technical_depth(candidate)
    career_score, _ = score_career_substance(candidate)
    behavioral_score, _ = score_behavioral(candidate)
    edu_score = score_education(candidate)

    component_scores = {
        "role_fit": role_fit_score,
        "technical_depth": tech_score,
        "career_substance": career_score,
        "behavioral": behavioral_score,
        "education": edu_score,
    }

    # Weighted sum
    total = sum(WEIGHTS[k] * v for k, v in component_scores.items())

    # ── Behavioral as partial multiplier ──────────────────────────────────
    # Per spec: behavioral signals should be a MODIFIER on top of skill scoring.
    # Apply as: total = base * (0.85 + 0.15 * behavioral) to ensure a
    # completely unavailable candidate can't outrank a slightly-less-skilled
    # available one.
    behavioral_multiplier = 0.80 + 0.20 * behavioral_score
    total = total * behavioral_multiplier

    # ── Role fit hard gate ────────────────────────────────────────────────
    # Per JD: wrong title → cannot score above a hard ceiling.
    # A disqualified title candidate (HR Manager, etc.) caps at 0.25 total.
    if role_fit_score <= 0.15:  # disqualified title
        total = min(total, 0.28)
    elif role_fit_score <= 0.35:  # very weak fit
        total = min(total, 0.50)

    return min(1.0, max(0.0, total)), component_scores


# ─── I/O helpers ─────────────────────────────────────────────────────────────

def load_candidates(path: Path, fmt: str) -> list[dict]:
    """Load candidates from JSONL or JSON file."""
    candidates = []
    if fmt == "jsonl":
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    candidates.append(json.loads(line))
    else:  # json array
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            candidates = data
        else:
            candidates = [data]
    return candidates


def write_submission(
    results: list[dict],
    out_path: Path,
) -> None:
    """Write the submission CSV in the exact required format."""
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for row in results:
            writer.writerow([
                row["candidate_id"],
                row["rank"],
                f"{row['score']:.4f}",
                row["reasoning"],
            ])


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Redrob Intelligent Candidate Ranking — produce submission CSV"
    )
    parser.add_argument(
        "--candidates",
        required=True,
        help="Path to candidates.jsonl (or sample_candidates.json with --format json)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output path for submission CSV (e.g. ./submission.csv)",
    )
    parser.add_argument(
        "--format",
        choices=["jsonl", "json"],
        default="jsonl",
        help="Input file format (default: jsonl for the full 100K pool)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=100,
        help="Number of top candidates to include in submission (default: 100)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress and top-20 summary after ranking",
    )
    args = parser.parse_args()

    in_path = Path(args.candidates)
    out_path = Path(args.out)

    if not in_path.exists():
        print(f"ERROR: Candidates file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading candidates from {in_path}...")
    t0 = time.time()
    candidates = load_candidates(in_path, args.format)
    t_load = time.time() - t0
    print(f"  Loaded {len(candidates):,} candidates in {t_load:.1f}s")

    # ── Score all candidates ─────────────────────────────────────────────────
    print("Scoring candidates...")
    t1 = time.time()
    scored = []

    batch_size = 10000
    for i, cand in enumerate(candidates):
        if i > 0 and i % batch_size == 0:
            elapsed = time.time() - t1
            rate = i / elapsed
            eta = (len(candidates) - i) / rate
            print(f"  {i:,}/{len(candidates):,} scored ({rate:.0f}/s, ETA {eta:.0f}s)...")

        total_score, component_scores = score_candidate(cand)
        scored.append({
            "candidate_id": cand["candidate_id"],
            "total_score": total_score,
            "components": component_scores,
            "candidate": cand,
        })

    t_score = time.time() - t1
    print(f"  Scored {len(scored):,} candidates in {t_score:.1f}s ({len(scored)/t_score:.0f}/s)")

    # ── Sort: descending score (4dp rounded), then ascending candidate_id as tie-break ─────
    # IMPORTANT: the validator compares PRINTED scores (4dp) for monotonicity + tie-breaking.
    # Sort by the rounded value so tie-breaks are consistent with what's written to CSV.
    for item in scored:
        item["score_4dp"] = round(item["total_score"], 4)

    scored.sort(key=lambda x: (-x["score_4dp"], x["candidate_id"]))

    # ── Take top N ────────────────────────────────────────────────────────────
    top_n = scored[:args.top]

    # ── Generate submission rows ──────────────────────────────────────────────
    print("Generating submission rows...")
    results = []
    for rank_idx, item in enumerate(top_n, start=1):
        cand = item["candidate"]
        score = item["score_4dp"]  # Use the rounded score used for sorting
        components = item["components"]

        reasoning = _generate_reasoning(cand, components, score, rank_idx)

        results.append({
            "candidate_id": item["candidate_id"],
            "rank": rank_idx,
            "score": score,
            "reasoning": reasoning,
        })

    # ── Validate monotone scores ──────────────────────────────────────────────
    # Score must be non-increasing. If we get ties, the tie-break sort handles it.
    for i in range(len(results) - 1):
        assert results[i]["score"] >= results[i + 1]["score"], (
            f"Score monotonicity violated at rank {i+1}: "
            f"{results[i]['score']} < {results[i+1]['score']}"
        )

    # ── Write output ──────────────────────────────────────────────────────────
    write_submission(results, out_path)
    t_total = time.time() - t0
    print(f"\nDone! Wrote {len(results)} rows to {out_path}")
    print(f"Total runtime: {t_total:.1f}s")

    # ── Verbose summary ───────────────────────────────────────────────────────
    if args.verbose or True:  # Always show top-20 for sanity check
        print("\n=== Top 20 candidates (sanity check) ===")
        print(f"{'Rank':>4}  {'Score':>6}  {'Title':<35}  {'RFit':>5}  {'Tech':>5}  {'Career':>6}  {'Behav':>5}")
        print("-" * 85)
        for r in results[:20]:
            cand = next(x for x in top_n if x["candidate_id"] == r["candidate_id"])
            c = cand["components"]
            title = cand["candidate"]["profile"].get("current_title", "?")[:34]
            print(
                f"{r['rank']:>4}  {r['score']:>6.4f}  {title:<35}  "
                f"{c['role_fit']:>5.2f}  {c['technical_depth']:>5.2f}  "
                f"{c['career_substance']:>6.2f}  {c['behavioral']:>5.2f}"
            )

        print("\n=== Bottom 5 (rank 96-100) ===")
        for r in results[-5:]:
            cand = next(x for x in top_n if x["candidate_id"] == r["candidate_id"])
            c = cand["components"]
            title = cand["candidate"]["profile"].get("current_title", "?")[:34]
            print(
                f"{r['rank']:>4}  {r['score']:>6.4f}  {title:<35}  "
                f"RF={c['role_fit']:.2f} TD={c['technical_depth']:.2f} "
                f"CS={c['career_substance']:.2f} BH={c['behavioral']:.2f}"
            )

        print("\n=== Score distribution ===")
        scores = [r["score"] for r in results]
        print(f"  Rank 1:   {scores[0]:.4f}")
        print(f"  Rank 10:  {scores[9]:.4f}")
        print(f"  Rank 50:  {scores[49]:.4f}")
        print(f"  Rank 100: {scores[99]:.4f}")
        unique_scores = len(set(f"{s:.4f}" for s in scores))
        print(f"  Unique scores (4dp): {unique_scores}/100")

        # Title distribution analysis
        from collections import Counter
        top_titles = [
            x["candidate"]["profile"].get("current_title", "?")
            for x in top_n[:20]
        ]
        title_counts = Counter(top_titles)
        print("\n=== Title distribution in top 20 ===")
        for t, n in title_counts.most_common(10):
            print(f"  {n:3d}x  {t}")


if __name__ == "__main__":
    main()
