# AI PDF Summarizer

A Streamlit app for extracting PDF text, reviewing document analytics, generating Gemini-powered summaries, and asking questions about selected PDF pages.

## Features

- Page-by-page PDF text extraction
- Page range selection
- Summary styles: academic, brief, detailed, executive, study notes, and simple explanation
- Page-aware summary prompts
- Ask questions about the uploaded PDF
- Word count chart, reading time, empty page count, and keyword frequency
- Export summary as TXT, Markdown, or JSON
- Export page statistics as CSV

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Gemini API key to `.env`.

## Run

```bash
streamlit run app.py
```

## Project Structure

```text
pdf-summarizer/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── pdf_reader.py
│   ├── summarizer.py
│   ├── prompts.py
│   ├── analytics.py
│   └── exporters.py
├── tests/
│   ├── test_pdf_reader.py
│   └── test_analytics.py
└── outputs/
    └── .gitkeep
```

## OCR Note

If a PDF contains only scanned images, the app will detect that no readable text is available. OCR can be added with a system OCR engine such as Tesseract or a vision-capable model.
