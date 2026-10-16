import os, sqlite3, shutil, uuid, json, random
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "data" / "pyq.db"
UPLOAD_DIR = BASE / "uploads"
STATIC_DIR = BASE / "static"
FRONTEND = BASE / "frontend" / "index.html"
SEED_FILE = BASE / "seed" / "questions.json"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
(BASE / "data").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="PYQ Platform", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
if UPLOAD_DIR.exists():
    app.mount("/files", StaticFiles(directory=str(UPLOAD_DIR)), name="files")


def db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS exams (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        icon TEXT
    );
    CREATE TABLE IF NOT EXISTS papers (
        id TEXT PRIMARY KEY,
        exam_id TEXT NOT NULL,
        title TEXT NOT NULL,
        year INTEGER,
        shift TEXT,
        subject TEXT,
        stored_name TEXT,
        source_url TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(exam_id) REFERENCES exams(id)
    );
    CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        exam_id TEXT NOT NULL,
        paper_id TEXT,
        subject TEXT NOT NULL,
        chapter TEXT,
        topic TEXT,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct TEXT NOT NULL,
        explanation TEXT,
        difficulty TEXT DEFAULT 'Medium',
        year INTEGER,
        FOREIGN KEY(exam_id) REFERENCES exams(id)
    );
    CREATE TABLE IF NOT EXISTS attempts (
        id TEXT PRIMARY KEY,
        exam_id TEXT,
        mode TEXT,
        score INTEGER,
        total INTEGER,
        time_taken INTEGER,
        created_at TEXT NOT NULL
    );
    """)
    conn.commit()

    # seed exams if empty
    if conn.execute("SELECT COUNT(*) c FROM exams").fetchone()["c"] == 0:
        seed_exams(conn)
    if conn.execute("SELECT COUNT(*) c FROM questions").fetchone()["c"] == 0:
        seed_questions(conn)
    if conn.execute("SELECT COUNT(*) c FROM papers").fetchone()["c"] == 0:
        seed_papers(conn)
    conn.close()


def seed_exams(conn):
    exams = [
        ("jee-main", "JEE Main", "Engineering", "Joint Entrance Examination for NITs, IIITs, GFTIs", "⚙️"),
        ("jee-adv", "JEE Advanced", "Engineering", "For IIT admissions", "🔬"),
        ("neet", "NEET UG", "Medical", "National Eligibility cum Entrance Test for MBBS/BDS", "🩺"),
        ("gate-cse", "GATE CSE", "Engineering", "Graduate Aptitude Test for CS/IT", "💻"),
        ("upsc-cse", "UPSC CSE", "Government", "Civil Services Examination (IAS/IPS/IFS)", "🏛️"),
        ("cat", "CAT", "Management", "Common Admission Test for IIMs", "📊"),
        ("ssc-cgl", "SSC CGL", "Government", "Staff Selection Commission Combined Graduate Level", "📋"),
        ("ibps-po", "IBPS PO", "Banking", "Probationary Officer exam", "🏦"),
        ("cbse-12", "CBSE Class 12", "Academic", "Central Board Class 12 board exams", "📘"),
        ("cbse-10", "CBSE Class 10", "Academic", "Central Board Class 10 board exams", "📗"),
        ("cuet", "CUET UG", "University", "Common University Entrance Test", "🎓"),
        ("clat", "CLAT", "Law", "Common Law Admission Test", "⚖️"),
    ]
    for e in exams:
        conn.execute("INSERT INTO exams (id,name,category,description,icon) VALUES (?,?,?,?,?)", e)
    conn.commit()


def seed_papers(conn):
    # link to demo pdf if available
    demo = BASE / "static" / "demo.pdf"
    alt = Path("/home/user/racing-game/anki-generator/static/demo.pdf")
    src = demo if demo.exists() else (alt if alt.exists() else None)
    stored = None
    if src and src.exists():
        stored = "demo.pdf"
        if not (UPLOAD_DIR / "demo.pdf").exists():
            shutil.copy(src, UPLOAD_DIR / "demo.pdf")
    samples = [
        ("jee-main", "JEE Main 2024 - Shift 1", 2024, "Shift 1", "Physics, Chemistry, Maths"),
        ("jee-main", "JEE Main 2023 - Shift 2", 2023, "Shift 2", "Physics, Chemistry, Maths"),
        ("neet", "NEET UG 2024", 2024, None, "Biology, Physics, Chemistry"),
        ("neet", "NEET UG 2023", 2023, None, "Biology, Physics, Chemistry"),
        ("upsc-cse", "UPSC Prelims 2024 - GS Paper I", 2024, None, "General Studies"),
        ("gate-cse", "GATE CSE 2024", 2024, None, "Computer Science"),
        ("cbse-12", "CBSE Class 12 Physics 2024", 2024, None, "Physics"),
        ("cbse-12", "CBSE Class 12 Maths 2024", 2024, None, "Maths"),
        ("cuet", "CUET UG 2024 - English", 2024, None, "English"),
        ("clat", "CLAT 2024", 2024, None, "Legal Reasoning, GK"),
    ]
    for exam_id, title, year, shift, subj in samples:
        conn.execute("""INSERT INTO papers (id,exam_id,title,year,shift,subject,stored_name,created_at) VALUES (?,?,?,?,?,?,?,?)""",
            (uuid.uuid4().hex, exam_id, title, year, shift, subj, stored, datetime.utcnow().isoformat()))
    conn.commit()


def seed_questions(conn):
    if not SEED_FILE.exists():
        return
    data = json.loads(SEED_FILE.read_text())
    for q in data:
        conn.execute("""INSERT INTO questions (id,exam_id,paper_id,subject,chapter,topic,question,option_a,option_b,option_c,option_d,correct,explanation,difficulty,year)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uuid.uuid4().hex, q["exam_id"], None, q["subject"], q.get("chapter"), q.get("topic"),
             q["question"], q["a"], q["b"], q["c"], q["d"], q["correct"], q.get("explanation",""), q.get("difficulty","Medium"), q.get("year")))
    conn.commit()


