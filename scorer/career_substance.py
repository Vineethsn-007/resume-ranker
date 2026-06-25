"""
career_substance.py — Career description NLP scoring.

This is the module that catches "Tier 5" candidates the JD describes:
"A Tier 5 candidate may not use the words 'RAG' or 'Pinecone' in their
profile, but if their career history shows they built a recommendation
system at a product company, they're a fit."

This module scores the ACTUAL WORK described in career history, not the
skills list. It rewards candidates whose descriptions demonstrate real
production experience in retrieval, ranking, and ML systems.

Also implements the disqualifier patterns:
- Pure research/academic with no production deployment
- <12 months total AI experience with no pre-LLM background
- Senior title but no production code in 18+ months
- Pure consulting career (all services, no product companies)
"""

from __future__ import annotations
import re
from datetime import date, datetime
from typing import Any


# ─── Production signal patterns ───────────────────────────────────────────────
# These appear in descriptions of real work, not just skill lists

PRODUCTION_SIGNALS = [
    # Search & retrieval
    (r"\b(built|developed|designed|implemented|deployed|shipped)\b.{0,60}\b(search|retrieval|rank|embedding)", 3.0),
    (r"\bretriev(al|ing|ed)\b", 1.5),
    (r"\bvector (search|db|database|index|store)\b", 2.0),
    (r"\bsemantic search\b", 2.0),
    (r"\bhybrid search\b", 2.0),
    (r"\bfaiss\b", 2.5),
    (r"\bpinecone\b", 2.0),
    (r"\bweaviate\b", 2.0),
    (r"\bqdrant\b", 2.0),
    (r"\bmilvus\b", 2.0),
    (r"\bopensearch\b", 1.5),
    (r"\belasticsearch\b", 1.2),
    (r"\bBM25\b", 1.5),

    # Embeddings & representations
    (r"\bsentence.transformer", 2.5),
    (r"\btext embedding[s]?\b", 2.0),
    (r"\bembedding (model|drift|index|pipeline|serv)", 2.0),
    (r"\bBGE\b", 2.0),
    (r"\bE5\b", 1.5),
    (r"\bembedding\b", 1.0),

    # Ranking systems
    (r"\b(learning.to.rank|L2R|LTR)\b", 3.0),
    (r"\brank(ing|ed|er)\b.{0,40}\b(system|model|pipeline|candidate)", 2.0),
    (r"\b(NDCG|nDCG)\b", 2.5),
    (r"\bMRR\b", 2.0),
    (r"\bMAP\b.{0,20}\b(metric|score|eval)", 1.5),
    (r"\brelevance (scoring|signal|rank|label)", 2.0),
    (r"\breranking\b", 2.5),
    (r"\bcross.encoder\b", 2.0),

    # LLMs and RAG
    (r"\bRAG\b", 2.5),
    (r"\bretrieval.augmented", 2.5),
    (r"\bfine.tun\b.{0,40}\b(LLM|GPT|BERT|model)", 2.5),
    (r"\bLoRA\b", 2.0),
    (r"\bQLoRA\b", 2.0),
    (r"\bPEFT\b", 2.0),
    (r"\bLLM (pipeline|serving|inference|integrat)", 2.0),

    # Recommendation systems
    (r"\brecommendation (system|engine|pipeline)\b", 2.5),
    (r"\bcolaborative filter", 2.0),
    (r"\bcollaborative filter", 2.0),
    (r"\bcontent.based filter", 1.5),
    (r"\bmatrix factori", 1.5),
    (r"\btwo.tower\b", 2.5),

    # Production deployment signals
    (r"\b(deployed|serving|prod(uction)?)\b.{0,50}\b(model|API|inference|pipeline)", 2.0),
    (r"\breal.time (inference|serving|rank)", 2.0),
    (r"\bA/B test\b", 1.5),
    (r"\bonline eval", 1.5),
    (r"\boffline eval", 1.0),

    # ML systems engineering
    (r"\bMLflow\b", 1.5),
    (r"\bKubeflow\b", 1.5),
    (r"\bMLOps\b", 1.5),
    (r"\bmodel monitor", 1.5),
    (r"\bfeature (store|engineer|pipeline)", 1.5),
    (r"\bpipeline (orchestrat|deploy|serve)", 1.5),

    # Core ML frameworks in production context
    (r"\b(PyTorch|TensorFlow)\b.{0,60}\b(train|deploy|product|serve|finetun)", 1.5),
    (r"\bxgboost\b.{0,40}\b(rank|score|model|train)", 1.5),
    (r"\bPyTorch\b", 0.8),
    (r"\bTensorFlow\b", 0.8),

    # Platform/scale signals
    (r"\b(billion|million|scale|latency|throughput)\b.{0,60}\b(candidate|query|vector|embed)", 2.0),
    (r"\b(latency|p50|p99|SLA)\b.{0,40}\b(ms|millisec|second)", 1.5),
]

