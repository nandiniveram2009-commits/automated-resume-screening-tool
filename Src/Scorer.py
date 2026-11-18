from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_tfidf_similarities(cleaned_jd: str, cleaned_resumes: List[str]) -> List[float]:
    """
    Compute cosine similarity between the Job Description and each Resume
    using TF-IDF (unigrams + bigrams).
    """
    if not cleaned_resumes:
        return []

    corpus = [cleaned_jd] + cleaned_resumes
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=3000)
    tfidf_matrix = vectorizer.fit_transform(corpus)

    jd_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(jd_vector, resume_vectors).flatten()
    return [round(float(score) * 100, 2) for score in similarities]


def calculate_final_score(
    tfidf_score: float,
    profile: Dict,
    min_experience_years: float,
) -> Dict:
    """
    Weighted ATS Score (0 - 100):
    - 45% Must-Have Skills Match
    - 30% TF-IDF Cosine Similarity (Scaled for readability)
    - 15% Experience Fit
    - 10% Nice-to-Have Skills Match
    """
    must_pct = profile["must_have_match_pct"]
    nice_pct = profile["nice_to_have_match_pct"]
    exp_years = profile["experience_years"]

    # Scale raw TF-IDF percentage gently (raw cosine similarity on resumes typically falls in 10%-60%)
    scaled_tfidf = min(tfidf_score * 1.8, 100.0)

    if min_experience_years > 0:
        exp_score = min((exp_years / min_experience_years) * 100.0, 100.0)
    else:
        exp_score = 100.0

    final_score = (
        0.45 * must_pct
        + 0.30 * scaled_tfidf
        + 0.15 * exp_score
        + 0.10 * nice_pct
    )

    # Apply penalty if critical must-have skills are missing
    gap_count = len(profile["missing_must_have"])
    if gap_count >= 3:
        final_score *= 0.80

    final_score = round(min(max(final_score, 0.0), 100.0), 2)

    # Build human-readable recruiter explanation
    explanation_parts = [
        f"Matched {len(profile['matched_must_have'])}/{len(profile['matched_must_have']) + gap_count} must-have skills ({must_pct:.0f}%)",
        f"TF-IDF similarity: {tfidf_score:.1f}%",
        f"Experience: {exp_years} yrs (target: {min_experience_years}+ yrs)",
    ]
    if gap_count > 0:
        explanation_parts.append(f"Flagged Gaps: {', '.join(profile['missing_must_have'])}")
    else:
        explanation_parts.append("No must-have skill gaps")

    return {
        "final_score": final_score,
        "tfidf_similarity_pct": tfidf_score,
        "experience_score_pct": round(exp_score, 2),
        "explanation": " | ".join(explanation_parts),
  }
