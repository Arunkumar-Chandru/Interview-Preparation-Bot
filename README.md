# Interview Practice Partner

A web-based interview practice assistant that allows users to simulate mock interviews for different technical roles. The bot asks questions, evaluates answers using OpenAI’s GPT-4o-mini (or a fallback evaluator), and provides feedback and corrections in real time.

---

## Features

- Role-based interview questions (Java Developer, Software Engineer, Python Developer, Data Analyst, Web Developer)
- Configurable number of questions per session (1–10)
- AI-powered evaluation of answers
- Instant feedback, verdict, and correction for incorrect or partially correct answers
- Summary of performance at the end of each session
- Simple, interactive web UI

---

## Setup Instructions

### 1.Create and activate a virtual environment
python -m venv venv
**Linux/macOS**
source venv/bin/activate
**Windows**
venv\Scripts\activate
## 2. Install dependencies

pip install -r requirements.txt

## 3. Add OpenAI API Key

Create a .env file in the project root:

OPENAI_API_KEY=your_openai_api_key_here

## 4. Run the application

uvicorn app:app --reload

By default, the app will be available at http://127.0.0.1:8000/.

## Usage

1.Select a role and number of questions.

2.Click Start Interview.

3.Type answers in the chat and click Send (or press Enter).

4.Receive feedback, corrections, and next questions.

5.View session summary after all questions.

## Architecture

**-Frontend:** Single-page UI, vanilla JS/CSS, communicates with /start and /answer.

**-Backend:** FastAPI handles requests, in-memory session storage, serves static files.

**-Interview Agent:** Generates questions from curated banks, evaluates answers via GPT-4o-mini or fallback.

**-Evaluation Logic:** call_openai_system() grades answers; fallback provides basic feedback.

**-Static Assets:** Placeholder images via FileResponse.

## Design Decisions

**-In-memory sessions**: Lightweight, simple demo; DB/Redis recommended for production.

**-Curated question banks**: 25 questions per role, random sampling for variety.

**-Fallback evaluator**: Works without OpenAI API.

**-Frontend simplicity**: Minimal dependencies, easy customization.

**-Extensibility**: Easy to add roles, questions, or alternative LLMs.

## Future Improvements

-Add voice input/output

-Persist sessions for multi-user support

-Analytics dashboard for performance tracking

-Dynamic question generation via GPT models
