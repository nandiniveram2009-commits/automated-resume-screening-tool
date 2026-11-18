import os
from docx import Document
from fpdf import FPDF

RESUME_DIR = "resumes"


SAMPLES = [
    {
        "filename": "01_Aarav_Sharma_Strong.pdf",
        "format": "pdf",
        "content": """Aarav Sharma
Email: aarav.sharma@email.com | Phone: +91-9876543210 | GitHub: github.com/aarav-ml
Education: B.Tech in Computer Science

Summary:
Python & NLP Engineer with 3 years of experience building automated text processing systems,
REST APIs, and machine learning pipelines.

Technical Skills:
Python, SQL, Pandas, NumPy, Scikit-learn, NLP, FastAPI, Git, Docker, Streamlit, Machine Learning

Experience:
Data & NLP Developer | TechFlow Analytics (2022 - Present)
- Built an NLP document classification and TF-IDF similarity engine using Python and Scikit-learn.
- Designed FastAPI microservices connected to PostgreSQL/SQL databases.
- Processed 50,000+ text records weekly using Pandas and NumPy.
- Containerized Python services using Docker and managed code with Git.
""",
    },
    {
        "filename": "02_Priya_Nair_Strong_Data.docx",
        "format": "docx",
        "content": """Priya Nair
Email: priya.nair@email.com | LinkedIn: linkedin.com/in/priyanair
Education: Master of Computer Applications (MCA)

Summary:
Data Analyst and Python Developer with 2.5 years of experience in predictive modeling,
NLP text mining, and dashboard automation.

Skills:
Python, Pandas, NumPy, SQL, Scikit-learn, NLP, Machine Learning, Streamlit, Git

Experience:
Junior Data Scientist | InsightBridge (2022 - Present)
- Developed NLP sentiment and keyword extraction pipelines using Python and Scikit-learn.
- Automated SQL reporting workflows with Pandas, reducing manual work by 60%.
- Built interactive recruiter and business dashboards in Streamlit.
""",
    },
    {
        "filename": "03_Rohan_Verma_Partial_Gap.pdf",
        "format": "pdf",
        "content": """Rohan Verma
Email: rohan.verma@email.com
Education: B.Sc in Information Technology

Summary:
Backend Python Developer with 2 years of experience building web APIs and database integrations.

Skills:
Python, SQL, FastAPI, Git, Docker, AWS, Pandas

Experience:
Python Backend Developer | CloudScale Systems (2023 - Present)
- Built scalable REST APIs in FastAPI and integrated PostgreSQL using SQL.
- Wrote ETL automation scripts with Pandas.
- Deployed backend applications on AWS using Docker.
""",
    },
    {
        "filename": "04_Sneha_Kulkarni_Fresher_Good.docx",
        "format": "docx",
        "content": """Sneha Kulkarni
Email: sneha.k@email.com
Education: B.Tech in Artificial Intelligence & Data Science

Summary:
Recent graduate with 1 year of internship experience in Machine Learning, NLP, and Python analytics.

Skills:
Python, Pandas, NumPy, Scikit-learn, NLP, Machine Learning, SQL, Git, Streamlit

Projects & Internship:
ML Intern | DataSpark Labs (1 year of experience)
- Built a resume parser and text clustering tool using Python, Pandas, and Scikit-learn.
- Implemented NLP preprocessing pipelines and SQL data storage.
""",
    },
    {
        "filename": "05_Vikram_Patel_Frontend_Mismatch.txt",
        "format": "txt",
        "content": """Vikram Patel
Email: vikram.patel@email.com
Education: B.E. in Computer Engineering

Summary:
Frontend Web Developer with 3 years of experience building responsive React and Next.js applications.

Skills:
JavaScript, TypeScript, React, Next.js, HTML, CSS, Tailwind, Git

Experience:
Frontend Engineer | PixelCraft Studio (2021 - Present)
- Built recruiter dashboards and SaaS portals in Next.js and React.
- Integrated REST APIs and improved web performance by 35%.
""",
    },
    {
        "filename": "06_Ananya_Gupta_NonTech_Mismatch.txt",
        "format": "txt",
        "content": """Ananya Gupta
Email: ananya.gupta@email.com
Education: MBA in Human Resources

Summary:
HR Specialist with 4 years of experience in talent acquisition, onboarding, and employee engagement.

Skills:
Recruitment, Sourcing, Interview Scheduling, Excel, Communication, Stakeholder Management

Experience:
Talent Acquisition Specialist | PeopleFirst Corp (2020 - Present)
- Screened candidate profiles manually and coordinated technical interviews.
- Maintained hiring trackers in Microsoft Excel.
""",
    },
]


def save_pdf(filepath: str, text: str) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    for line in text.split("\n"):
        # Replace unsupported unicode dashes if any
        safe_line = line.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_line)
    pdf.output(filepath)


def save_docx(filepath: str, text: str) -> None:
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(filepath)


def save_txt(filepath: str, text: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)


def generate_all_samples(output_dir: str = RESUME_DIR) -> None:
    os.makedirs(output_dir, exist_ok=True)
    for sample in SAMPLES:
        path = os.path.join(output_dir, sample["filename"])
        fmt = sample["format"]
        if fmt == "pdf":
            save_pdf(path, sample["content"])
        elif fmt == "docx":
            save_docx(path, sample["content"])
        else:
            save_txt(path, sample["content"])
        print(f"[CREATED] {path}")


if __name__ == "__main__":
    generate_all_samples()
    print("\nAll sample resumes generated successfully!")
