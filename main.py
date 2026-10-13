import os, re, json, time, datetime, httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Hack Your College Life")
os.makedirs("reports", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")   # serves me.png (your logo)
def load_env():                       # reads GROQ_API_KEY from .env file (no extra package)
    if os.path.exists(".env"):
        for l in open(".env", encoding="utf-8"):
            if "=" in l and not l.lstrip().startswith("#"):
                k, v = l.strip().split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip("\"'"))
load_env()
KEY = (os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY", "")).strip()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELS = [m for m in [os.getenv("GROQ_MODEL"), "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-20b"] if m]   # auto-fallback list

def llm(system, user, mock="", max_tokens=2500, json_mode=False):
    """Brain of every agent (Groq). No key -> DEMO MODE returns `mock`."""
    if not KEY: return mock or f"[DEMO MODE] {user[:200]}"
    last = ""
    for m in MODELS:                                   # model band/limit ho to next model try
        body = {"model": m, "max_tokens": max_tokens, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if json_mode: body["response_format"] = {"type": "json_object"}
        for _ in range(2):                             # 429 rate-limit -> wait & retry once
            r = httpx.post(GROQ_URL, timeout=90, headers={"Authorization": f"Bearer {KEY}"}, json=body)
            d = r.json()
            if "choices" in d: return d["choices"][0]["message"]["content"]
            last = d.get("error", d)
            if r.status_code == 429: time.sleep(3); continue
            break
        if r.status_code in (401, 403): break          # bad key: other models won't help
    raise RuntimeError(last)

def safe(fn, *a):
    try: return fn(*a)
    except Exception as e: return {"error": f"AI call fail hua: {e}"}

def jparse(t):
    return json.loads(re.search(r"[\[{].*[\]}]", t, re.S).group())

def save(prefix, text):
    name = re.sub(r"\W+", "_", prefix)[:25] + "_" + datetime.datetime.now().strftime("%H%M%S") + ".md"
    open(f"reports/{name}", "w", encoding="utf-8").write(text)
    return name

# ============ AGENT 1: STUDY BUDDY (summary + flashcards + quiz) ============
def study_agent(topic):
    mock = json.dumps({"summary": f"**{topic}** - demo summary. Real AI key lagao to full notes milenge.",
        "flashcards": [{"q": f"{topic}: concept {i}?", "a": f"Demo answer {i}"} for i in range(1, 7)],
        "quiz": [{"q": f"Demo MCQ {i} on {topic}?", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": i % 4, "why": "Demo explanation"} for i in range(1, 5)]})
    sys = ('You are a study buddy for 1st year college students. Return ONLY JSON: {"summary":"short markdown notes","flashcards":[{"q":"","a":""}] (8 items),'
           '"quiz":[{"q":"","options":["","","",""],"answer":0-3 index,"why":""}] (5 items)}')
    try: return jparse(llm(sys, f"Topic: {topic}", mock, 3500, True))
    except Exception as e: return {"error": f"Study agent failed: {e}"}

# ============ AGENT 2: YOUTUBE SUMMARIZER ============
def get_transcript(vid):
    from youtube_transcript_api import YouTubeTranscriptApi as Y
    if hasattr(Y, "get_transcript"): parts = Y.get_transcript(vid)           # old versions
    else: parts = next(iter(Y().list(vid))).fetch()                           # v1.x
    return " ".join(p.text if hasattr(p, "text") else p["text"] for p in parts)

def yt_agent(url, transcript=""):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([\w-]{11})", url or "")
    vid = m.group(1) if m else ""
    if not vid and not transcript: return {"error": "Valid YouTube URL daalo."}
    title = ""
    try: title = httpx.get("https://www.youtube.com/oembed", params={"url": url, "format": "json"}, timeout=8).json()["title"]
    except Exception: pass
    if not transcript:
        try: transcript = get_transcript(vid)
        except Exception: return {"error": "Is video ke captions nahi mile. Transcript paste karke try karo.", "video_id": vid, "title": title}
    mock = "## Demo Summary\n- Point 1 from the video\n- Point 2 from the video\n\n**Takeaway:** real key lagao to asli summary milegi."
    s = llm("Summarize this lecture/video transcript for a college student: TL;DR (2 lines), 5 key points, 3 things to remember. Markdown.", transcript[:15000], mock, 1500)
    return {"summary": s, "video_id": vid, "title": title, "chars": len(transcript)}

# ============ AGENT 3: RESEARCH ASSISTANT ============
def wiki(topic):
    try:
        h = {"User-Agent": "CollegeAgentDemo/1.0"}; out = []
        s = httpx.get("https://en.wikipedia.org/w/api.php", headers=h, timeout=15, params={"action": "query", "list": "search", "srsearch": topic, "format": "json", "srlimit": 3}).json()
        for hit in s["query"]["search"]:
            e = httpx.get("https://en.wikipedia.org/w/api.php", headers=h, timeout=15, params={"action": "query", "prop": "extracts", "exintro": 1, "explaintext": 1, "titles": hit["title"], "format": "json"}).json()
            out.append({"title": hit["title"], "text": list(e["query"]["pages"].values())[0].get("extract", "")[:1800], "url": "https://en.wikipedia.org/wiki/" + hit["title"].replace(" ", "_")})
        return out
    except Exception: return []

def research_agent(topic, words=300):
    words = max(50, min(int(words or 300), 1500))
    steps = [f"Searching the web for '{topic}'"]
    srcs = wiki(topic)
    steps.append(f"Read {len(srcs)} sources" if srcs else "No web access - using AI knowledge")
    ctx = "\n\n".join(f"## {s['title']}\n{s['text']}" for s in srcs)
    steps.append(f"Writing ~{words} word summary")
    rep = llm(f"You are a research assistant. Write a clear markdown summary of about {words} words (headings + bullets ok).", f"Topic: {topic}\n\nSources:\n{ctx}",
              f"## {topic}\nDemo research summary (~{words} words target). Real key lagao to asli report milegi.", words * 2 + 400)
    rep += "\n\n---\n**Sources**\n" + "\n".join(f"- {s['url']}" for s in srcs)
    f = save("research_" + topic, rep); steps.append(f"Saved report: {f}")
    return {"result": rep, "steps": steps, "file": f}

# ============ AGENT 4: ASSIGNMENT WRITER ============
def assignment_agent(topic, questions):
    qs = [q.strip() for q in questions if q.strip()]
    if not qs: return {"error": "Kam se kam 1 question daalo."}
    answers = []
    for q in qs[:15]:
        a = llm(f"You are a diligent student writing a neat assignment on '{topic}'. Answer in 80-150 words, simple English, point-wise if suitable.", q, f"Demo answer for: {q}")
        answers.append({"q": q, "a": a})
    doc = f"# Assignment: {topic}\n\n" + "\n\n".join(f"## Q{i+1}. {x['q']}\n{x['a']}" for i, x in enumerate(answers))
    return {"answers": answers, "file": save("assignment_" + topic, doc)}

# ============ AGENT 5: ORCHESTRATOR (Dean) ============
def plan_steps(task):
    if KEY:
        try:
            p = jparse(llm('You are the Dean orchestrating agents: study, youtube, research, assignment. Return ONLY a JSON list of steps like '
                '[{"agent":"study","topic":""},{"agent":"youtube","url":""},{"agent":"research","topic":"","words":300},{"agent":"assignment","topic":"","questions":[""]}]. Use only needed agents.', task))
            if isinstance(p, list) and p: return p
        except Exception: pass
    t, steps = task.lower(), []                                    # keyword fallback
    url = re.search(r"https?://\S*(?:youtu\.be|youtube\.com)\S*", task)
    topic = re.sub(r"https?://\S+", "", task).strip()[:80] or task[:80]
    if url: steps.append({"agent": "youtube", "url": url.group()})
    qs = [l.strip() for l in task.splitlines() if l.strip().endswith("?") or re.match(r"\d+[.)]", l.strip())]
    if "assignment" in t or qs: steps.append({"agent": "assignment", "topic": topic, "questions": qs or [topic]})
    if any(k in t for k in ["research", "report", "summary of", "find out"]): steps.append({"agent": "research", "topic": topic, "words": 250})
    if any(k in t for k in ["flashcard", "quiz", "study", "learn", "explain", "exam"]) or not steps: steps.append({"agent": "study", "topic": topic})
    return steps

def run_step(s):
    a = s.get("agent")
    return {"youtube": lambda: yt_agent(s.get("url", ""), s.get("transcript", "")),
            "research": lambda: research_agent(s.get("topic", ""), s.get("words", 300)),
            "assignment": lambda: assignment_agent(s.get("topic", ""), s.get("questions", [])),
            "study": lambda: study_agent(s.get("topic", ""))}.get(a, lambda: {"error": f"Unknown agent {a}"})()

def orchestrate(task):
    plan, outs, log = plan_steps(task), [], []
    log.append("Dean planned: " + " -> ".join(s.get("agent", "?") for s in plan))
    for s in plan:
        r = safe(run_step, s)
        if "error" in r and s.get("agent") != "youtube": log.append(f"{s['agent']} failed, retrying once"); r = safe(run_step, s)   # supervise: retry
        log.append(f"{s.get('agent')}: " + ("FAILED - " + r["error"] if "error" in r else "done"))
        outs.append({"agent": s.get("agent"), "data": r})
    ok = sum("error" not in o["data"] for o in outs)
    note = llm("You are the Dean supervising AI agents. In 3 short lines: what got done, one quality tip, one next step. Hinglish ok.",
               f"Task: {task}\nAgents run: {[o['agent'] for o in outs]}\nSuccessful: {ok}/{len(outs)}",
               f"All {ok}/{len(outs)} agents ne kaam kar diya. Tip: output ko apne words me revise karo. Next: flashcards se revise karo!")
    return {"plan": plan, "log": log, "outputs": outs, "note": note}

# ============ API ============
class Study(BaseModel): topic: str
class YT(BaseModel): url: str = ""; transcript: str = ""
class Res(BaseModel): topic: str; words: int = 300
class Asg(BaseModel): topic: str; questions: list[str]
class Orch(BaseModel): task: str

@app.post("/api/study")
def _s(b: Study): return study_agent(b.topic)
@app.post("/api/youtube")
def _y(b: YT): return safe(yt_agent, b.url, b.transcript)
@app.post("/api/research")
def _r(b: Res): return safe(research_agent, b.topic, b.words)
@app.post("/api/assignment")
def _a(b: Asg): return safe(assignment_agent, b.topic, b.questions)
@app.post("/api/orchestrate")
def _o(b: Orch): return safe(orchestrate, b.task)
@app.get("/reports/{name}")
def _f(name: str): return FileResponse(f"reports/{os.path.basename(name)}", filename=name)
@app.get("/")
def home(): return FileResponse("static/index.html")