init_db()


def row_to_dict(r):
    return {k: r[k] for k in r.keys()}


@app.get("/")
async def root():
    if FRONTEND.exists():
        return FileResponse(str(FRONTEND))
    return JSONResponse({"status": "ok"})


@app.get("/api/exams")
async def list_exams():
    conn = db()
    rows = conn.execute("SELECT * FROM exams ORDER BY category, name").fetchall()
    out = []
    for r in rows:
        d = row_to_dict(r)
        d["question_count"] = conn.execute("SELECT COUNT(*) c FROM questions WHERE exam_id=?", (r["id"],)).fetchone()["c"]
        d["paper_count"] = conn.execute("SELECT COUNT(*) c FROM papers WHERE exam_id=?", (r["id"],)).fetchone()["c"]
        out.append(d)
    conn.close()
    return out


@app.get("/api/exams/{eid}")
async def get_exam(eid: str):
    conn = db()
    r = conn.execute("SELECT * FROM exams WHERE id=?", (eid,)).fetchone()
    if not r:
        conn.close(); raise HTTPException(404, "Exam not found")
    d = row_to_dict(r)
    d["question_count"] = conn.execute("SELECT COUNT(*) c FROM questions WHERE exam_id=?", (eid,)).fetchone()["c"]
    d["paper_count"] = conn.execute("SELECT COUNT(*) c FROM papers WHERE exam_id=?", (eid,)).fetchone()["c"]
    # subjects
    subs = [x[0] for x in conn.execute("SELECT DISTINCT subject FROM questions WHERE exam_id=? ORDER BY subject", (eid,)).fetchall()]
    d["subjects"] = subs
    conn.close()
    return d


@app.get("/api/papers")
async def list_papers(exam_id: Optional[str]=None, year: Optional[int]=None, subject: Optional[str]=None):
    conn = db()
    where=[]; params=[]
    if exam_id: where.append("exam_id=?"); params.append(exam_id)
    if year: where.append("year=?"); params.append(year)
    if subject: where.append("subject LIKE ?"); params.append(f"%{subject}%")
    sql="SELECT * FROM papers" + (" WHERE "+" AND ".join(where) if where else "") + " ORDER BY year DESC"
    rows = conn.execute(sql, params).fetchall()
    out=[]
    for r in rows:
        d=row_to_dict(r)
        d["download_url"] = f"/api/papers/{r['id']}/download" if r["stored_name"] else None
        out.append(d)
    conn.close()
    return out


@app.get("/api/papers/{pid}/download")
async def download_paper(pid: str):
    conn = db()
    r = conn.execute("SELECT * FROM papers WHERE id=?", (pid,)).fetchone()
    conn.close()
    if not r or not r["stored_name"]:
        raise HTTPException(404, "File not available")
    path = UPLOAD_DIR / r["stored_name"]
    if not path.exists():
        raise HTTPException(404, "File missing")
    return FileResponse(str(path), filename=f"{r['title']}.pdf", media_type="application/pdf")


@app.get("/api/chapters")
async def chapters(exam_id: str, subject: Optional[str]=None):
    conn = db()
    where=["exam_id=?"]; params=[exam_id]
    if subject: where.append("subject=?"); params.append(subject)
    rows = conn.execute(f"SELECT subject, chapter, COUNT(*) c FROM questions WHERE {' AND '.join(where)} GROUP BY subject, chapter ORDER BY subject, chapter", params).fetchall()
    conn.close()
    out={}
    for r in rows:
        out.setdefault(r["subject"], []).append({"chapter": r["chapter"], "count": r["c"]})
    return out


