from dataclasses import dataclass
import re

import fitz


@dataclass(frozen=True)
class TextChunk:
    text: str
    pages: tuple[int, ...]


def _read_upload_bytes(uploaded_file) -> bytes:
    if hasattr(uploaded_file, "getvalue"):
        return uploaded_file.getvalue()

    uploaded_file.seek(0)
    return uploaded_file.read()


def extract_pdf_pages(uploaded_file) -> list[dict]:
    pdf_bytes = _read_upload_bytes(uploaded_file)
    pages = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text", sort=True).strip()

            pages.append(
                {
                    "page": page_number,
                    "text": text,
                    "word_count": len(text.split()),
                    "char_count": len(text),
                }
            )

    return pages


def clean_text(text: str) -> str:
    return " ".join(text.split())


def parse_page_ranges(value: str, max_page: int) -> list[int]:
    pages = set()

    for part in value.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            start_text, end_text = part.split("-", 1)
            try:
                start = int(start_text.strip())
                end = int(end_text.strip())
            except ValueError as exc:
                raise ValueError(f"Invalid page range: {part}") from exc

            if start > end:
                start, end = end, start
            pages.update(range(start, end + 1))
        else:
            try:
                pages.add(int(part))
            except ValueError as exc:
                raise ValueError(f"Invalid page number: {part}") from exc

    return sorted(page for page in pages if 1 <= page <= max_page)


def filter_pages(pages: list[dict], selected_pages: list[int] | None) -> list[dict]:
    if not selected_pages:
        return pages

    selected = set(selected_pages)
    return [page for page in pages if page["page"] in selected]


def build_page_chunks(pages: list[dict], max_chars: int = 8000) -> list[TextChunk]:
    chunks = []
    current_parts = []
    current_pages = []
    current_size = 0

    for page in pages:
        text = clean_text(page["text"])
        if not text:
            continue

        page_text = f"[Page {page['page']}]\n{text}"
        page_size = len(page_text)

        if current_parts and current_size + page_size > max_chars:
            chunks.append(TextChunk(text="\n\n".join(current_parts), pages=tuple(current_pages)))
            current_parts = []
            current_pages = []
            current_size = 0

        if page_size <= max_chars:
            current_parts.append(page_text)
            current_pages.append(page["page"])
            current_size += page_size
            continue

        for paragraph in re.split(r"\n\s*\n", page_text):
            paragraph = clean_text(paragraph)
            if not paragraph:
                continue

            if current_parts and current_size + len(paragraph) > max_chars:
                chunks.append(TextChunk(text="\n\n".join(current_parts), pages=tuple(current_pages)))
                current_parts = []
                current_pages = []
                current_size = 0

            current_parts.append(paragraph)
            if page["page"] not in current_pages:
                current_pages.append(page["page"])
            current_size += len(paragraph)

    if current_parts:
        chunks.append(TextChunk(text="\n\n".join(current_parts), pages=tuple(current_pages)))

    return chunks
