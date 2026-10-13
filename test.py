import main
from fastapi.testclient import TestClient
main.get_transcript = lambda vid: "This lecture explains recursion. A function calls itself. Base case stops it."
c = TestClient(main.app); P = lambda u, b: c.post("/api/" + u, json=b).json()
assert c.get("/").status_code == 200
d = P("study", {"topic": "Recursion"}); assert d["flashcards"] and d["quiz"][0]["options"] and "error" not in d; print("study OK")
d = P("youtube", {"url": "https://youtu.be/dQw4w9WgXcQ"}); assert d["summary"]; print("youtube OK")
assert "error" in P("youtube", {"url": "hello"}); print("youtube bad-url handled OK")
d = P("research", {"topic": "Machine learning", "words": 200}); assert d["steps"] and c.get("/reports/" + d["file"]).status_code == 200; print("research OK")
d = P("assignment", {"topic": "OS", "questions": ["What is a process?", "What is a thread?"]}); assert len(d["answers"]) == 2 and c.get("/reports/" + d["file"]).status_code == 200; print("assignment OK")
t = "Make assignment on DBMS\n1. What is a primary key?\n2. What is normalization?\nAlso summarize https://youtu.be/dQw4w9WgXcQ and give flashcards to study"
d = P("orchestrate", {"task": t}); print([o["agent"] for o in d["outputs"]], d["log"]); assert len(d["outputs"]) >= 3 and d["note"]; print("orchestrator OK")
# bad key / API error must not crash (500)
class R:  status_code = 401
R.json = lambda self: {"error": {"message": "Invalid API Key"}}
main.KEY = "bad"; main.httpx.post = lambda *a, **k: R()
for u, b in [("research", {"topic": "AI"}), ("study", {"topic": "AI"}), ("assignment", {"topic": "x", "questions": ["q?"]}), ("youtube", {"url": "https://youtu.be/dQw4w9WgXcQ"})]:
    r = c.post("/api/" + u, json=b); assert r.status_code == 200, u; print(u, "->", str(r.json())[:90])
assert c.post("/api/orchestrate", json={"task": "study recursion"}).status_code == 200; print("error handling OK")
# Groq model fallback: 1st model fails, 2nd works
calls = []
class G:
    def __init__(s, ok): s.ok = ok; s.status_code = 200 if ok else 400
    def json(s): return {"choices": [{"message": {"content": "hello from groq"}}]} if s.ok else {"error": {"message": "model decommissioned"}}
def fake(url, **k): calls.append(k["json"]["model"]); return G(len(calls) > 1)
main.httpx.post = fake; main.KEY = "gsk_test"
assert main.llm("s", "u") == "hello from groq" and len(calls) == 2; print("groq fallback OK", calls)