@app.get("/api/questions")
async def list_questions(exam_id: Optional[str]=None, subject: Optional[str]=None, chapter: Optional[str]=None,
                        topic: Optional[str]=None, year: Optional[int]=None, difficulty: Optional[str]=None,
                        limit: int=Query(50,le=200), offset: int=0):
    conn = db()
    where=[]; params=[]
    if exam_id: where.append("exam_id=?"); params.append(exam_id)
    if subject: where.append("subject=?"); params.append(subject)
    if chapter: where.append("chapter=?"); params.append(chapter)
    if topic: where.append("topic=?"); params.append(topic)
    if year: where.append("year=?"); params.append(year)
    if difficulty: where.append("difficulty=?"); params.append(difficulty)
    sql="SELECT * FROM questions" + (" WHERE "+" AND ".join(where) if where else "") + " ORDER BY RANDOM() LIMIT ? OFFSET ?"
    rows = conn.execute(sql, params+[limit, offset]).fetchall()
    total = conn.execute("SELECT COUNT(*) c FROM questions" + (" WHERE "+" AND ".join(where) if where else ""), params).fetchone()["c"]
    conn.close()
    return {"total": total, "items": [row_to_dict(r) for r in rows]}


@app.get("/api/mock")
async def mock_questions(exam_id: str, subjects: Optional[str]=None, count: int=Query(30,le=100), difficulty: Optional[str]=None):
    conn = db()
    where=["exam_id=?"]; params=[exam_id]
    if subjects:
        subs=[s.strip() for s in subjects.split(",") if s.strip()]
        if subs:
            where.append("subject IN (%s)" % ",".join("?"*len(subs)))
            params += subs
    if difficulty:
        where.append("difficulty=?"); params.append(difficulty)
    sql="SELECT * FROM questions WHERE " + " AND ".join(where) + " ORDER BY RANDOM() LIMIT ?"
    rows = conn.execute(sql, params+[count]).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@app.post("/api/attempts")
async def save_attempt(exam_id: Optional[str]=Form(None), mode: str=Form("mock"), score: int=Form(0), total: int=Form(0), time_taken: int=Form(0)):
    aid = uuid.uuid4().hex
    conn = db()
    conn.execute("INSERT INTO attempts (id,exam_id,mode,score,total,time_taken,created_at) VALUES (?,?,?,?,?,?,?)",
        (aid, exam_id, mode, score, total, time_taken, datetime.utcnow().isoformat()))
    conn.commit(); conn.close()
    return {"id": aid}


@app.get("/api/attempts")
async def list_attempts(limit: int=20):
    conn = db()
    rows = conn.execute("SELECT * FROM attempts ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@app.get("/api/stats")
async def stats():
    conn = db()
    return {
        "exams": conn.execute("SELECT COUNT(*) c FROM exams").fetchone()["c"],
        "papers": conn.execute("SELECT COUNT(*) c FROM papers").fetchone()["c"],
        "questions": conn.execute("SELECT COUNT(*) c FROM questions").fetchone()["c"],
        "attempts": conn.execute("SELECT COUNT(*) c FROM attempts").fetchone()["c"],
    }


@app.post("/api/questions")
async def add_question(exam_id: str=Form(...), subject: str=Form(...), chapter: Optional[str]=Form(None),
                      topic: Optional[str]=Form(None), question: str=Form(...),
                      option_a: str=Form(...), option_b: str=Form(...), option_c: str=Form(...), option_d: str=Form(...),
                      correct: str=Form(...), explanation: Optional[str]=Form(None),
                      difficulty: Optional[str]=Form("Medium"), year: Optional[int]=Form(None)):
    qid = uuid.uuid4().hex
    conn = db()
    conn.execute("""INSERT INTO questions (id,exam_id,subject,chapter,topic,question,option_a,option_b,option_c,option_d,correct,explanation,difficulty,year)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (qid, exam_id, subject, chapter, topic, question, option_a, option_b, option_c, option_d, correct, explanation, difficulty, year))
    conn.commit(); conn.close()
    return {"id": qid}


@app.post("/api/upload-paper")
async def upload_paper(exam_id: str=Form(...), title: str=Form(...), year: Optional[int]=Form(None),
                      shift: Optional[str]=Form(None), subject: Optional[str]=Form(None),
                      source_url: Optional[str]=Form(None), file: UploadFile=File(...)):
    pid = uuid.uuid4().hex
    stored = f"{pid}.pdf"
    dst = UPLOAD_DIR / stored
    with dst.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    conn = db()
    conn.execute("""INSERT INTO papers (id,exam_id,title,year,shift,subject,stored_name,source_url,created_at) VALUES (?,?,?,?,?,?,?,?,?)""",
        (pid, exam_id, title, year, shift, subject, stored, source_url, datetime.utcnow().isoformat()))
    conn.commit(); conn.close()
    return {"id": pid}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8030, reload=True)
