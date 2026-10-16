# PastPaper → Anki

Turns a past exam paper PDF into an importable Anki deck (.apkg).

## Run
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Open http://localhost:8000

## How it works
- Extracts text from the PDF (pypdf).
- Heuristically splits into numbered questions (works offline, no key).
- Optional: if you paste an OpenAI/Anthropic key and enable "Use AI", questions are cleaned and answers + topic tags are generated.
- Builds an .apkg with genanki. Import via Anki → File → Import.

## Notes
- Scanned (image-only) PDFs won't extract text; run OCR first.
- API key stays in your browser (localStorage not used; sent per request only).
