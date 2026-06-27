import streamlit as st
import json
import pandas as pd
from rank import score_candidate, _generate_reasoning

st.set_page_config(page_title="Resume Ranker Sandbox", layout="wide")

st.title("Redrob Candidate Ranker Sandbox")
st.markdown("Upload a JSON/JSONL sample (≤ 100 candidates) to see the ranking pipeline in action, or run the default sample.")

uploaded_file = st.file_uploader("Upload Candidates (JSON or JSONL)", type=["json", "jsonl"])

candidates = []

if uploaded_file is not None:
    # Read the file
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if uploaded_file.name.endswith(".jsonl"):
        for line in file_contents.splitlines():
            if line.strip():
                candidates.append(json.loads(line))
    else:
        data = json.loads(file_contents)
        if isinstance(data, list):
            candidates = data
        else:
            candidates = [data]
    
    if len(candidates) > 100:
        st.warning(f"File contains {len(candidates)} candidates. Truncating to 100 for the sandbox.")
        candidates = candidates[:100]

elif st.button("Load Default Sample (data/candidates.jsonl - first 100)"):
    try:
        candidates = []
        with open("data/candidates.jsonl", "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if line.strip():
                    candidates.append(json.loads(line))
                if len(candidates) >= 100:
                    break
    except FileNotFoundError:
        st.error("Default sample file not found. Please upload a file instead.")

if candidates:
    st.write(f"Loaded **{len(candidates)}** candidates.")
    
    with st.spinner("Scoring candidates..."):
        scored = []
        for cand in candidates:
            total_score, component_scores = score_candidate(cand)
            scored.append({
                "candidate_id": cand.get("candidate_id", "Unknown"),
                "total_score": total_score,
                "components": component_scores,
                "candidate": cand
            })
            
        # Sort
        for item in scored:
            item["score_4dp"] = round(item["total_score"], 4)
        scored.sort(key=lambda x: (-x["score_4dp"], x["candidate_id"]))
        
        # Prepare results
        results = []
        for rank_idx, item in enumerate(scored, start=1):
            cand = item["candidate"]
            score = item["score_4dp"]
            components = item["components"]
            reasoning = _generate_reasoning(cand, components, score, rank_idx)
            title = cand.get("profile", {}).get("current_title", "Unknown")
            
            results.append({
                "Rank": rank_idx,
                "Candidate ID": item["candidate_id"],
                "Score": f"{score:.4f}",
                "Title": title,
                "Role Fit": f"{components['role_fit']:.2f}",
                "Tech Depth": f"{components['technical_depth']:.2f}",
                "Career": f"{components['career_substance']:.2f}",
                "Behavioral": f"{components['behavioral']:.2f}",
                "Education": f"{components['education']:.2f}",
                "Reasoning": reasoning
            })
            
        df = pd.DataFrame(results)
        
        st.success("Ranking complete!")
        st.dataframe(df, use_container_width=True, hide_index=True)
