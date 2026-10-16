# Question Paper Hub

One place for all previous question papers — academic (university, board) and competitive (JEE, NEET, UPSC, GATE, CAT, GRE, …).

## Run
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8020 --reload
```
Open http://localhost:8020

## Features
- Browse/search/filter by exam type, exam name, subject, year.
- Download PDFs; upload your own papers (community contributions).
- Request a paper that's missing.
- SQLite storage + file storage; seeded with sample papers on first run.

## API
- GET /api/stats, /api/exams, /api/papers, /api/papers/{id}, /api/papers/{id}/download
- POST /api/papers (multipart upload), POST /api/requests
