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


def important_keywords(text: str, limit: int = 10) -> list[dict]:
    tokens = re.findall(r"[A-Za-z][A-Za-z-]{2,}", text)
    normalized_tokens = [token.lower() for token in tokens]
    meaningful_tokens = [
        token
        for token in tokens
        if token.lower() not in STOPWORDS and len(token) > 2
    ]

    candidates = Counter()
    display_names = {}

    for token in meaningful_tokens:
        key = token.lower()
        candidates[key] += 1
        display_names.setdefault(key, token)

    for size in (2, 3):
        for index in range(0, len(meaningful_tokens) - size + 1):
            phrase_tokens = meaningful_tokens[index:index + size]
            phrase_key = " ".join(token.lower() for token in phrase_tokens)

            if len(set(phrase_key.split())) == 1:
                continue

            candidates[phrase_key] += 1
            display_names.setdefault(phrase_key, " ".join(phrase_tokens))

    scored_keywords = []
    for key, count in candidates.items():
        words = key.split()
        display_name = display_names[key]
        original_parts = display_name.split()
        proper_bonus = sum(1 for part in original_parts if part[:1].isupper()) * 0.35
        acronym_bonus = sum(1 for part in original_parts if part.isupper() and len(part) > 1) * 0.75
        phrase_bonus = 1.2 * (len(words) - 1)
        repeat_bonus = count * (1.7 if len(words) > 1 else 1.0)
        document_spread_bonus = 0.4 if normalized_tokens.count(words[0]) > 1 else 0
        score = repeat_bonus + phrase_bonus + proper_bonus + acronym_bonus + document_spread_bonus

        scored_keywords.append(
            {
                "keyword": display_name,
                "occurrences": count,
                "score": round(score, 2),
            }
        )

    scored_keywords.sort(key=lambda item: (-item["score"], -item["occurrences"], item["keyword"].lower()))

    return scored_keywords[:limit]

print("hello world")
print("hello world")
