from src.pdf_reader import filter_pages, parse_page_ranges


def test_parse_page_ranges_supports_ranges_and_single_pages():
    assert parse_page_ranges("1-3, 5, 7-6", max_page=10) == [1, 2, 3, 5, 6, 7]


def test_parse_page_ranges_ignores_pages_outside_document():
    assert parse_page_ranges("0, 2, 99", max_page=5) == [2]


def test_filter_pages_returns_all_pages_without_selection():
    pages = [{"page": 1}, {"page": 2}]

    assert filter_pages(pages, None) == pages
