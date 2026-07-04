from src.analytics import calculate_document_stats, important_keywords, keyword_frequency


def test_calculate_document_stats_counts_empty_pages_and_reading_time():
    pages = [
        {"text": "one two", "word_count": 2, "char_count": 7},
        {"text": "", "word_count": 0, "char_count": 0},
    ]

    assert calculate_document_stats(pages) == {
        "pages": 2,
        "words": 2,
        "characters": 7,
        "reading_minutes": 1,
        "empty_pages": 1,
    }


def test_keyword_frequency_removes_common_words():
    assert keyword_frequency("This paper studies climate climate risk.", limit=2) == [
        ("climate", 2),
        ("paper", 1),
    ]


def test_important_keywords_prefers_repeated_multi_word_terms():
    keywords = important_keywords(
        "The Transformer Architecture improves neural networks. "
        "Transformer Architecture is useful for NLP systems.",
        limit=3,
    )

    assert keywords[0]["keyword"] == "Transformer Architecture"
    assert keywords[0]["occurrences"] == 2
