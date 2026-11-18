import re
from typing import Dict, List


EDUCATION_KEYWORDS = [
    "ph.d", "phd", "master", "m.tech", "m.sc", "mca", "mba",
    "bachelor", "b.tech", "b.e.", "b.sc", "bca"
]


def _skill_present(skill: str, text_lower: str) -> bool:
    """
    Check exact skill presence using safe word boundaries.
    Handles symbols like C++, C#, Node.js, Next.js, Scikit-learn accurately.
    """
    pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
    return re.search(pattern, text_lower) is not None


def extract_experience_years(text: str) -> float:
    """Extract maximum mentioned years of experience from resume text."""
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:hands-on\s+)?experience",
        r"experience\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b",
    ]
    found_years = []
    text_lower = text.lower()
    for pat in patterns:
        matches = re.findall(pat, text_lower)
        for m in matches:
            try:
                val = float(m)
                if 0 < val <= 40:
                    found_years.append(val)
            except ValueError:
                continue
    return max(found_years) if found_years else 0.0


def extract_education(text: str) -> str:
    """Identify highest/first detected degree keyword."""
    text_lower = text.lower()
    detected = [deg.upper() for deg in EDUCATION_KEYWORDS if _skill_present(deg, text_lower)]
    return ", ".join(dict.fromkeys(detected)) if detected else "Not Specified"


def extract_candidate_name(filename: str, text: str) -> str:
    """Infer candidate name from first non-empty line or filename."""
    for line in text.splitlines():
        clean_line = line.strip()
        if clean_line and "@" not in clean_line and len(clean_line.split()) <= 5:
            return clean_line
    base = filename.rsplit(".", 1)[0]
    return base.replace("_", " ")


def analyze_candidate_profile(
    filename: str,
    raw_text: str,
    must_have_skills: List[str],
    nice_to_have_skills: List[str],
) -> Dict:
    """Extract structured skills, must-have gaps, experience, and education."""
    text_lower = raw_text.lower()

    matched_must = [s for s in must_have_skills if _skill_present(s, text_lower)]
    missing_must = [s for s in must_have_skills if s not in matched_must]
    matched_nice = [s for s in nice_to_have_skills if _skill_present(s, text_lower)]

    must_ratio = (len(matched_must) / len(must_have_skills)) if must_have_skills else 1.0
    nice_ratio = (len(matched_nice) / len(nice_to_have_skills)) if nice_to_have_skills else 0.0

    experience_years = extract_experience_years(raw_text)
    education = extract_education(raw_text)
    candidate_name = extract_candidate_name(filename, raw_text)

    return {
        "candidate_name": candidate_name,
        "matched_must_have": matched_must,
        "missing_must_have": missing_must,
        "matched_nice_to_have": matched_nice,
        "must_have_match_pct": round(must_ratio * 100, 2),
        "nice_to_have_match_pct": round(nice_ratio * 100, 2),
        "experience_years": experience_years,
        "education": education,
    }
