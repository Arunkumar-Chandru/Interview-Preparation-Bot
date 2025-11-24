# app.py
import os
import uuid
import random
import traceback
from typing import Dict, Any, List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

try:
    import openai
    openai.api_key = OPENAI_API_KEY
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

app = FastAPI()

sessions: Dict[str, Dict[str, Any]] = {}

QUESTION_BANKS: Dict[str, List[str]] = {
    "Java Developer": [
        "What is Java and what are its main features?",
        "Explain the difference between JDK, JRE, and JVM.",
        "What is the difference between == and equals() in Java?",
        "What is inheritance in Java and why is it useful?",
        "Explain polymorphism with an example.",
        "What is encapsulation and how does Java support it?",
        "What is an interface and how is it different from an abstract class?",
        "Explain checked vs unchecked exceptions in Java.",
        "What are Java collections? Name some collection interfaces.",
        "What is the difference between ArrayList and LinkedList?",
        "Explain HashMap and how it works internally (high-level).",
        "What is multithreading and how do you create a thread in Java?",
        "What is synchronization and why is it important?",
        "What is the volatile keyword?",
        "Describe the Java memory model (heap vs stack) briefly.",
        "What is garbage collection and how does it work in Java (high-level)?",
        "What are generics in Java and why are they useful?",
        "Explain the Stream API in Java 8 briefly.",
        "What is a lambda expression in Java?",
        "What is the difference between final, finally, and finalize?",
        "Explain dependency injection and how frameworks like Spring use it.",
        "What is JDBC?",
        "Explain the Singleton pattern and how to implement it safely in Java.",
        "What is REST and how would you build a simple REST service in Java?",
        "What is the difference between process and thread?"
    ],
    "Software Engineer": [
        "Explain the software development lifecycle.",
        "What is OOP and name its principles.",
        "What is unit testing and why is it important?",
        "Explain REST vs SOAP.",
        "What are design patterns? Give an example.",
        "How do you handle version control? (git basics)",
        "What is continuous integration?",
        "Explain time vs space complexity (big-O).",
        "Describe a system design for a URL shortener (high-level).",
        "What is load balancing?",
        "Explain database indexing briefly.",
        "What is eventual consistency?",
        "Describe a cache and when to use it.",
        "What is microservices architecture?",
        "Explain an example of a race condition and how to prevent it.",
        "What is a deadlock?",
        "How do you design for failure in distributed systems?",
        "Explain pagination strategies for APIs.",
        "What is OAuth?",
        "Explain the difference between SQL and NoSQL databases.",
        "What is observability (logs/metrics/traces)?",
        "How do you ensure API backward compatibility?",
        "What is refactoring and when to do it?",
        "Explain feature toggles and their use.",
        "What is a message queue and when to use it?"
    ],
    "Data Analyst": [
        "What is the difference between mean, median, and mode?",
        "What is data cleaning and why is it important?",
        "Explain correlation vs causation.",
        "What is SQL and write a basic SELECT example.",
        "What is normalization in databases?",
        "Explain joins (INNER, LEFT, RIGHT).",
        "What is a pivot table?",
        "What is data visualization and name tools you use.",
        "Explain A/B testing basics.",
        "What is regression analysis?",
        "How do you handle missing data?",
        "What is outlier detection?",
        "What is ETL?",
        "Explain the difference between structured and unstructured data.",
        "What is a time series?",
        "What is PCA (in brief)?",
        "Explain precision and recall.",
        "What is hypothesis testing?",
        "Describe a dashboard you've built.",
        "What is a KPI?",
        "Explain data sampling methods.",
        "What is normalization vs standardization?",
        "What is the role of a data analyst in a business?",
        "What is clustering?",
        "Explain the difference between supervised and unsupervised learning."
    ],
    "Python Developer": [
        "What are Python's key features?",
        "Explain list vs tuple.",
        "What is GIL (Global Interpreter Lock)?",
        "How do you manage dependencies in Python?",
        "What is a decorator?",
        "Explain generators and yield.",
        "What is list comprehension?",
        "How do you handle exceptions in Python?",
        "What are virtual environments and why use them?",
        "Explain the difference between deep copy and shallow copy.",
        "What is a context manager?",
        "What are type hints?",
        "Explain Python's OOP basics.",
        "What is a module and a package?",
        "How to read/write files in Python?",
        "What is the difference between == and is?",
        "Explain the use of __init__.py file.",
        "What is pip and PyPI?",
        "How to optimize Python code performance?",
        "Explain multiprocessing vs threading.",
        "What are dataclasses?",
        "What is pytest?",
        "How to serialize objects (pickle, json)?",
        "Explain HTTP requests in Python (e.g., requests library).",
        "What is Flask vs Django?"
    ],
    "Web Developer": [
        "What is HTML, CSS, and JavaScript?",
        "Explain the box model in CSS.",
        "What is responsive design?",
        "What is the DOM?",
        "Explain event delegation in JS.",
        "What is AJAX?",
        "What are RESTful APIs?",
        "What is CORS and why it matters?",
        "Explain CSS Flexbox.",
        "What is CSS Grid?",
        "What is progressive enhancement?",
        "Explain single-page application (SPA).",
        "What is a service worker?",
        "Explain web accessibility basics.",
        "What is HTTPS and why important?",
        "What are cookies vs localStorage?",
        "Explain frontend build tools (webpack, etc.).",
        "What is cross-site scripting (XSS)?",
        "What is SQL injection?",
        "Explain SEO basics.",
        "What is WebSockets?",
        "What are HTTP status codes (200, 404, 500)?",
        "What is REST vs GraphQL?",
        "Explain progressive web apps (PWA).",
        "What is redirection (301 vs 302)?"
    ]
}

