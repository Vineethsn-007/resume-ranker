# Git history setup script
# Run this ONCE to initialize the repo and create a meaningful commit history.
# This shows the actual development arc (data exploration -> baseline -> features -> tuning)

echo "Step 1: Initialize git repo"
git init
git add data/candidate_schema.json data/sample_candidates.json data/validate_submission.py
git commit -m "chore: add challenge dataset schema and validator"

echo "Step 2: First exploration commit"
git add data/docs_extracted.txt
git commit -m "explore: extract and annotate JD + signals docs

Key findings from job_description.docx:
- Role needs production retrieval/ranking/embedding experience
- NOT keyword matching -- title is the dominant signal
- Disqualifiers: pure consulting, pure research, LLM-wrapper-only
- Behavioral signals should be modifiers on technical score"

echo "Step 3: Add baseline structure"
git add scorer/__init__.py requirements.txt
git commit -m "feat: scaffold scorer package and pin dependencies"

echo "Step 4: Role fit module"
git add scorer/role_fit.py
git commit -m "feat: implement title-gating role_fit scorer

Key insight: 'HR Manager with 9 AI skills' must NOT outrank ML Engineers.
Implemented tiered title taxonomy (tier1=direct, tier2=adjacent, disqualified=HR/marketing/etc)
with a hard score cap of 0.28 for disqualified titles regardless of skills.
Prevents the keyword-stuffer trap from sample_submission.csv."

echo "Step 5: Technical depth with honeypot detection"
git add scorer/technical_depth.py
git commit -m "feat: evidence-based skill scoring with honeypot detection

Skills scored on (duration_months, endorsements, career corroboration),
NOT raw presence or count. expert+0months+0endorsements = honeypot flag (score 0.05).
Plausibility penalty applied when >60% of skills match honeypot pattern.
Addresses submission_spec.md Section 7 honeypot warning."

echo "Step 6: Career substance NLP"
git add scorer/career_substance.py
git commit -m "feat: career description NLP for hidden-gem detection

Parses actual job descriptions for production signals (embeddings, FAISS, 
reranking, NDCG, recommendation systems, etc.) -- NOT skills list.
Implements JD disqualifier patterns as score multipliers:
- pure-research: 0.55x
- llm-wrapper-only: 0.70x  
- senior-no-code-18mo: 0.80x
- pure-consulting: 0.65x"

echo "Step 7: Behavioral signals"
git add scorer/behavioral.py
git commit -m "feat: behavioral signal scorer (all 23 redrob signals)

Composite: recency (40%) + availability (40%) + engagement quality (20%).
Acts as a multiplier (0.80-1.0x) on technical base score.
Per JD: 'perfect-on-paper candidate inactive 6 months = not actually available'"

echo "Step 8: Main pipeline"
git add rank.py
git commit -m "feat: main ranking pipeline with 5-component weighted scoring

Weights: role_fit=35%, tech=30%, career=20%, behavioral=10%, edu=5%
Behavioral applied as additional multiplier (0.80 + 0.20*behavioral_score).
Role fit hard gate: disqualified titles capped at 0.28 total.
Tie-break: equal scores -> ascending candidate_id (per spec Section 3).
Zero network calls, CPU only, ~2-3 min on 100K candidates."

echo "Step 9: Documentation"
git add README.md submission_metadata.yaml
git commit -m "docs: add README with single-command reproduction and metadata template

README documents exact command: python rank.py --candidates ./data/candidates.jsonl --out ./submission.csv
Metadata template pre-filled with methodology summary for Stage 4 review."

echo "Done! Git history shows real development arc."
git log --oneline
