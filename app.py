import os
import fitz
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def extract_pdf_pages(uploaded_file):
    pdf_bytes = uploaded_file.read()
    pages = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text", sort=True).strip()

            pages.append({
                "page": page_number,
                "text": text,
                "word_count": len(text.split()),
                "char_count": len(text)
            })

    return pages


def clean_text(text):
    return " ".join(text.split())


def split_text(text, max_chars=8000):
    chunks = []

    for i in range(0, len(text), max_chars):
        chunks.append(text[i:i + max_chars])

    return chunks


def ask_gemini(prompt):
    response = client.interactions.create(
        model=GEMINI_MODEL,
        input=prompt
    )

    return response.output_text


def summarize_chunk(chunk):
    prompt = f"""
You are an academic PDF summarizer.

Summarize this PDF section clearly.

Include:
- Important points
- Definitions
- Key findings
- Simple explanation

Text:
{chunk}
"""

    return ask_gemini(prompt)


def create_final_summary(partial_summaries):
    combined = "\n\n".join(partial_summaries)

    prompt = f"""
Create a final structured summary from these partial PDF summaries.

Format:

1. Main Topic
2. Short Summary
3. Key Points
4. Important Details
5. Conclusion

Partial summaries:
{combined}
"""

    return ask_gemini(prompt)


def summarize_pdf(full_text):
    chunks = split_text(full_text)
    partial_summaries = []

    progress = st.progress(0)

    for index, chunk in enumerate(chunks):
        summary = summarize_chunk(chunk)
        partial_summaries.append(summary)
        progress.progress((index + 1) / len(chunks))

    return create_final_summary(partial_summaries)


st.set_page_config(
    page_title="AI PDF Summarizer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI PDF Summarizer")
st.write("Upload a PDF, analyze its content, and generate an AI summary using Gemini 2.5 Flash.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

    with st.spinner("Extracting text from PDF..."):
        pages = extract_pdf_pages(uploaded_file)

    df = pd.DataFrame(pages)

    full_text = "\n\n".join(df["text"].tolist())
    full_text = clean_text(full_text)

    if not full_text:
        st.error("No readable text found. This may be a scanned PDF and needs OCR.")
    else:
        st.subheader("PDF Statistics")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Pages", len(df))
        col2.metric("Total Words", int(df["word_count"].sum()))
        col3.metric("Total Characters", int(df["char_count"].sum()))

        st.subheader("Page-wise Word Count Chart")

        fig, ax = plt.subplots()
        ax.bar(df["page"], df["word_count"])
        ax.set_xlabel("Page Number")
        ax.set_ylabel("Word Count")
        ax.set_title("Words Per Page")
        st.pyplot(fig)

        with st.expander("View Extracted Text"):
            st.write(full_text[:10000])

        st.subheader("Generate Summary")

        if st.button("Summarize PDF"):
            with st.spinner("Generating summary using Gemini 2.5 Flash..."):
                summary = summarize_pdf(full_text)

            st.subheader("AI Generated Summary")
            st.write(summary)

            st.download_button(
                label="Download Summary",
                data=summary,
                file_name="pdf_summary.txt",
                mime="text/plain"
            )