def pick_questions_for_role(role: str, count: int = 5) -> List[str]:
    bank = QUESTION_BANKS.get(role, [])
    if len(bank) >= count:
        return random.sample(bank, count)
    else:
        return [random.choice(bank) for _ in range(count)]


def call_openai_evaluator(question: str, user_answer: str) -> Dict[str, str]:
    """
    Ask the model to grade the user's answer and return:
    {
        verdict: "Correct" / "Partially correct" / "Incorrect",
        short_feedback: "one-line feedback",
        correction: "Simple correct answer or correction in plain words"
    }
    """
    if not OPENAI_AVAILABLE:
        if len(user_answer.strip()) > 20:
            return {
                "verdict": "Partially correct",
                "short_feedback": "You have some correct points but missed details.",
                "correction": "Key idea: give concise definition and main points."
            }
        else:
            return {
                "verdict": "Incorrect",
                "short_feedback": "Short answer — missing key points.",
                "correction": "Try to mention the definition and 2–3 main features."
            }

    prompt = f"""
You are a strict but fair interviewer assistant. I will give you a question and the candidate's answer.
Return a JSON object with three keys: verdict, short_feedback, correction.
- verdict: one of "Correct", "Partially correct", or "Incorrect".
- short_feedback: 1-2 sentence feedback on what was good/missing.
- correction: a single-paragraph, simple concise correct answer that the candidate can learn.

Question: {question}
Candidate answer: {user_answer}

Keep each field short and in plain language.
Return ONLY valid JSON.
"""
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=250
        )
        text = resp.choices[0].message.content.strip()
        import json
        jstart = text.find("{")
        jtext = text[jstart:] if jstart != -1 else text
        data = json.loads(jtext)
        return {
            "verdict": data.get("verdict", "Incorrect"),
            "short_feedback": data.get("short_feedback", ""),
            "correction": data.get("correction", "")
        }
    except Exception:
        return {
            "verdict": "Partially correct",
            "short_feedback": "Couldn't fully evaluate — review key points.",
            "correction": "Main idea: provide definition, example, and why it's useful."
        }


class StartRequest(BaseModel):
    role: str
    num_questions: int = 5  # default 5


class AnswerRequest(BaseModel):
    session_id: str
    user_answer: str


@app.post("/start")
async def start_interview(req: StartRequest):
    role = req.role
    num = req.num_questions if req.num_questions and 1 <= req.num_questions <= 10 else 5
    qs = pick_questions_for_role(role, count=num)
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "role": role,
        "questions": qs,
        "current": 0,
        "answers": []
    }
    return {
        "session_id": session_id,
        "question": qs[0],
        "remaining": num - 1
    }


