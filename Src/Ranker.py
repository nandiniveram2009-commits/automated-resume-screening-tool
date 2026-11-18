import json
import os
from typing import Dict, List
import pandas as pd


def assign_decision(
    final_score: float,
    missing_must_count: int,
    shortlist_threshold: float,
    review_threshold: float,
) -> str:
    """Determine screening status based on score and must-have gaps."""
    if final_score >= shortlist_threshold and missing_must_count == 0:
        return "Shortlisted"
    if final_score >= shortlist_threshold and missing_must_count <= 1:
        return "Shortlisted (With Minor Gap)"
    if final_score >= review_threshold:
        return "Needs Review"
    return "Rejected"


def rank_and_export(
    records: List[Dict],
    output_csv: str = "outputs/screening_report.csv",
    output_json: str = "outputs/screening_results.json",
) -> pd.DataFrame:
    """Sort candidates by final score descending and export CSV + JSON."""
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = df.sort_values(by=["final_score", "must_have_match_pct"], ascending=[False, False])
    df.insert(0, "rank", range(1, len(df) + 1))

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

    return df
