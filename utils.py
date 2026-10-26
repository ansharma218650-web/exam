"""Storage + helper functions. All data lives in JSON/CSV files inside /data.

Students: every function that touches results or progress takes a `user` slug.
An empty slug ("") is the shared "Guest" profile and uses the original files, so
data from earlier versions keeps working.
"""
import csv
import hashlib
import io
import json
import re
import shutil
import uuid
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

BASE = Path(__file__).parent / "data"
PRACTICE_DIR = BASE / "practice"        # data/practice/<subject>.json
TEST_DIR = BASE / "test_series"         # data/test_series/<series>/<test>.json
STUDENTS_DIR = BASE / "students"        # data/students/<student>/results.csv + progress.json
NOTES_DIR = BASE / "notes"              # data/notes/index.json + data/notes/files/<id>.pdf
SAMPLE_DIR = Path(__file__).parent / "sample_data"
for _d in (PRACTICE_DIR, TEST_DIR, NOTES_DIR / "files"):
    _d.mkdir(parents=True, exist_ok=True)


# ---------- basic helpers ----------
def slugify(text: str) -> str:
    s = re.sub(r"[^\w]+", "_", text.strip().lower()).strip("_")
    return s or "untitled"


def pretty(slug: str) -> str:
    return slug.replace("_", " ").title()


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def qid(q: dict) -> str:
    """Stable id for a question (falls back to a hash for hand-written JSON without ids)."""
    return str(q.get("id") or hashlib.md5(q.get("question", "").encode("utf-8")).hexdigest()[:8])


def _norm_text(q: dict) -> str:
    return re.sub(r"\s+", " ", str(q.get("question", ""))).strip().lower()


def _dedupe(existing: list, new: list) -> list:
    seen = {_norm_text(q) for q in existing}
    out = []
    for q in new:
        k = _norm_text(q)
        if k not in seen:
            seen.add(k)
            out.append(q)
    return out


# ---------- question validation / parsing ----------
def normalize_question(q: dict) -> dict:
    text = str(q.get("question", "")).strip()
    opts = [str(o).strip() for o in q.get("options", []) if str(o).strip()]
    if not text:
        raise ValueError("question text is empty")
    if len(opts) < 2:
        raise ValueError("at least 2 options are required")
    ans = q.get("answer")
    if isinstance(ans, str):
        a = ans.strip().upper()
        ans = ord(a) - 65 if (len(a) == 1 and a.isalpha()) else int(a)
    if not isinstance(ans, int) or not 0 <= ans < len(opts):
        raise ValueError("answer must be a letter (A-D) or a valid 0-based index")
    return {
        "id": q.get("id") or uuid.uuid4().hex[:8],
        "question": text,
        "options": opts,
        "answer": ans,
        "explanation": str(q.get("explanation", "")).strip(),
    }


def parse_upload(filename: str, raw: bytes):
    """Return (questions, errors) from a .json or .csv upload."""
    questions, errors = [], []
    rows = []
    try:
        if filename.lower().endswith(".json"):
            data = json.loads(raw.decode("utf-8-sig"))
            rows = data["questions"] if isinstance(data, dict) else data
        else:
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
            for r in reader:
                r = {(k or "").strip().lower(): (v or "") for k, v in r.items()}
                rows.append({
                    "question": r.get("question", ""),
                    "options": [r.get(f"option_{c}", "") for c in "abcd"],
                    "answer": r.get("answer", ""),
                    "explanation": r.get("explanation", ""),
                })
    except Exception as e:
        return [], [f"Could not read file: {e}"]
    for n, row in enumerate(rows, 1):
        try:
            questions.append(normalize_question(row))
        except Exception as e:
            errors.append(f"Row {n}: {e}")
    return questions, errors


# ---------- practice ----------
def list_subjects():
    out = []
    for p in PRACTICE_DIR.glob("*.json"):
        out.append((p.stem, _read(p).get("subject", pretty(p.stem))))
    return sorted(out, key=lambda x: x[1])


def load_practice(slug: str) -> dict:
    return _read(PRACTICE_DIR / f"{slug}.json")


def add_practice(subject_name: str, questions: list) -> int:
    """Add questions, skipping duplicates. Returns how many were actually added."""
    path = PRACTICE_DIR / f"{slugify(subject_name)}.json"
    data = _read(path) if path.exists() else {"subject": subject_name.strip(), "questions": []}
    fresh = _dedupe(data["questions"], questions)
    data["questions"].extend(fresh)
    _write(path, data)
    return len(fresh)


