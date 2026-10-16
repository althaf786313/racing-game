import os, sqlite3, shutil, uuid, json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "data" / "hub.db"
UPLOAD_DIR = BASE / "uploads"
STATIC_DIR = BASE / "static"
FRONTEND = BASE / "frontend" / "index.html"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
(BASE / "data").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Question Paper Hub", version="1.0.0")
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
    conn.execute("""CREATE TABLE IF NOT EXISTS papers (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        exam_type TEXT NOT NULL,        -- Academic | Competitive
        exam_name TEXT NOT NULL,       -- e.g. JEE Main, B.Tech CSE Sem 3
        subject TEXT,
        year INTEGER,
        semester TEXT,
        university TEXT,
        filename TEXT NOT NULL,
        stored_name TEXT NOT NULL,
        source_url TEXT,
        size INTEGER,
        downloads INTEGER DEFAULT 0,
        uploaded_by TEXT DEFAULT 'community',
        created_at TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS requests (
        id TEXT PRIMARY KEY,
        exam_name TEXT NOT NULL,
        subject TEXT,
        year INTEGER,
        note TEXT,
        created_at TEXT NOT NULL
    )""")
    conn.commit()
    # migrate: add source_url if missing
    cols = [r[1] for r in conn.execute("PRAGMA table_info(papers)").fetchall()]
    if "source_url" not in cols:
        conn.execute("ALTER TABLE papers ADD COLUMN source_url TEXT")
        conn.commit()
    # seed if empty
    cur = conn.execute("SELECT COUNT(*) c FROM papers")
    if cur.fetchone()["c"] == 0:
        seed_papers(conn)
    conn.close()


