from collections.abc import Callable
import json
import re

from google import genai

from src.pdf_reader import build_page_chunks
from src.prompts import (
    chunk_summary_prompt,
    final_summary_prompt,
    question_prompt,
    topic_extraction_prompt,
)


class GeminiSummarizer:
    def __init__(self, api_key: str, model: str):
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def ask(self, prompt: str) -> str:
        if hasattr(self.client, "interactions"):
            response = self.client.interactions.create(model=self.model, input=prompt)
            return response.output_text

        response = self.client.models.generate_content(model=self.model, contents=prompt)
        return response.text

    def summarize_pdf(
        self,
        pages: list[dict],
        style: str = "Academic",
        max_chars: int = 8000,
        progress_callback: Callable[[float], None] | None = None,
    ) -> str:
        chunks = build_page_chunks(pages, max_chars=max_chars)
        partial_summaries = []

        for index, chunk in enumerate(chunks):
            prompt = chunk_summary_prompt(chunk.text, style=style, pages=chunk.pages)
            partial_summaries.append(self.ask(prompt))

            if progress_callback:
                progress_callback((index + 1) / len(chunks))

        return self.ask(final_summary_prompt(partial_summaries, style=style))

    def answer_question(self, pages: list[dict], question: str, max_chars: int = 8000) -> str:
        chunks = build_page_chunks(pages, max_chars=max_chars)
        context = "\n\n".join(chunk.text for chunk in chunks)

        if len(context) > max_chars * 2:
            context = context[: max_chars * 2]

        return self.ask(question_prompt(context=context, question=question))

    def extract_learning_topics(
        self,
        pages: list[dict],
        limit: int = 5,
        max_chars: int = 8000,
    ) -> list[dict]:
        chunks = build_page_chunks(pages, max_chars=max_chars)
        context = "\n\n".join(chunk.text for chunk in chunks)

        if len(context) > max_chars * 2:
            context = context[: max_chars * 2]

        response = self.ask(topic_extraction_prompt(context=context, limit=limit))
        json_text = self._extract_json_array(response)
        topics = json.loads(json_text)

        return [
            {
                "topic": str(topic.get("topic", "")).strip(),
                "why_relevant": str(topic.get("why_relevant", "")).strip(),
                "search_query": str(topic.get("search_query", "")).strip(),
            }
            for topic in topics
            if topic.get("topic")
        ][:limit]

    @staticmethod
    def _extract_json_array(text: str) -> str:
        match = re.search(r"\[[\s\S]*\]", text)
        if not match:
            raise ValueError("Gemini did not return a JSON topic list.")

        return match.group(0)