# ---------- test series ----------
def list_series():
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(p.name for p in TEST_DIR.iterdir() if p.is_dir())


def list_tests(series: str):
    out = []
    for p in sorted((TEST_DIR / series).glob("*.json")):
        out.append((p.stem, _read(p).get("title", pretty(p.stem))))
    return out


def load_test(series: str, test: str) -> dict:
    return _read(TEST_DIR / series / f"{test}.json")


def add_test(series_name, test_name, questions, settings=None) -> int:
    """Add questions, skipping duplicates. Returns how many were actually added."""
    path = TEST_DIR / slugify(series_name) / f"{slugify(test_name)}.json"
    if path.exists():
        data = _read(path)
    else:
        s = settings or {}
        data = {
            "title": test_name.strip(),
            "duration_minutes": s.get("duration_minutes", 30),
            "marks_per_question": s.get("marks_per_question", 1),
            "negative_marks": s.get("negative_marks", 0),
            "questions": [],
        }
    fresh = _dedupe(data["questions"], questions)
    data["questions"].extend(fresh)
    _write(path, data)
    return len(fresh)


# ---------- notes & concepts (PDF files or typed notes) ----------
def _notes_index() -> list:
    f = NOTES_DIR / "index.json"
    if not f.exists():
        return []
    try:
        return _read(f).get("notes", [])
    except Exception:
        return []


def list_notes() -> list:
    """All notes, newest first."""
    return sorted(_notes_index(), key=lambda n: n.get("added", ""), reverse=True)


def add_note(title: str, subject: str, description: str = "", pdf_bytes: bytes = None, text: str = None) -> dict:
    """Save a PDF note (pdf_bytes) or a typed note (text). Raises ValueError on bad input."""
    title, subject = title.strip(), (subject or "General").strip() or "General"
    if not title:
        raise ValueError("please give the note a title")
    nid = uuid.uuid4().hex[:8]
    entry = {"id": nid, "title": title, "subject": subject, "description": description.strip(),
             "added": datetime.now().strftime("%Y-%m-%d %H:%M")}
    if pdf_bytes is not None:
        if not pdf_bytes.lstrip()[:5] == b"%PDF-":
            raise ValueError("that file does not look like a valid PDF")
        (NOTES_DIR / "files").mkdir(parents=True, exist_ok=True)
        (NOTES_DIR / "files" / f"{nid}.pdf").write_bytes(pdf_bytes)
        entry.update(kind="pdf", size=len(pdf_bytes))
    else:
        if not (text or "").strip():
            raise ValueError("the note is empty")
        entry.update(kind="text", text=text.strip(), size=len(text.encode("utf-8")))
    _write(NOTES_DIR / "index.json", {"notes": _notes_index() + [entry]})
    return entry


def read_note_file(nid: str) -> bytes:
    p = NOTES_DIR / "files" / f"{nid}.pdf"
    return p.read_bytes() if p.exists() else b""


def delete_note(nid: str) -> None:
    keep = [n for n in _notes_index() if n["id"] != nid]
    _write(NOTES_DIR / "index.json", {"notes": keep})
    (NOTES_DIR / "files" / f"{nid}.pdf").unlink(missing_ok=True)


# ---------- sample content ----------
def has_content() -> bool:
    return bool(list_subjects() or list_series())


def seed_sample() -> int:
    """Copy demo questions from /sample_data into /data (never overwrites). Returns files copied."""
    copied = 0
    if not SAMPLE_DIR.exists():
        return 0
    for src in SAMPLE_DIR.rglob("*.json"):
        dst = BASE / src.relative_to(SAMPLE_DIR)
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
    return copied


# ---------- generic (used by the admin "Manage" tab) ----------
def all_sets():
    """[(label, path)] for every practice subject and every test."""
    sets = []
    for slug, name in list_subjects():
        sets.append((f"Practice › {name}", PRACTICE_DIR / f"{slug}.json"))
    for s in list_series():
        for slug, title in list_tests(s):
            sets.append((f"Test › {pretty(s)} › {title}", TEST_DIR / s / f"{slug}.json"))
    return sets


def read_set(path):
    return _read(Path(path))


def write_set(path, data):
    _write(Path(path), data)


def delete_set(path):
    p = Path(path)
    p.unlink(missing_ok=True)
    if p.parent != PRACTICE_DIR and p.parent.exists() and not any(p.parent.iterdir()):
        p.parent.rmdir()


