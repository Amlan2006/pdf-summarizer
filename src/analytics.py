from collections import Counter
import re


STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "because",
    "before",
    "between",
    "could",
    "from",
    "have",
    "into",
    "more",
    "other",
    "over",
    "such",
    "than",
    "that",
    "their",
    "there",
    "these",
    "this",
    "through",
    "were",
    "when",
    "where",
    "which",
    "while",
    "with",
    "would",
}


def calculate_document_stats(pages: list[dict]) -> dict:
    total_words = sum(page["word_count"] for page in pages)

    return {
        "pages": len(pages),
        "words": total_words,
        "characters": sum(page["char_count"] for page in pages),
        "reading_minutes": max(1, round(total_words / 200)),
        "empty_pages": sum(1 for page in pages if not page["text"].strip()),
    }


def keyword_frequency(text: str, limit: int = 10) -> list[tuple[str, int]]:
    words = re.findall(r"[A-Za-z][A-Za-z-]{2,}", text.lower())
    filtered_words = [word for word in words if word not in STOPWORDS]

    return Counter(filtered_words).most_common(limit)
