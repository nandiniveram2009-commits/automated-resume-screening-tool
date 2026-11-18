import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


def clean_text_for_nlp(text: str) -> str:
    """
    Clean raw text for TF-IDF vectorization:
    - lowercase
    - remove URLs and emails
    - keep alphanumeric words
    - remove standard English stopwords
    """
    if not text:
        return ""

    text = text.lower()
    # Remove emails & URLs
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    # Replace non-alphanumeric characters (keep spaces)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    # Collapse whitespace and filter stopwords
    tokens = [
        word for word in text.split()
        if word not in ENGLISH_STOP_WORDS and len(word) > 1
    ]
    return " ".join(tokens)