PRODUCTION_COMPILED = [
    (re.compile(p, re.IGNORECASE), w) for p, w in PRODUCTION_SIGNALS
]

# ─── Anti-patterns from the JD ────────────────────────────────────────────────

# Pure research/academic signals
ACADEMIC_SIGNALS = [
    r"\b(paper|publication|arxiv|preprint|conference|journal|lab|thesis|dissertation)\b",
    r"\bPhD (student|candidate|research)\b",
    r"\bpostdoc\b",
    r"\bNeurIPS\b|\bICML\b|\bACL\b|\bEMNLP\b|\bIJCAI\b",
]
ACADEMIC_COMPILED = [re.compile(p, re.IGNORECASE) for p in ACADEMIC_SIGNALS]

# Production deployment counter-signals (offsets academic signals)
DEPLOYMENT_SIGNALS = [
    r"\b(deployed|shipped|production|real.user|customer|API|serving)\b",
    r"\bproduct (company|team|engineering)\b",
    r"\buser-facing\b",
    r"\bprod (env|cluster|system)\b",
]
DEPLOYMENT_COMPILED = [re.compile(p, re.IGNORECASE) for p in DEPLOYMENT_SIGNALS]

# LLM-wrapper-only warning signals (JD: <12 months of LangChain-only is a disqualifier)
LLM_WRAPPER_SIGNALS = [
    r"\bLangChain\b",
    r"\bOpenAI API\b",
    r"\bGPT-3\.5|GPT-4\b",
    r"\bChatGPT\b",
    r"\bLlamaIndex\b",
    r"\bchatbot\b",
]
LLM_WRAPPER_COMPILED = [re.compile(p, re.IGNORECASE) for p in LLM_WRAPPER_SIGNALS]

# Pre-LLM ML evidence (offsets LLM-wrapper concern)
PRE_LLM_SIGNALS = [
    r"\bXGBoost\b",
    r"\bScikit.learn\b",
    r"\bLightGBM\b",
    r"\bCatBoost\b",
    r"\bRandom Forest\b",
    r"\bSVM\b",
    r"\bfeature engineer",
    r"\bclassification (model|pipeline|system)\b",
    r"\bBERT\b",
    r"\bfine.tun.{0,30}\bBERT\b",
    r"\bElasticsearch\b",
    r"\bBM25\b",
    r"\brecommendation system\b",
    r"\b(20[01][0-9])\b",  # mentions of years 2000–2019
]
PRE_LLM_COMPILED = [re.compile(p, re.IGNORECASE) for p in PRE_LLM_SIGNALS]

# Consulting-firm identifiers
CONSULTING_FIRMS_PATTERN = re.compile(
    r"\b(TCS|Tata Consultancy|Infosys|Wipro|Accenture|Cognizant|Capgemini|"
    r"HCL|Tech Mahindra|Mphasis|Hexaware|LTIMindtree|Mindtree|"
    r"Persistent|NIIT|Mastech|Zensar|Syntel|KPIT|Cyient|Birlasoft)\b",
    re.IGNORECASE,
)


