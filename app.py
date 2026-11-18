import os
import json
import tempfile
import streamlit as st
import pandas as pd

from src.extractor import extract_resume_text
from src.cleaner import clean_text_for_nlp
from src.skill_extractor import analyze_candidate_profile
from src.scorer import compute_tfidf_similarities, calculate_final_score
from src.ranker import assign_decision


st.set_page_config(page_title="Automated Resume Screener", page_icon="📄", layout="wide")
st.title("📄 Automated Resume Screening Tool (NLP & ATS)")
st.markdown("Screen resumes against any job description, rank candidates, and flag must-have skill gaps.")

# Load defaults
with open("data/job_description.txt", "r", encoding="utf-8") as f:
    default_jd = f.read()
with open("data/skills_config.json", "r", encoding="utf-8") as f:
    default_cfg = json.load(f)

with st.sidebar:
    st.header("⚙️ Screening Criteria")
    must_have_input = st.text_input(
        "Must-Have Skills (comma-separated)",
        value=", ".join(default_cfg["must_have_skills"]),
    )
    nice_to_have_input = st.text_input(
        "Nice-to-Have Skills (comma-separated)",
        value=", ".join(default_cfg["nice_to_have_skills"]),
    )
    min_exp = st.number_input("Minimum Experience (Years)", min_value=0.0, max_value=20.0, value=2.0, step=0.5)
    shortlist_thresh = st.slider("Shortlist Threshold Score", 40, 95, 70)
    review_thresh = st.slider("Review Threshold Score", 20, 75, 50)

jd_text = st.text_area("📌 Job Description", value=default_jd, height=200)

uploaded_files = st.file_uploader(
    "📤 Upload Resumes (PDF, DOCX, TXT) — leave empty to screen `/resumes` folder",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)

if st.button("🚀 Run Resume Screening", type="primary"):
    must_have = [s.strip().lower() for s in must_have_input.split(",") if s.strip()]
    nice_to_have = [s.strip().lower() for s in nice_to_have_input.split(",") if s.strip()]

    items = []
    if uploaded_files:
        for uf in uploaded_files:
            suffix = os.path.splitext(uf.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uf.read())
                tmp_path = tmp.name
            raw = extract_resume_text(tmp_path)
            os.remove(tmp_path)
            if raw:
                items.append({"filename": uf.name, "raw_text": raw, "cleaned": clean_text_for_nlp(raw)})
    else:
        for fname in sorted(os.listdir("resumes")):
            if os.path.splitext(fname)[1].lower() in {".pdf", ".docx", ".txt"}:
                raw = extract_resume_text(os.path.join("resumes", fname))
                if raw:
                    items.append({"filename": fname, "raw_text": raw, "cleaned": clean_text_for_nlp(raw)})

    if not items:
        st.error("No readable resumes found!")
    else:
        tfidf_scores = compute_tfidf_similarities(clean_text_for_nlp(jd_text), [i["cleaned"] for i in items])
        rows = []
        for item, tfidf_score in zip(items, tfidf_scores):
            profile = analyze_candidate_profile(item["filename"], item["raw_text"], must_have, nice_to_have)
            score_data = calculate_final_score(tfidf_score, profile, min_exp)
            decision = assign_decision(
                score_data["final_score"],
                len(profile["missing_must_have"]),
                shortlist_thresh,
                review_thresh,
            )
            rows.append({
                "Candidate": profile["candidate_name"],
                "File": item["filename"],
                "Score": score_data["final_score"],
                "Decision": decision,
                "Must-Have %": profile["must_have_match_pct"],
                "TF-IDF %": score_data["tfidf_similarity_pct"],
                "Exp (Yrs)": profile["experience_years"],
                "Missing Must-Haves": ", ".join(profile["missing_must_have"]) or "None",
                "Explanation": score_data["explanation"],
            })

        df = pd.DataFrame(rows).sort_values(by="Score", ascending=False).reset_index(drop=True)
        df.insert(0, "Rank", range(1, len(df) + 1))

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Resumes", len(df))
        col2.metric("Shortlisted", int(df["Decision"].str.startswith("Shortlisted").sum()))
        col3.metric("Top Score", f"{df['Score'].max():.1f}/100")

        st.subheader("🏆 Ranked Candidates")
        st.dataframe(df, use_container_width=True)

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV Report", data=csv_bytes, file_name="screening_report.csv", mime="text/csv")
