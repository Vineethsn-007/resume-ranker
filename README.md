# Redrob Intelligent Candidate Ranking Challenge

## Quick Start

> [!IMPORTANT]
> This repository uses Git LFS for the 464MB candidate dataset. Ensure you have [Git LFS](https://git-lfs.com/) installed, then run `git lfs pull` after cloning to download `data/candidates.jsonl`.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the ranker (produces submission.csv in ~2-4 minutes on 100K candidates)
python rank.py --candidates data/candidates.jsonl --out submission.csv

# 3. Validate the output
python data/validate_submission.py submission.csv
```

## How it works

The ranker uses a **multi-stage scoring pipeline** designed to avoid the keyword-stuffer trap explicitly documented in the challenge spec:

### Scoring architecture (5 components, weighted)

| Component | Weight | What it measures |
|-----------|--------|-----------------|
| Role fit (title + career) | 35% | Title and career trajectory match for a Senior AI Engineer role |
| Technical depth | 30% | Evidence-backed skills with plausibility checks (honeypot detection) |
| Career substance | 20% | Career history descriptions for retrieval/ranking/embedding/LLM work |
| Behavioral signals | 10% | Redrob engagement, availability, and recency signals |
| Disqualifier penalties | -∞ | Hard down-weights for JD-specified anti-patterns |

### Key design decisions

1. **Title gate is load-bearing**: A candidate titled "HR Manager" or "Accountant" with 9 AI skills gets ≤0.25 role-fit score, capping their total score. ML/AI/Data Science/Search titles get 1.0.

2. **Skills are plausibility-checked**: `endorsements=0` AND `duration_months=0` AND `proficiency=expert` → flagged as honeypot. Genuine skill evidence requires at least one of: endorsements > 5, duration > 12 months, or a matching career description.

3. **Career descriptions are parsed for substance**: Keywords from actual work (embeddings, FAISS, vector search, retrieval, ranking, sentence-transformers, RAG, etc.) in job descriptions — not skills lists — are the strongest signal. A candidate who built a recommendation system without using the words "RAG" still scores well.

4. **Disqualifiers are modeled, not hardcoded**:
   - Pure consulting firm history (TCS, Infosys, Wipro, etc.) with no product company → 0.7x multiplier
   - Pure research/academic with no production → 0.6x multiplier
   - <12 months total AI experience, no pre-LLM background → 0.7x
   - Senior title, no production code evidence in 18+ months → 0.8x

5. **Behavioral signals multiply, not add**: Availability score (last_active, open_to_work, response_rate, interview_completion) acts as a 0.75–1.0x multiplier on the technical score, not an additive component. A great candidate who is inactive gets meaningfully penalized.

6. **Honeypots are naturally excluded**: The plausibility check (expert proficiency in many skills, 0 duration_months used, experience claims that exceed company age) downgrades impossible profiles without hardcoding IDs.

## Compute constraints

- Runtime: ~2-4 minutes on CPU (100K candidates)
- Peak RAM: ~4-6 GB
- Network calls during ranking: **zero** (no API calls, no external requests)
- Disk: minimal (no embedding indexes needed — pure heuristic scoring)

## Reproducing the submission

```bash
python rank.py --candidates ./data/candidates.jsonl --out ./submission.csv
```

That one command produces the complete, valid submission CSV.

## Repository structure

```
├── rank.py                    # Main ranker (run this)
├── scorer/
│   ├── __init__.py
│   ├── role_fit.py            # Title/role fit scoring
│   ├── technical_depth.py     # Skills evidence scoring
│   ├── career_substance.py    # Career description NLP scoring
│   ├── behavioral.py          # Redrob signal scoring
│   └── disqualifiers.py       # JD-specified anti-pattern penalties
├── data/
│   ├── candidates.jsonl       # 100K candidate pool (Tracked via Git LFS, ~464MB)
│   ├── validate_submission.py # Official validator
│   └── ...                    # Challenge spec docs
├── submission_metadata.yaml   # Submission metadata (fill in your team details)
├── requirements.txt           # Python dependencies
├── app.py                     # Streamlit Sandbox UI
└── README.md
```

## Local Sandbox (Fast Test)

A local Streamlit UI is provided to easily visualize and test the ranking pipeline without running the full dataset.

```bash
# Start the local sandbox
streamlit run app.py
```

The sandbox will automatically load the first 100 candidates from your `data/candidates.jsonl` file and display the ranking results, component scores, and AI-generated reasoning in an interactive table.

## Hosted Sandbox

A hosted Streamlit sandbox is available at: https://resume-ranker-v1.streamlit.app/

It accepts a ≤100 candidate JSON/JSONL sample upload, runs the ranker, and displays the ranked output with scores.
