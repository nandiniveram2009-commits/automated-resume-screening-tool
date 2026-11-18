import json
import os
import tempfile
from typing import List
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.extractor import extract_resume_text
from src.cleaner import clean_text_for_nlp
from src.skill_extractor import analyze_candidate_profile
from src.scorer import compute_tfidf_similarities, calculate_final_score
from src.ranker import assign_decision, rank_and_export

app = FastAPI(title="Automated Resume Screening API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/results")
def get_latest_results():
    """Return the latest screened candidate rankings for a Next.js dashboard."""
    results_path = "outputs/screening_results.json"
    if not os.path.exists(results_path):
        return {"candidates": [], "message": "Run main.py first to generate results."}
    with open(results_path, "r", encoding="utf-8") as f:
        return {"candidates": json.load(f)}


@app.post("/screen")
async def screen_uploaded_resumes(
    job_description: str = Form(...),
    must_have_skills: str = Form("python,sql,pandas,scikit-learn,nlp"),
    nice_to_have_skills: str = Form("fastapi,docker,git"),
    min_experience_years: float = Form(2.0),
    files: List[UploadFile] = File(...),
):
    must_have = [s.strip().lower() for s in must_have_skills.split(",") if s.strip()]
    nice_to_have = [s.strip().lower() for s in nice_to_have_skills.split(",") if s.strip()]

    extracted = []
    for file in files:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        raw_text = extract_resume_text(tmp_path)
        os.remove(tmp_path)
        if raw_text:
            extracted.append({
                "filename": file.filename,
                "raw_text": raw_text,
                "cleaned": clean_text_for_nlp(raw_text),
            })

    tfidf_scores = compute_tfidf_similarities(clean_text_for_nlp(job_description), [x["cleaned"] for x in extracted])
    records = []
    for item, tfidf_score in zip(extracted, tfidf_scores):
        profile = analyze_candidate_profile(item["filename"], item["raw_text"], must_have, nice_to_have)
        score_data = calculate_final_score(tfidf_score, profile, min_experience_years)
        decision = assign_decision(score_data["final_score"], len(profile["missing_must_have"]), 70.0, 50.0)
        records.append({
            "candidate_name": profile["candidate_name"],
            "file_name": item["filename"],
            "final_score": score_data["final_score"],
            "decision": decision,
            "must_have_match_pct": profile["must_have_match_pct"],
            "tfidf_similarity_pct": score_data["tfidf_similarity_pct"],
            "experience_years": profile["experience_years"],
            "missing_must_have_gaps": profile["missing_must_have"],
            "explanation": score_data["explanation"],
        })

    df = rank_and_export(records)
    return {"total": len(df), "candidates": df.to_dict(orient="records")}
