import json
import os
from src.extractor import extract_resume_text
from src.cleaner import clean_text_for_nlp
from src.skill_extractor import analyze_candidate_profile
from src.scorer import compute_tfidf_similarities, calculate_final_score
from src.ranker import assign_decision, rank_and_export


RESUME_DIR = "resumes"
JD_PATH = "data/job_description.txt"
CONFIG_PATH = "data/skills_config.json"


def run_screening_pipeline(
    resume_dir: str = RESUME_DIR,
    jd_path: str = JD_PATH,
    config_path: str = CONFIG_PATH,
):
    print("=" * 70)
    print("        AUTOMATED RESUME SCREENING TOOL (NLP + ML PIPELINE)")
    print("=" * 70)

    # 1. Load Job Description & Skill Config
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    must_have = config.get("must_have_skills", [])
    nice_to_have = config.get("nice_to_have_skills", [])
    min_exp = config.get("min_experience_years", 0.0)
    shortlist_thresh = config.get("shortlist_threshold", 70.0)
    review_thresh = config.get("review_threshold", 50.0)

    print(f"\nTarget Role      : {config.get('job_title')}")
    print(f"Must-Have Skills : {', '.join(must_have)}")
    print(f"Min Experience   : {min_exp} years\n")

    # 2. Discover and extract resumes
    supported_exts = {".pdf", ".docx", ".txt"}
    files = sorted(
        f for f in os.listdir(resume_dir)
        if os.path.splitext(f)[1].lower() in supported_exts
    )

    if not files:
        print(f"[WARNING] No resumes found in '{resume_dir}/'. Run src/generate_samples.py first.")
        return None

    extracted_items = []
    for filename in files:
        path = os.path.join(resume_dir, filename)
        raw_text = extract_resume_text(path)
        if not raw_text:
            print(f"[SKIPPED] Could not extract text from {filename}")
            continue
        extracted_items.append({
            "filename": filename,
            "raw_text": raw_text,
            "cleaned_text": clean_text_for_nlp(raw_text),
        })

    # 3. Compute TF-IDF Cosine Similarity in batch
    cleaned_jd = clean_text_for_nlp(jd_text)
    cleaned_resumes = [item["cleaned_text"] for item in extracted_items]
    tfidf_scores = compute_tfidf_similarities(cleaned_jd, cleaned_resumes)

    # 4. Analyze skills, compute hybrid score, and decide status
    records = []
    for item, tfidf_score in zip(extracted_items, tfidf_scores):
        profile = analyze_candidate_profile(
            filename=item["filename"],
            raw_text=item["raw_text"],
            must_have_skills=must_have,
            nice_to_have_skills=nice_to_have,
        )
        score_data = calculate_final_score(
            tfidf_score=tfidf_score,
            profile=profile,
            min_experience_years=min_exp,
        )
        decision = assign_decision(
            final_score=score_data["final_score"],
            missing_must_count=len(profile["missing_must_have"]),
            shortlist_threshold=shortlist_thresh,
            review_threshold=review_thresh,
        )

        records.append({
            "candidate_name": profile["candidate_name"],
            "file_name": item["filename"],
            "final_score": score_data["final_score"],
            "decision": decision,
            "must_have_match_pct": profile["must_have_match_pct"],
            "tfidf_similarity_pct": score_data["tfidf_similarity_pct"],
            "experience_years": profile["experience_years"],
            "education": profile["education"],
            "matched_must_have": ", ".join(profile["matched_must_have"]) or "None",
            "missing_must_have_gaps": ", ".join(profile["missing_must_have"]) or "None",
            "matched_nice_to_have": ", ".join(profile["matched_nice_to_have"]) or "None",
            "explanation": score_data["explanation"],
        })

    # 5. Rank & Export Reports
    df = rank_and_export(records)

    print("SCREENING SUMMARY:")
    print("-" * 70)
    display_cols = ["rank", "candidate_name", "final_score", "decision", "missing_must_have_gaps"]
    print(df[display_cols].to_string(index=False))
    print("-" * 70)
    print("\n[SUCCESS] Report saved to 'outputs/screening_report.csv'")
    print("[SUCCESS] JSON saved to   'outputs/screening_results.json'")
    return df


if __name__ == "__main__":
    run_screening_pipeline()