def seed_papers(conn):
    seed_dir = BASE / "seed"
    seed_dir.mkdir(exist_ok=True)
    # create a demo pdf if missing
    demo = seed_dir / "demo.pdf"
    if not demo.exists():
        src = BASE / "static" / "demo.pdf" if (BASE/"static"/"demo.pdf").exists() else None
        # fallback: copy from anki-generator demo if present
        alt = Path("/home/user/racing-game/anki-generator/static/demo.pdf")
        if alt.exists():
            shutil.copy(alt, demo)
    samples = [
        ("JEE Main 2024 - Shift 1 (Physics/Chem/Maths)", "Competitive", "JEE Main", "Physics, Chemistry, Maths", 2024, None, "NTA", "https://ntaexampapers.com/question-papers/"),
        ("JEE Main 2023 - Shift 2", "Competitive", "JEE Main", "Physics, Chemistry, Maths", 2023, None, "NTA", "https://ntaexampapers.com/question-papers/"),
        ("JEE Advanced 2024 - Paper 1", "Competitive", "JEE Advanced", "Physics, Chemistry, Maths", 2024, None, "IIT", "https://jeeadv.ac.in/"),
        ("NEET UG 2024 Question Paper", "Competitive", "NEET", "Biology, Physics, Chemistry", 2024, None, "NTA", "https://ntaexampapers.com/question-papers/"),
        ("NEET UG 2023 Question Paper", "Competitive", "NEET", "Biology, Physics, Chemistry", 2023, None, "NTA", "https://ntaexampapers.com/question-papers/"),
        ("UPSC Civil Services Prelims 2024 - GS Paper I", "Competitive", "UPSC CSE", "General Studies", 2024, None, "UPSC", "https://www.upsc.gov.in/examinations/previous-question-papers"),
        ("UPSC Civil Services Mains 2023 - Essay", "Competitive", "UPSC CSE", "Essay", 2023, None, "UPSC", "https://www.upsc.gov.in/examinations/previous-question-papers"),
        ("GATE 2024 - Computer Science", "Competitive", "GATE", "Computer Science", 2024, None, "IIT", "https://gate2024.iisc.ac.in/"),
        ("CAT 2023 Question Paper", "Competitive", "CAT", "Quant, VARC, DILR", 2023, None, "IIM", "https://iimcat.ac.in/"),
        ("GRE General Test - Practice Paper", "Competitive", "GRE", "Verbal, Quant, AWA", 2024, None, "ETS", "https://www.ets.org/gre.html"),
        ("CUET UG 2024 - English", "Competitive", "CUET", "English", 2024, None, "NTA", "https://ntaexampapers.com/question-papers/"),
        ("CLAT 2024 Question Paper", "Competitive", "CLAT", "Legal Reasoning, GK", 2024, None, "Consortium of NLUs", "https://consortiumofnlus.ac.in/"),
        ("IBPS PO Prelims 2023", "Competitive", "IBPS PO", "Reasoning, Quant, English", 2023, None, "IBPS", "https://www.ibps.in/"),
        ("SSC CGL Tier 1 2023", "Competitive", "SSC CGL", "GK, Reasoning, Quant, English", 2023, None, "SSC", "https://ssc.nic.in/"),
        ("BITSAT 2024", "Competitive", "BITSAT", "Physics, Chemistry, Maths, English", 2024, None, "BITS Pilani", "https://www.bitsadmission.com/"),
        ("NDA 2024 - Maths", "Competitive", "NDA", "Mathematics", 2024, None, "UPSC", "https://www.upsc.gov.in/examinations/previous-question-papers"),
        ("B.Tech CSE - Data Structures (Sem 3)", "Academic", "University Exam", "Data Structures", 2023, "3", "Generic University", None),
        ("B.Tech CSE - Operating Systems (Sem 4)", "Academic", "University Exam", "Operating Systems", 2023, "4", "Generic University", None),
        ("B.Sc Physics - Mechanics (Sem 2)", "Academic", "University Exam", "Mechanics", 2024, "2", "Generic University", None),
        ("MBA - Financial Management (Sem 1)", "Academic", "University Exam", "Financial Management", 2023, "1", "Generic University", None),
        ("Class 12 Physics Board Paper 2024", "Academic", "Board Exam (CBSE)", "Physics", 2024, "12", "CBSE", "https://www.cbse.gov.in/"),
        ("Class 12 Maths Board Paper 2024", "Academic", "Board Exam (CBSE)", "Maths", 2024, "12", "CBSE", "https://www.cbse.gov.in/"),
        ("Class 10 Science Board Paper 2024", "Academic", "Board Exam (CBSE)", "Science", 2024, "10", "CBSE", "https://www.cbse.gov.in/"),
        ("IGNOU BCA - TEE June 2024", "Academic", "IGNOU", "BCA", 2024, None, "IGNOU", "https://webservices.ignou.ac.in/Pre-Question/"),
        ("DU B.Com - Financial Accounting Sem 2", "Academic", "Delhi University", "Financial Accounting", 2023, "2", "DU", "https://www.du.ac.in/"),
        ("NIOS Senior Secondary Physics 2024", "Academic", "NIOS", "Physics", 2024, "12", "NIOS", "https://nios.ac.in/student-information-section/question-paper-of-previous-year-examination-academic.aspx"),
    ]
    for title, etype, exam, subj, year, sem, uni, src in samples:
        pid = uuid.uuid4().hex
        stored = f"{pid}.pdf"
        dst = UPLOAD_DIR / stored
        if demo.exists():
            shutil.copy(demo, dst)
        else:
            dst.write_bytes(b"%PDF-1.4\n%%EOF\n")
        conn.execute("""INSERT INTO papers (id,title,exam_type,exam_name,subject,year,semester,university,filename,stored_name,size,source_url,created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (pid, title, etype, exam, subj, year, sem, uni, "question_paper.pdf", stored, dst.stat().st_size if dst.exists() else 0, src, datetime.utcnow().isoformat()))
    conn.commit()


init_db()


def row_to_dict(r):
    return {
        "id": r["id"], "title": r["title"], "exam_type": r["exam_type"],
        "exam_name": r["exam_name"], "subject": r["subject"], "year": r["year"],
        "semester": r["semester"], "university": r["university"],
        "downloads": r["downloads"], "uploaded_by": r["uploaded_by"],
        "created_at": r["created_at"], "size": r["size"],
        "download_url": f"/api/papers/{r['id']}/download",
        "source_url": r["source_url"],
    }


@app.get("/")
async def root():
    if FRONTEND.exists():
        return FileResponse(str(FRONTEND))
    return JSONResponse({"status": "ok"})


@app.get("/api/stats")
async def stats():
    conn = db()
    total = conn.execute("SELECT COUNT(*) c FROM papers").fetchone()["c"]
    ac = conn.execute("SELECT COUNT(*) c FROM papers WHERE exam_type='Academic'").fetchone()["c"]
    comp = conn.execute("SELECT COUNT(*) c FROM papers WHERE exam_type='Competitive'").fetchone()["c"]
    dl = conn.execute("SELECT COALESCE(SUM(downloads),0) s FROM papers").fetchone()["s"]
    exams = conn.execute("SELECT COUNT(DISTINCT exam_name) c FROM papers").fetchone()["c"]
    conn.close()
    return {"total": total, "academic": ac, "competitive": comp, "downloads": dl, "exams": exams}


@app.get("/api/exams")
async def exams():
    conn = db()
    rows = conn.execute("SELECT exam_name, exam_type, COUNT(*) c FROM papers GROUP BY exam_name, exam_type ORDER BY exam_type, exam_name").fetchall()
    conn.close()
    return [{"exam_name": r["exam_name"], "exam_type": r["exam_type"], "count": r["c"]} for r in rows]


@app.get("/api/papers")
async def list_papers(
    q: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    exam_name: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    conn = db()
    where = []
    params = []
    if q:
        where.append("(title LIKE ? OR subject LIKE ? OR exam_name LIKE ?)")
        like = f"%{q}%"
        params += [like, like, like]
    if exam_type:
        where.append("exam_type = ?")
        params.append(exam_type)
    if exam_name:
        where.append("exam_name = ?")
        params.append(exam_name)
    if subject:
        where.append("subject LIKE ?")
        params.append(f"%{subject}%")
    if year:
        where.append("year = ?")
        params.append(year)
    sql = "SELECT * FROM papers"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY year DESC, created_at DESC"
    total = conn.execute("SELECT COUNT(*) c FROM papers" + (" WHERE " + " AND ".join(where) if where else ""), params).fetchone()["c"]
    offset = (page - 1) * page_size
    rows = conn.execute(sql + " LIMIT ? OFFSET ?", params + [page_size, offset]).fetchall()
    conn.close()
    return {"total": total, "page": page, "page_size": page_size, "items": [row_to_dict(r) for r in rows]}


@app.get("/api/papers/{pid}")
async def get_paper(pid: str):
    conn = db()
    r = conn.execute("SELECT * FROM papers WHERE id=?", (pid,)).fetchone()
    conn.close()
    if not r:
        raise HTTPException(404, "Not found")
    return row_to_dict(r)


@app.get("/api/papers/{pid}/download")
async def download_paper(pid: str):
    conn = db()
    r = conn.execute("SELECT * FROM papers WHERE id=?", (pid,)).fetchone()
    if not r:
        conn.close()
        raise HTTPException(404, "Not found")
    conn.execute("UPDATE papers SET downloads = downloads + 1 WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    path = UPLOAD_DIR / r["stored_name"]
    if not path.exists():
        raise HTTPException(404, "File missing")
    return FileResponse(str(path), filename=r["filename"] or r["stored_name"], media_type="application/pdf")


@app.post("/api/papers")
async def upload_paper(
    title: str = Form(...),
    exam_type: str = Form(...),
    exam_name: str = Form(...),
    subject: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    semester: Optional[str] = Form(None),
    university: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    uploaded_by: Optional[str] = Form("community"),
    file: UploadFile = File(...),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")
    pid = uuid.uuid4().hex
    stored = f"{pid}.pdf"
    dst = UPLOAD_DIR / stored
    with dst.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    conn = db()
    conn.execute("""INSERT INTO papers (id,title,exam_type,exam_name,subject,year,semester,university,filename,stored_name,size,source_url,uploaded_by,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (pid, title, exam_type, exam_name, subject, year, semester, university, file.filename, stored, dst.stat().st_size, source_url, uploaded_by or "community", datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"id": pid, "status": "uploaded"}


@app.post("/api/requests")
async def request_paper(exam_name: str = Form(...), subject: Optional[str] = Form(None), year: Optional[int] = Form(None), note: Optional[str] = Form(None)):
    rid = uuid.uuid4().hex
    conn = db()
    conn.execute("INSERT INTO requests (id,exam_name,subject,year,note,created_at) VALUES (?,?,?,?,?,?)",
        (rid, exam_name, subject, year, note, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"id": rid, "status": "requested"}


@app.get("/api/requests")
async def list_requests():
    conn = db()
    rows = conn.execute("SELECT * FROM requests ORDER BY created_at DESC LIMIT 50").fetchall()
    conn.close()
    return [dict(r) for r in rows]



@app.post("/api/import-url")
async def import_from_url(
    title: str = Form(...),
    exam_type: str = Form(...),
    exam_name: str = Form(...),
    subject: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    semester: Optional[str] = Form(None),
    university: Optional[str] = Form(None),
    source_url: str = Form(...),
    uploaded_by: Optional[str] = Form("community"),
):
    """Fetch a PDF from a public URL and store it in the hub."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as c:
            r = await c.get(source_url)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(400, f"Could not fetch URL: {e}")
    ctype = r.headers.get("content-type", "")
    if "pdf" not in ctype.lower() and not source_url.lower().endswith(".pdf"):
        raise HTTPException(400, "URL does not appear to be a PDF")
    pid = uuid.uuid4().hex
    stored = f"{pid}.pdf"
    dst = UPLOAD_DIR / stored
    dst.write_bytes(r.content)
    conn = db()
    conn.execute("""INSERT INTO papers (id,title,exam_type,exam_name,subject,year,semester,university,filename,stored_name,size,source_url,uploaded_by,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (pid, title, exam_type, exam_name, subject, year, semester, university, source_url.split("/")[-1] or "imported.pdf", stored, dst.stat().st_size, source_url, uploaded_by or "community", datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"id": pid, "status": "imported"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8020, reload=True)