@app.post("/answer")
async def answer_question(payload: AnswerRequest):
    sid = payload.session_id
    user_answer = payload.user_answer or ""
    if sid not in sessions:
        return JSONResponse({"error": "Invalid session_id"}, status_code=400)

    session = sessions[sid]
    idx = session["current"]
    question = session["questions"][idx]

    eval_result = call_openai_evaluator(question, user_answer)

    session["answers"].append({
        "question": question,
        "user_answer": user_answer,
        "verdict": eval_result["verdict"],
        "feedback": eval_result["short_feedback"],
        "correction": eval_result["correction"]
    })

    session["current"] += 1
    if session["current"] < len(session["questions"]):
        next_q = session["questions"][session["current"]]
        remaining = len(session["questions"]) - session["current"] - 1
        return {
            "verdict": eval_result["verdict"],
            "feedback": eval_result["short_feedback"],
            "correction": eval_result["correction"],
            "next_question": next_q,
            "remaining": remaining,
            "done": False
        }
    else:
        # Finished interview — generate a short summary using OpenAI if available
        summary = "Interview complete."
        if OPENAI_AVAILABLE:
            try:
                summary_prompt = f"""
You are an interviewer. Provide a 3-sentence overall summary of the candidate based on these Q/A pairs.
Candidate role: {session['role']}
Q/A pairs:
"""
                for a in session["answers"]:
                    summary_prompt += f"\nQ: {a['question']}\nA: {a['user_answer']}\nResult: {a['verdict']}\n"
                summary_prompt += "\nKeep it short and constructive."
                resp = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": summary_prompt}],
                    temperature=0.5,
                    max_tokens=150
                )
                summary = resp.choices[0].message.content.strip()
            except Exception:
                summary = "Interview finished. Review answers for improvement."

        log = session["answers"]

        del sessions[sid]
        return {
            "verdict": eval_result["verdict"],
            "feedback": eval_result["short_feedback"],
            "correction": eval_result["correction"],
            "done": True,
            "summary": summary,
            "log": log
        }


