# automated-resume-screening-tool
NLP &amp; ML-powered Automated Resume Screening Tool that extracts skills/experience from PDF/DOCX resumes, computes TF-IDF similarity, flags must-have gaps, ranks candidates, and serves results via Streamlit &amp; FastAPI.
# 📄 Automated Resume Screening Tool (NLP & ATS Engine)

An end-to-end **Machine Learning & NLP Resume Screening System** that parses candidate resumes (PDF, DOCX, TXT), extracts skills, experience, and education, computes **TF-IDF Cosine Similarity** against a target Job Description, flags **must-have skill gaps**, ranks candidates with human-readable explanations, and exports reports via **CSV, JSON, Streamlit, and FastAPI**.

---

## 🎯 Problem Statement
Recruiters often receive hundreds of applications per role, making manual resume screening slow, inconsistent, and error-prone. Standard keyword-only filters either reject strong candidates due to formatting differences or blindly pass buzzword-stuffed resumes without checking critical skill gaps.

## 💡 Industry Relevance
This project mirrors real-world **Applicant Tracking Systems (ATS)** and **HR Tech Screening Engines** by combining:
- **Unstructured NLP Matching** (TF-IDF + Cosine Similarity)
- **Structured Rule & Gap Analysis** (Must-Have vs. Nice-to-Have skills, Years of Experience)
- **Explainable Decisions** (Clear justification for every Shortlist, Review, or Reject tag)

---

## ✨ Key Features
- **Multi-Format Parsing:** Extracts text reliably from `.pdf` (`pdfplumber` + `PyPDF2` fallback), `.docx` (`python-docx`), and `.txt`.
- **Boundary-Safe Skill Extraction:** Accurately matches skills like `Python`, `SQL`, `C++`, `Next.js`, and `Scikit-learn` without substring false positives.
- **Must-Have Gap Flagging:** Explicitly identifies which critical skills a candidate is missing.
- **Experience & Education Parsing:** Extracts years of experience and degree keywords using regex.
- **Hybrid Scoring Engine:** Combines Must-Have Skill Match (45%), TF-IDF Cosine Similarity (30%), Experience Fit (15%), and Nice-to-Have Skills (10%).
- **Automated Reporting & UI:** Generates `screening_report.csv`, `screening_results.json`, an interactive **Streamlit** dashboard, and **FastAPI** endpoints ready for a Next.js frontend.

---

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **NLP & ML:** `scikit-learn` (TF-IDF Vectorizer, Cosine Similarity), Regex
- **Data Processing:** `pandas`, `numpy`
- **Document Parsing:** `pdfplumber`, `PyPDF2`, `python-docx`, `fpdf2`
- **Dashboard & API:** `Streamlit`, `FastAPI`, `Uvicorn`

---

## 📂 Folder Structure
```text
Automated-Resume-Screening-Tool/
├── resumes/              # Sample and input resumes (.pdf, .docx, .txt)
├── data/                 # Job description and skills_config.json
├── src/                  # Modular extraction, cleaning, scoring & ranking code
├── outputs/              # Generated CSV and JSON screening reports
├── images/               # Screenshots of terminal, CSV, and dashboard
├── main.py               # CLI pipeline runner
├── app.py                # Streamlit interactive recruiter UI
├── api.py                # FastAPI REST endpoints
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
