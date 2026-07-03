SUMMARY_STYLES = {
    "Academic": "Use an academic tone with clear definitions, key findings, and important details.",
    "Brief": "Keep the summary concise and focused on only the most important ideas.",
    "Detailed": "Create a thorough summary with context, supporting points, and nuanced details.",
    "Executive": "Write for a busy decision-maker. Highlight outcomes, risks, and recommended attention areas.",
    "Study Notes": "Write as study notes with headings, bullet points, definitions, and review-friendly phrasing.",
    "Explain Simply": "Explain the document in simple, plain language without assuming expert knowledge.",
}


def chunk_summary_prompt(chunk_text: str, style: str, pages: tuple[int, ...]) -> str:
    style_instruction = SUMMARY_STYLES.get(style, SUMMARY_STYLES["Academic"])
    page_label = ", ".join(str(page) for page in pages)

    return f"""
You are a careful PDF summarizer.

Summarize this PDF section.
Style: {style_instruction}
Source pages: {page_label}

Include page references when making specific claims.

Text:
{chunk_text}
"""


def final_summary_prompt(partial_summaries: list[str], style: str) -> str:
    style_instruction = SUMMARY_STYLES.get(style, SUMMARY_STYLES["Academic"])
    combined = "\n\n".join(partial_summaries)

    return f"""
Create a final structured PDF summary from these partial summaries.
Style: {style_instruction}

Use this format:

1. Main Topic
2. Short Summary
3. Key Points
4. Important Details
5. Key Terms and Definitions
6. Conclusion

Preserve useful page references from the partial summaries.

Partial summaries:
{combined}
"""


def question_prompt(context: str, question: str) -> str:
    return f"""
Answer the user's question using only the PDF context below.
If the answer is not in the context, say that the PDF text does not provide enough information.
Include page references where possible.

Question:
{question}

PDF context:
{context}
"""
