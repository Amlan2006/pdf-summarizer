import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.analytics import calculate_document_stats, important_keywords
from src.config import get_settings
from src.exporters import summary_to_json, summary_to_markdown
from src.pdf_reader import (
    clean_text,
    extract_pdf_pages,
    filter_pages,
    parse_page_ranges,
)
from src.summarizer import GeminiSummarizer


st.set_page_config(
    page_title="AI PDF Summarizer",
    page_icon="PDF",
    layout="wide",
)


@st.cache_resource
def get_summarizer(api_key, model):
    return GeminiSummarizer(api_key=api_key, model=model)


def render_word_count_chart(df):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df["page"], df["word_count"], color="#2f6f73")
    ax.set_xlabel("Page Number")
    ax.set_ylabel("Word Count")
    ax.set_title("Words Per Page")
    st.pyplot(fig)


def render_summary_downloads(summary, uploaded_name):
    base_name = uploaded_name.rsplit(".", 1)[0]
    col1, col2, col3 = st.columns(3)

    col1.download_button(
        label="Download TXT",
        data=summary,
        file_name=f"{base_name}_summary.txt",
        mime="text/plain",
        use_container_width=True,
    )
    col2.download_button(
        label="Download Markdown",
        data=summary_to_markdown(summary, title=f"{base_name} Summary"),
        file_name=f"{base_name}_summary.md",
        mime="text/markdown",
        use_container_width=True,
    )
    col3.download_button(
        label="Download JSON",
        data=summary_to_json(summary, source_file=uploaded_name),
        file_name=f"{base_name}_summary.json",
        mime="application/json",
        use_container_width=True,
    )


settings = get_settings()

st.title("AI PDF Summarizer")
st.caption("Upload a PDF, inspect its content, summarize selected pages, and ask questions with Gemini.")

with st.sidebar:
    st.header("Options")
    summary_style = st.selectbox(
        "Summary style",
        [
            "Academic",
            "Brief",
            "Detailed",
            "Executive",
            "Study Notes",
            "Explain Simply",
        ],
    )
    page_range_text = st.text_input("Pages to use", placeholder="Example: 1-3, 7, 10-12")
    max_chars = st.slider("Chunk size", min_value=3000, max_value=14000, value=8000, step=1000)
    keyword_limit = st.slider("Important keywords to show", min_value=5, max_value=25, value=10)

    st.divider()
    st.write(f"Model: `{settings.gemini_model}`")
    if not settings.gemini_api_key:
        st.warning("Add GEMINI_API_KEY to .env before generating summaries or answers.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

    with st.spinner("Extracting text from PDF..."):
        pages = extract_pdf_pages(uploaded_file)

    all_page_count = len(pages)
    selected_pages = None
    if page_range_text:
        try:
            selected_pages = parse_page_ranges(page_range_text, all_page_count)
        except ValueError as exc:
            st.error(str(exc))
            st.stop()

        if not selected_pages:
            st.warning(f"No valid pages found. Enter pages between 1 and {all_page_count}.")
            st.stop()

    pages = filter_pages(pages, selected_pages)
    df = pd.DataFrame(pages)

    full_text = clean_text("\n\n".join(page["text"] for page in pages))
    readable_pages = [page for page in pages if page["text"].strip()]

    if not readable_pages:
        st.error("No readable text found in the selected pages. This is likely a scanned PDF and needs OCR.")
        st.info("OCR support is the next natural add-on: install an OCR engine such as Tesseract or use a vision-capable model.")
    else:
        stats = calculate_document_stats(pages)

        st.subheader("PDF Statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Selected Pages", stats["pages"])
        col2.metric("Total Words", stats["words"])
        col3.metric("Reading Time", f"{stats['reading_minutes']} min")
        col4.metric("Empty Pages", stats["empty_pages"])

        tab_summary, tab_ask, tab_stats, tab_text = st.tabs(
            ["Summary", "Ask PDF", "Analytics", "Extracted Text"]
        )

        with tab_summary:
            st.subheader("Generate Summary")
            st.write(f"Using pages: {', '.join(str(page['page']) for page in pages)}")

            if st.button("Summarize PDF", type="primary", disabled=not settings.gemini_api_key):
                progress = st.progress(0)
                summarizer = get_summarizer(settings.gemini_api_key, settings.gemini_model)

                with st.spinner("Generating page-aware summary..."):
                    summary = summarizer.summarize_pdf(
                        pages,
                        style=summary_style,
                        max_chars=max_chars,
                        progress_callback=progress.progress,
                    )

                st.session_state["summary"] = summary
                st.session_state["summary_source"] = uploaded_file.name

            if st.session_state.get("summary"):
                st.subheader("AI Generated Summary")
                st.write(st.session_state["summary"])
                render_summary_downloads(st.session_state["summary"], st.session_state["summary_source"])

        with tab_ask:
            st.subheader("Ask a Question")
            question = st.text_area("Question", placeholder="Example: What are the main findings?")

            if st.button("Ask PDF", disabled=not settings.gemini_api_key or not question.strip()):
                summarizer = get_summarizer(settings.gemini_api_key, settings.gemini_model)

                with st.spinner("Reading the PDF context..."):
                    answer = summarizer.answer_question(pages, question, max_chars=max_chars)

                st.subheader("Answer")
                st.write(answer)

        with tab_stats:
            st.subheader("Page-wise Word Count")
            render_word_count_chart(df)

            st.subheader("Important Keywords")
            keywords = important_keywords(full_text, limit=keyword_limit)
            if keywords:
                keyword_df = pd.DataFrame(keywords)
                st.dataframe(keyword_df, use_container_width=True, hide_index=True)
            else:
                st.write("No keywords found.")

            st.download_button(
                label="Download Page Stats CSV",
                data=df.drop(columns=["text"]).to_csv(index=False),
                file_name="pdf_page_stats.csv",
                mime="text/csv",
            )

        with tab_text:
            st.subheader("Extracted Text")
            st.text_area("Text preview", value=full_text[:20000], height=400)
else:
    st.info("Upload a PDF to begin.")
