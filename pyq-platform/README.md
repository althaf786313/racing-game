# PYQ Platform

Practice previous year questions like ExamGOAL/PYQ Junction — exam-wise, chapter-wise, with mock tests.

## Run
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8030 --reload
```
Open http://localhost:8030

## Features
- Exam catalog (12 exams) with question & paper counts
- Chapter-wise practice with instant feedback & explanations
- Timed mock tests with OMR palette, negative marking, review
- Bookmarks & progress (localStorage)
- Upload/import papers
- 40 seeded MCQs across subjects