def backup_zip() -> bytes:
    """Everything in /data (questions, results, progress) as one ZIP."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in BASE.rglob("*"):
            if p.is_file() and p.name != ".gitkeep":
                z.write(p, p.relative_to(BASE.parent).as_posix())
    return buf.getvalue()


# ---------- per-student files ----------
def _user_dir(user: str) -> Path:
    return BASE if not user else STUDENTS_DIR / user


def results_file(user: str = "") -> Path:
    return _user_dir(user) / "results.csv"


def progress_file(user: str = "") -> Path:
    return _user_dir(user) / "progress.json"


# ---------- results history ----------
FIELDS = ["time", "series", "test", "score", "max_score", "correct", "wrong", "unattempted"]


def save_result(row: dict, user: str = "") -> None:
    f = results_file(user)
    f.parent.mkdir(parents=True, exist_ok=True)
    new = not f.exists()
    with f.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), **row})


def load_results(user: str = ""):
    f = results_file(user)
    if not f.exists():
        return []
    with f.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))[::-1]


# ---------- progress: streaks, mistakes, bookmarks, subject accuracy ----------
def pkey(slug: str, q: dict) -> str:
    return f"p|{slug}|{qid(q)}"


def tkey(series: str, test: str, q: dict) -> str:
    return f"t|{series}|{test}|{qid(q)}"


def _empty_progress() -> dict:
    return {"q": {}, "bm": [], "days": {}, "groups": {}, "goal": 20}


def load_progress(user: str = "") -> dict:
    f = progress_file(user)
    p = _empty_progress()
    if f.exists():
        try:
            p.update(_read(f))
        except Exception:
            pass
    return p


def _save_progress(user: str, p: dict) -> None:
    _write(progress_file(user), p)


def record_answers(user: str, items) -> None:
    """items: [(question_key, was_correct, group_label)] - saved in one write."""
    items = list(items)
    if not items:
        return
    p = load_progress(user)
    today = date.today().isoformat()
    for key, ok, group in items:
        e = p["q"].setdefault(key, {"a": 0, "c": 0})
        e["a"] += 1
        e["c"] += int(ok)
        e["last"] = bool(ok)
        e["t"] = today
        g = p["groups"].setdefault(group, {"a": 0, "c": 0})
        g["a"] += 1
        g["c"] += int(ok)
    p["days"][today] = p["days"].get(today, 0) + len(items)
    _save_progress(user, p)


def toggle_bookmark(user: str, key: str) -> bool:
    p = load_progress(user)
    if key in p["bm"]:
        p["bm"].remove(key)
        saved = False
    else:
        p["bm"].append(key)
        saved = True
    _save_progress(user, p)
    return saved


def set_goal(user: str, goal: int) -> None:
    p = load_progress(user)
    p["goal"] = int(goal)
    _save_progress(user, p)


def today_count(p: dict) -> int:
    return int(p["days"].get(date.today().isoformat(), 0))


def streak(p: dict) -> int:
    """Consecutive days with practice, ending today (or yesterday if today has none yet)."""
    d = date.today()
    if not p["days"].get(d.isoformat()):
        d -= timedelta(days=1)
    n = 0
    while p["days"].get(d.isoformat()):
        n += 1
        d -= timedelta(days=1)
    return n


def mistake_keys(p: dict) -> list:
    return [k for k, v in p["q"].items() if v.get("last") is False]


def resolve_key(key: str):
    """Question key -> question dict (with _key/_group) or None if it no longer exists."""
    try:
        parts = key.split("|")
        if parts[0] == "p":
            d = load_practice(parts[1])
            group = d.get("subject", pretty(parts[1]))
            qs = d["questions"]
            target = parts[2]
        else:
            d = load_test(parts[1], parts[2])
            group, qs, target = "Mock tests", d["questions"], parts[3]
        for q in qs:
            if qid(q) == target:
                return {**q, "_key": key, "_group": group}
    except Exception:
        return None
    return None


def questions_for(keys) -> list:
    return [q for q in (resolve_key(k) for k in keys) if q]


def subject_questions(slug: str) -> list:
    d = load_practice(slug)
    group = d.get("subject", pretty(slug))
    return [{**q, "_key": pkey(slug, q), "_group": group} for q in d["questions"]]


def list_students():
    """[(slug, display_name)] - 'Guest' (shared profile) first if it has data."""
    out = []
    if results_file("").exists() or progress_file("").exists():
        out.append(("", "Guest"))
    if STUDENTS_DIR.exists():
        out += [(p.name, pretty(p.name)) for p in sorted(STUDENTS_DIR.iterdir()) if p.is_dir()]
    return out
