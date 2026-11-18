import os
import pdfplumber
from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber with PyPDF2 fallback."""
    text_parts = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception:
        pass

    combined = "\n".join(text_parts).strip()
    if combined:
        return combined

    # Fallback to PyPDF2 if pdfplumber returned empty
    try:
        reader = PdfReader(file_path)
        fallback_parts = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(fallback_parts).strip()
    except Exception as exc:
        print(f"[ERROR] Failed to read PDF '{file_path}': {exc}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX paragraphs and tables."""
    try:
        doc = Document(file_path)
        parts = [para.text for para in doc.paragraphs if para.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = " ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    parts.append(row_text)
        return "\n".join(parts).strip()
    except Exception as exc:
        print(f"[ERROR] Failed to read DOCX '{file_path}': {exc}")
        return ""


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from plain TXT file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception as exc:
        print(f"[ERROR] Failed to read TXT '{file_path}': {exc}")
        return ""


def extract_resume_text(file_path: str) -> str:
    """Dispatch extraction based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    if ext == ".txt":
        return extract_text_from_txt(file_path)
    return ""