#Serve UI (single-file)
@app.get("/", response_class=HTMLResponse)
async def ui():

    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Interview Practice Partner</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        body {
            margin:0; padding:0; height:100vh;
            font-family: Arial, Helvetica, sans-serif;
            background: #0b0c10; color: #c5c6c7;
            display:flex;
        }
        .sidebar {
            width: 260px; background: #1f2833; padding:20px; border-right:2px solid #45a29e;
        }
        .sidebar h3 { color: #66fcf1; margin:0 0 12px 0; }
        label { display:block; margin-top:12px; font-size:14px; }
        select, input[type=number] {
            width:100%; padding:10px; margin-top:6px; border-radius:6px; border:none; background:#0b0c10; color:#c5c6c7;
        }
        button {
            width:100%; padding:10px; margin-top:16px; border-radius:6px; border:none; background:#45a29e; color:#0b0c10; cursor:pointer;
        }
        button:hover { background:#66fcf1; }

        .main {
            flex:1; padding:28px; display:flex; flex-direction:column;
        }
        .title { text-align:center; color:#66fcf1; font-size:20px; margin-bottom:12px; }
        #chatBox {
            flex:1; background:#0b0c10; border:1px solid #45a29e; padding:14px; border-radius:10px; overflow:auto;
        }
        .msg { margin:8px 0; padding:10px; border-radius:8px; max-width:80%; }
        .msg.user { background:#111; color:#c5c6c7; margin-left:auto; text-align:right; }
        .msg.bot { background:#092; color:#0b0c10; background:#142; color:#c7ffee; margin-right:auto; text-align:left; }
        .controls { display:flex; gap:8px; margin-top:12px; }
        .controls input[type=text] { flex:1; padding:12px; border-radius:6px; border:none; background:#1f2833; color:#c5c6c7; }
        .controls button { padding:10px 16px; border-radius:6px; border:none; background:#45a29e; color:#0b0c10; cursor:pointer; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>Interview Setup</h3>
        <label for="role">Role</label>
        <select id="role">
            <option>Java Developer</option>
            <option>Software Engineer</option>
            <option>Data Analyst</option>
            <option>Python Developer</option>
            <option>Web Developer</option>
        </select>

        <label for="num">Number of Questions (1-10)</label>
        <input id="num" type="number" min="1" max="10" value="5" />

        <button id="startBtn">Start Interview</button>

        <hr style="margin-top:18px;border:0;border-top:1px solid #223;">
        <div style="font-size:13px;color:#9fb8b0;margin-top:10px;">
            <strong>Tip:</strong> Give concise answers. The bot will tell you if your answer is correct and show a simple correction when needed.
        </div>
        <div style="margin-top:8px;color:#9fb8b0;font-size:12px;">
            Image: <br/><small style="color:#7fbeb0">local demo image shown to developer</small>
            <div style="margin-top:8px;">
                <img src="/static/placeholder.png" alt="placeholder" style="width:100%; border-radius:6px; opacity:0.9;">
            </div>
        </div>
    </div>

    <div class="main">
        <div class="title">💬 Interview Practice Partner</div>

        <div id="chatBox"></div>

        <div class="controls">
            <input id="answerInput" type="text" placeholder="Type your answer here..." />
            <button id="sendBtn">Send</button>
        </div>

        <div style="margin-top:8px; font-size:13px; color:#99bfb6">
            <span id="sessionInfo"></span>
        </div>
    </div>

<script>
let sessionId = null;
let currentQuestion = null;

function appendUser(text) {
    const box = document.getElementById('chatBox');
    const div = document.createElement('div');
    div.className = 'msg user';
    div.innerHTML = `<strong>You:</strong> ${escapeHtml(text)}`;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function appendBot(text) {
    const box = document.getElementById('chatBox');
    const div = document.createElement('div');
    div.className = 'msg bot';
    div.innerHTML = `<strong>Bot:</strong> ${escapeHtml(text)}`;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function escapeHtml(unsafe) {
    return unsafe
         .replaceAll('&', '&amp;')
         .replaceAll('<', '&lt;')
         .replaceAll('>', '&gt;');
}

document.getElementById('startBtn').addEventListener('click', async () => {
    const role = document.getElementById('role').value;
    const num = parseInt(document.getElementById('num').value) || 5;
    // clear chat
    document.getElementById('chatBox').innerHTML = '';
    appendBot(`Starting interview for ${role} (${num} questions)...`);

    const res = await fetch('/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ role: role, num_questions: num })
    });
    const data = await res.json();
    sessionId = data.session_id;
    currentQuestion = data.question;
    document.getElementById('sessionInfo').textContent = `Session: ${sessionId}`;
    appendBot(currentQuestion);
});

document.getElementById('sendBtn').addEventListener('click', async () => {
    const val = document.getElementById('answerInput').value.trim();
    if (!val || !sessionId) return;
    appendUser(val);
    document.getElementById('answerInput').value = '';
    appendBot('Checking answer...');
    try {
        const res = await fetch('/answer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ session_id: sessionId, user_answer: val })
        });
        const data = await res.json();
        // remove the 'Checking answer...' last bot message
        const box = document.getElementById('chatBox');
        // remove last bot 'Checking answer...' by finding last bot class with that text
        let nodes = box.querySelectorAll('.msg.bot');
        if (nodes.length) {
            let last = nodes[nodes.length - 1];
            if (last && last.textContent.includes('Checking answer')) {
                last.remove();
            }
        }

        appendBot(`Verdict: ${data.verdict}`);
        if (data.feedback) appendBot(`Feedback: ${data.feedback}`);
        if (data.verdict !== 'Correct' && data.correction) appendBot(`Correction: ${data.correction}`);

        if (data.done) {
            appendBot("Interview complete.");
            if (data.summary) appendBot(`Summary: ${data.summary}`);
            // optional: show log
            console.log('Interview log:', data.log);
            sessionId = null;
            currentQuestion = null;
            document.getElementById('sessionInfo').textContent = '';
        } else {
            // next question
            currentQuestion = data.next_question;
            appendBot(currentQuestion);
        }
    } catch (err) {
        appendBot('Error connecting to server.');
        console.error(err);
    }
});

// allow enter to send
document.getElementById('answerInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('sendBtn').click();
    }
});
</script>
</body>
</html>
    """, media_type="text/html")

import io, base64
from fastapi.responses import Response

UPLOADED_IMAGE_PATH = "/mnt/data/WhatsApp Image 2025-11-23 at 11.17.45_8fdc28b3.jpg"

@app.get("/static/placeholder.png")
def serve_placeholder():

    if os.path.exists(UPLOADED_IMAGE_PATH):
        return FileResponse(UPLOADED_IMAGE_PATH, media_type="image/jpeg")

    png_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAIAAAoA"
        "AYq3Y+0AAAAASUVORK5CYII="
    )
    png = base64.b64decode(png_base64)
    return Response(content=png, media_type="image/png")