def _parse_date(date_str: str | None) -> date | None:
    """Parse ISO date string to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def _is_product_company(company: str, industry: str, company_size: str) -> bool:
    """
    Heuristic to detect if a company is a product company vs pure services.
    Product companies build something; services/consulting firms build for clients.
    """
    company_lower = company.lower()
    industry_lower = industry.lower()

    # Known consulting/services patterns
    if CONSULTING_FIRMS_PATTERN.search(company):
        return False

    services_industries = {
        "it services", "consulting", "staffing", "outsourcing",
        "bpo", "kpo", "professional services", "management consulting",
    }
    if any(s in industry_lower for s in services_industries):
        return False

    # Product company indicators
    product_industries = {
        "saas", "software", "technology", "internet", "fintech",
        "e-commerce", "edtech", "healthtech", "hr tech", "ai",
        "machine learning", "data analytics", "cloud",
        "semiconductor", "consumer electronics",
        "gaming", "media technology",
    }
    if any(p in industry_lower for p in product_industries):
        return True

    # Mid-size companies are more likely product than services
    if company_size in ("51-200", "201-500", "501-1000"):
        return True

    return True  # Default: assume product (benefit of the doubt)


def score_career_substance(candidate: dict[str, Any]) -> tuple[float, str]:
    """
    Main entry point for career substance scoring.
    Returns (score: 0.0–1.0, explanation: str)
    """
    career_history = candidate.get("career_history", []) or []
    redrob_signals = candidate.get("redrob_signals", {}) or {}
    profile = candidate.get("profile", {})
    yoe = profile.get("years_of_experience", 0) or 0

    if not career_history:
        return 0.0, "no-career-history"

    today = date.today()

    # ── Per-job scoring ──────────────────────────────────────────────────────
    total_production_score = 0.0
    total_academic_hits = 0
    total_deployment_hits = 0
    total_llm_wrapper_hits = 0
    total_pre_llm_hits = 0
    product_company_months = 0
    consulting_only_months = 0
    most_recent_code_months_ago = 999
    has_pre_llm_experience = False
    recent_ai_months = 0

    for job in career_history:
        desc = job.get("description", "")
        dur = job.get("duration_months", 0) or 0
        is_current = job.get("is_current", False)
        company = job.get("company", "")
        industry = job.get("industry", "")
        company_size = job.get("company_size", "1-10")
        title = job.get("title", "")
        start_str = job.get("start_date", "")
        end_str = job.get("end_date")

        is_product = _is_product_company(company, industry, company_size)
        if is_product:
            product_company_months += dur
        else:
            consulting_only_months += dur

        # Recency weight: last 24 months count 2x
        end_date = _parse_date(end_str) if end_str else today
        start_date = _parse_date(start_str)
        if end_date:
            months_since_end = max((today - end_date).days // 30, 0)
        else:
            months_since_end = 0
        recency_w = 2.0 if months_since_end <= 24 else 1.0

        # Production signals in descriptions
        job_prod_score = 0.0
        for pattern, weight in PRODUCTION_COMPILED:
            if pattern.search(desc):
                job_prod_score += weight * recency_w

        # Cap per-job contribution
        job_prod_score = min(job_prod_score, 30.0) * min(dur / 12.0, 2.0)
        total_production_score += job_prod_score

        # Academic signals
        acad_hits = sum(1 for p in ACADEMIC_COMPILED if p.search(desc))
        deploy_hits = sum(1 for p in DEPLOYMENT_COMPILED if p.search(desc))
        total_academic_hits += acad_hits
        total_deployment_hits += deploy_hits

        # LLM wrapper signals
        llm_wrap = sum(1 for p in LLM_WRAPPER_COMPILED if p.search(desc))
        pre_llm = sum(1 for p in PRE_LLM_COMPILED if p.search(desc))
        total_llm_wrapper_hits += llm_wrap
        total_pre_llm_hits += pre_llm

        # Pre-LLM experience: check if the start year is before 2023
        if start_date and start_date.year < 2023:
            if pre_llm > 0 or job_prod_score > 5:
                has_pre_llm_experience = True

        # Production code recency check: non-management engineering roles
        mgmt_words = ["manager", "director", "head of", "vp", "chief"]
        is_management = any(w in title.lower() for w in mgmt_words)
        if not is_management and is_current:
            most_recent_code_months_ago = 0
        elif not is_management and months_since_end < most_recent_code_months_ago:
            most_recent_code_months_ago = months_since_end

        # Recent AI months (last 12 months)
        if months_since_end <= 12 and job_prod_score > 0:
            recent_ai_months += min(dur, 12 - months_since_end)

    # ── Normalize production score ────────────────────────────────────────
    # 60+ weighted production score → near max
    base_score = min(total_production_score / 60.0, 1.0)

    # ── Penalties ─────────────────────────────────────────────────────────

    # Penalty 1: Pure research with no production deployment (JD disqualifier)
    if total_academic_hits > 3 and total_deployment_hits < 2:
        base_score *= 0.55
        research_note = "research-without-deployment"
    else:
        research_note = ""

    # Penalty 2: Recent (< 12 months) LLM-wrapper-only experience, no pre-LLM background
    # JD: "AI experience of primarily recent LangChain projects" without pre-LLM background
    if total_llm_wrapper_hits > 2 and not has_pre_llm_experience and recent_ai_months < 12:
        base_score *= 0.70
        wrapper_note = "llm-wrapper-only-no-preLLM-background"
    else:
        wrapper_note = ""

    # Penalty 3: Senior title (from profile) but no production code in 18+ months
    current_title = profile.get("current_title", "").lower()
    is_senior = any(w in current_title for w in ["senior", "staff", "principal", "lead", "head"])
    if is_senior and most_recent_code_months_ago > 18:
        base_score *= 0.80
        arch_note = "senior-no-recent-code"
    else:
        arch_note = ""

    # Penalty 4: Consulting-only career with no product company (JD: "entire career at consulting firms")
    if product_company_months == 0 and consulting_only_months > 0:
        base_score *= 0.65
        consulting_note = "pure-consulting-no-product"
    elif product_company_months > 0:
        # Boost if substantial product company experience
        product_ratio = product_company_months / max(product_company_months + consulting_only_months, 1)
        if product_ratio > 0.5:
            base_score = min(base_score * 1.1, 1.0)
        consulting_note = ""
    else:
        consulting_note = ""

    # ── Build explanation ────────────────────────────────────────────────
    notes = [n for n in [research_note, wrapper_note, arch_note, consulting_note] if n]
    product_note = f"product-company-months={product_company_months}"
    explanation = product_note
    if notes:
        explanation += "; penalties: " + ", ".join(notes)

    return max(0.0, min(1.0, base_score)), explanation
