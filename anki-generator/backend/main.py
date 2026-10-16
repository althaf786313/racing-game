import os, re, json, tempfile, uuid
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pypdf
import genanki
import httpx

APP_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = APP_DIR / "static"
FRONTEND = APP_DIR / "frontend" / "index.html"

app = FastAPI(title="PastPaper → Anki", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Serve frontend
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def extract_pdf_text(file_bytes: bytes) -> str:
    reader = pypdf.PdfReader(__import__("io").BytesIO(file_bytes))
    pages = []
    for i, p in enumerate(reader.pages):
        try:
            pages.append(f"\n--- PAGE {i+1} ---\n" + (p.extract_text() or ""))
        except Exception:
            pages.append(f"\n--- PAGE {i+1} ---\n")
    return "\n".join(pages)


def heuristic_questions(text: str) -> List[dict]:
    """Best-effort extraction of numbered questions from raw exam text."""
    lines = text.splitlines()
    # Normalize
    questions = []
    current = None
    q_re = re.compile(r"^\s*(?:Q(?:uestion)?\s*)?(\d{1,3})[\.\)]\s*(.*)$", re.IGNORECASE)
    sub_re = re.compile(r"^\s*\(?([a-z]|[ivx]{1,4})\)?[\.\)]\s*(.+)$", re.IGNORECASE)
    for line in lines:
        line = line.rstrip()
        if not line.strip():
            if current is not None:
                current["front"] += "\n"
            continue
        m = q_re.match(line)
        if m:
            if current is not None:
                questions.append(current)
            current = {"front": m.group(2).strip() or f"Question {m.group(1)}", "back": "", "tags": []}
            continue
        if current is not None:
            # sub-part
            sm = sub_re.match(line)
            if sm and len(sm.group(1)) <= 4:
                current["front"] += f"\n({sm.group(1)}) {sm.group(2)}"
            else:
                current["front"] += " " + line.strip()
    if current is not None:
        questions.append(current)
    # Clean up
    out = []
    for q in questions:
        front = re.sub(r"\s+\n", "\n", q["front"]).strip()
        if len(front) < 8:
            continue
        out.append({"front": front, "back": q["back"], "tags": q["tags"]})
    return out


LLM_PROMPT = """You are an exam-question extractor and tutor.

Given raw text extracted from a past exam paper, return a JSON array of objects with keys:
- "front": the question text, cleaned, preserving sub-parts (a), (b) etc.
- "back": a concise, correct answer. If the source provides an answer/marking scheme, use it; otherwise produce your best answer. If unsure, say "Review your notes / consult marking scheme."
- "tags": array of 1-4 short topic keywords.

Rules:
- Include only actual questions (not instructions, rubrics, headers, page numbers).
- One object per top-level question (combine its sub-parts into "front").
- Return ONLY valid JSON, no markdown fences.

RAW TEXT:
"""


async def llm_extract(text: str, provider: str, api_key: str, model: Optional[str]) -> List[dict]:
    text = text[:18000]  # safety
    if provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        body = {
            "model": model or "claude-3-5-haiku-latest",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": LLM_PROMPT + text}],
        }
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(url, headers=headers, json=body)
        r.raise_for_status()
        content = r.json()["content"][0]["text"]
    else:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        body = {
            "model": model or "gpt-4o-mini",
            "messages": [{"role": "user", "content": LLM_PROMPT + text}],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(url, headers=headers, json=body)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
    # strip fences
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    data = json.loads(content)
    out = []
    for item in data:
        out.append({
            "front": str(item.get("front", "")).strip(),
            "back": str(item.get("back", "")).strip(),
            "tags": [str(t) for t in (item.get("tags") or [])],
        })
    return [q for q in out if q["front"]]


def build_apkg(questions: List[dict], deck_name: str) -> str:
    model = genanki.Model(
        1607392319,
        "PastPaper Basic",
        fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Tags"}],
        templates=[{
            "name": "Card 1",
            "qfmt": "{{Front}}",
            "afmt": "{{FrontSide}}<hr id=answer>{{Back}}",
        }],
    )
    deck = genanki.Deck(2059400110, deck_name)
    for q in questions:
        note = genanki.Note(
            model=model,
            fields=[q["front"], q["back"] or "—", " ".join(q.get("tags", []))],
            tags=q.get("tags", []),
        )
        deck.add_note(note)
    out_path = os.path.join(tempfile.gettempdir(), f"pastpaper_{uuid.uuid4().hex}.apkg")
    genanki.Package(deck).write_to_file(out_path)
    return out_path


@app.get("/")
async def root():
    if FRONTEND.exists():
        return FileResponse(str(FRONTEND))
    return JSONResponse({"status": "ok", "message": "frontend missing"})


@app.post("/api/generate")
async def generate(
    file: UploadFile = File(...),
    provider: str = Form("openai"),
    api_key: str = Form(""),
    model: str = Form(""),
    deck_name: str = Form("Past Paper Deck"),
    use_llm: str = Form("false"),
):
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")
    text = extract_pdf_text(data)
    if use_llm == "true" and api_key.strip():
        try:
            questions = await llm_extract(text, provider, api_key.strip(), model.strip() or None)
        except Exception as e:
            questions = heuristic_questions(text)
            for q in questions:
                q["back"] = f"(LLM failed: {e}) — review your notes."
    else:
        questions = heuristic_questions(text)
    if not questions:
        raise HTTPException(422, "No questions could be extracted. Try a text-based PDF.")
    path = build_apkg(questions, deck_name or "Past Paper Deck")
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=f"{(deck_name or 'pastpaper').replace(' ','_')}.apkg",
        headers={"X-Question-Count": str(len(questions))},
    )


@app.post("/api/preview")
async def preview(
    file: UploadFile = File(...),
    provider: str = Form("openai"),
    api_key: str = Form(""),
    model: str = Form(""),
    use_llm: str = Form("false"),
):
    data = await file.read()
    text = extract_pdf_text(data)
    if use_llm == "true" and api_key.strip():
        try:
            questions = await llm_extract(text, provider, api_key.strip(), model.strip() or None)
        except Exception as e:
            questions = heuristic_questions(text)
            for q in questions:
                q["back"] = f"(LLM error: {e}) — review your notes."
    else:
        questions = heuristic_questions(text)
    return JSONResponse({"count": len(questions), "questions": questions, "chars": len(text)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
