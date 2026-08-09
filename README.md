🎯 AI Interview Agent

Build the interviewer, not the interview.

An adaptive technical interviewing platform for AI engineeringcandidates. Instead of following a fixed questionnaire, the systemtracks candidate performance, curriculum coverage, question history,difficulty, weak areas and answer quality to select the next questionand produce a structured final report.

🔗 Live Project

Resource                            URL

GitHub                              https://github.com/VanshTyagi99/AI-Interview-Agent

Live Frontend                       https://ai-interview-agent-iota-two.vercel.app

Live Backend                        https://ai-interview-agent-api-svqe.onrender.com

Health Check                        https://ai-interview-agent-api-svqe.onrender.com/health

📌 Problem

Traditional technical interviews often behave like staticquestionnaires:

Question 1 → Question 2 → Question 3 → ... → Final Score

This creates several problems:

Strong and weak candidates may receive similar questions.

Difficulty does not respond to performance.

Weak concepts are not automatically revisited.

Topic/curriculum coverage is difficult to control.

Keyword-only scoring can reward technically related but irrelevantanswers.

Final feedback is often generic.

The AI Interview Agent turns the interview into an adaptive assessmentloop.

💡 Solution

The system continuously maintains:

Candidate profile

Session ID

Current question

Current topic

Current difficulty

Curriculum day

Asked questions

Follow-up count

Answer history

Topic scores

Curriculum coverage

Final performance

Interview flow

Candidate Profile
       ↓
Create Session
       ↓
Select Curriculum Day
       ↓
Select Difficulty
       ↓
Ask Question
       ↓
Candidate Answer
       ↓
Phase 3.5 Evaluation
       ↓
┌───────────────────────┐
│ Score + Intent + Depth│
└───────────┬───────────┘
            ↓
   Adaptive Decision
      ↙          ↘
 Strong          Weak
   ↓               ↓
Harder /       Easier /
deeper         same-area
question       reinforcement
      ↘          ↙
       Next Question
            ↓
       Repeat
            ↓
       Final Report

🏗️ Architecture

┌──────────────────────────────┐
│          Candidate           │
│ Profile + Technical Answer   │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│          FRONTEND            │
│ HTML + CSS + JavaScript      │
│                              │
│ Candidate setup              │
│ Interview UI                 │
│ Question / Answer UI         │
│ Progress                     │
│ Final report                 │
└──────────────┬───────────────┘
               │ HTTPS / JSON
               ↓
┌──────────────────────────────┐
│        FASTAPI BACKEND       │
│                              │
│ Session management           │
│ Curriculum selection         │
│ Adaptive difficulty          │
│ Follow-up selection          │
│ Deterministic evaluation     │
│ Final result generation      │
│ History / result APIs        │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│       Project Data           │
│ Curriculum / Candidates      │
│ Sessions / Interview History │
└──────────────────────────────┘

Deployment

Vercel Frontend
      │ HTTPS
      ▼
Render FastAPI Backend
      │
      ▼
Interview + Evaluation Engine

🧩 Technology Stack

Frontend

HTML5

CSS3

Vanilla JavaScript

Fetch API

Browser session state

Backend

Python

FastAPI

Pydantic

Uvicorn

Data / Intelligence

Curriculum JSON

Candidate/session data

Deterministic rubrics

Question-specific intent rules

Adaptive selection logic

Deployment

GitHub

Vercel

Render

🎤 Core Interview Engine

The current interview configuration uses:

8 total questions

Minimum 4 curriculum days

Easy / Medium / Hard difficulty

Topic tracking

Follow-up questions

Weak-area reinforcement

Duplicate-question avoidance

Complete answer history

Final topic-wise scoring

The interview is curriculum-aware rather than a fixed list.

🧠 Adaptive Question Selection

The next question considers:

Candidate profile

Curriculum coverage

Previous questions

Topic performance

Current difficulty

Follow-up availability

Weak areas

Remaining interview capacity

The selector first works to satisfy the minimum curriculum-day coverage.After that it can prioritize weak areas, candidate-relevant unused days,or other unused curriculum content.

This keeps interviews diverse and prevents unnecessary repetition.

📈 Question-Level Improvement System

A major feature is performance-based question difficulty.

Instead of:

Easy → Easy → Easy → Easy

the system can evolve:

Easy
 ↓ strong answer
Medium
 ↓ strong answer
Hard

Example:

Easy > What are embeddings and how do they represent semanticmeaning?

Medium > How would you evaluate whether an embedding model isproducing useful representations?

Hard > How would you design an embedding and retrieval evaluationstrategy for a production RAG system?

For weak answers, the system can move toward easier questions or revisitthe same curriculum area before progressing.

This makes the interview behave more like an adaptive assessment than astatic quiz.

🔁 Follow-Up Questions

The system can explore a topic further when an answer shows enoughunderstanding.

Example for Vector Database:

Why are embeddings used in vector databases?

What is the difference between cosine similarity and Euclideandistance?

How would you improve search performance in a large vector database?

Follow-ups are controlled by:

Current topic

Candidate score

Follow-up count

Previously asked questions

🧪 Phase 3.5 --- Deterministic Evaluation Engine

Phase 3.5 is the core evaluation upgrade.

The evaluator combines:

Topic rubric

Question-specific concepts

Technical concepts

Practical concepts

Answer depth

Strict question relevance

The implementation explicitly documents the Phase 3.5 weighting as:

Dimension                     Weight

Concept Coverage                 30%Technical Depth                  25%Practical Understanding          15%Answer Depth                     15%Question Relevance               15%Total                   100%

The source implementation defines these dimensions inevaluate_answer(). fileciteturn23file1

🎯 Question-Specific Relevance

A technically related answer is not automatically considered a correctanswer.

Example question:

How would you evaluate whether an embedding model is producing usefulrepresentations?

Weak/irrelevant answer:

A vector database stores embeddings and retrieves documents for RAG.

This mentions embeddings, vectors and retrieval, but it does not explainhow to evaluate an embedding model.

Phase 3.5 therefore uses question-specific aliases and intent rules todistinguish:

Topic relevance
      ≠
Question relevance

The implementation contains question-specific concepts for embeddings,Python environment setup, local LLMs, FastAPI + React, CSV processing,document extraction, and chunking/metadata.fileciteturn23file0turn23file4

🔍 Evaluation Signals

Each answer can produce:

Overall score

Performance level

Matched concepts

Matched technical concepts

Matched practical concepts

Word count

Concept score

Technical score

Practical score

Depth score

Relevance score

Matched question intent

Feedback

This makes the evaluation transparent and testable instead of returningonly an unexplained number. fileciteturn23file1

📚 Curriculum-Aware Assessment

Questions are connected to curriculum days and can carry:

Curriculum day

Curriculum title

Curriculum type

Topic

Difficulty

Question

The session tracks curriculum_days_covered and evaluates whether theminimum curriculum requirement has been met. fileciteturn24file6

🗂️ Session Management

An interview session can contain:

sessionId
candidate
questionNumber
currentQuestion
currentTopic
currentDay
difficulty
completed
followUpCount
curriculumDaysCovered
askedQuestions
history
topics

History stores the candidate response and its evaluation.

Available backend endpoints also expose session history and finalresults. fileciteturn24file7

📊 Final Evaluation

At completion the system generates:

Overall score

Performance level

Total questions

Answered questions

Completion percentage

Curriculum days covered

Curriculum day count

Minimum required days

Curriculum requirement status

Topic-wise scores

Strengths

Weak areas

Recommendation

Structured feedback

The final feedback contains a summary, strengths, gaps and recommendednext steps. fileciteturn24file6

Performance bands

  Score Level

85--100 Excellent
 70--84 Good
 50--69 Average
  0--49 Weak

Topic scores are averaged from interview history. Topics scoring atleast 70 are treated as strengths, while topics below 50 are treated asweak areas. fileciteturn24file8

🔌 API Endpoints

Health

GET /health

Example:

{
  "status": "ok"
}

Start / Continue Interview

POST /api/interview

Example question response:

{
  "reply": "What are embeddings and how do they represent the semantic meaning of text?",
  "done": false,
  "difficulty": "easy",
  "topic": "Embeddings",
  "curriculumDay": 7
}

The backend returns the next question with difficulty, topic andcurriculum information. fileciteturn24file12

Interview History

GET /api/interview/{session_id}/history

Returns candidate data, current state, curriculum coverage, askedquestions, history and topic statistics. fileciteturn24file7

Final Result

GET /api/interview/{session_id}/result

Returns:

sessionId
interviewCompleted
result
feedback

🖥️ Frontend Features

Candidate Setup

Candidate ID

Name

Job role

Experience

Interview Screen

Question number

Topic

Difficulty

Technical question

Answer input

Submit answer

Progress

Connection status

Result Screen

Overall score

Performance

Completion

Curriculum coverage

Topic scores

Strengths

Weak areas

Recommendation

Feedback

🚀 Local Setup

1. Clone

git clone https://github.com/VanshTyagi99/AI-Interview-Agent.git
cd AI-Interview-Agent

2. Virtual environment

Windows:

python -m venv .venv
.venv\Scriptsctivate

Linux/macOS:

python3 -m venv .venv
source .venv/bin/activate

3. Install backend dependencies

pip install -r backend/requirements.txt

4. Start backend

From project root:

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

Development reload:

python -m uvicorn backend.app.main:app --reload

5. Start frontend

python -m http.server 5500 --directory frontend

Open:

http://127.0.0.1:5500

🧪 API Testing

Health:

curl http://127.0.0.1:8000/health

Swagger/OpenAPI:

http://127.0.0.1:8000/docs

Expected health response:

{
  "status": "ok"
}

🧪 End-to-End Testing

Candidate Setup
      ↓
Start Interview
      ↓
Question 1
      ↓
Submit Answer
      ↓
Evaluation
      ↓
Adaptive Question
      ↓
...
      ↓
Question 8
      ↓
Final Evaluation
      ↓
Final Report

Recommended tests:

Strong Answer Test

Give a technically strong answer and verify that the next question canbecome more challenging.

Weak Answer Test

Give an unrelated answer and verify lower scoring plus weak-areahandling.

Relevance Test

Give an answer related to the topic but not to the actual question andverify question-specific relevance.

Coverage Test

Verify the interview reaches the minimum curriculum-day requirement.

Completion Test

Complete all 8 questions and verify:

answered_questions = 8
completion_percentage = 100

🧱 Project Structure

AI-Interview-Agent/
│
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── models/
│   │   └── interview.py
│   └── requirements.txt
│
├── data/
│   ├── curriculum.json
│   ├── candidates.json
│   └── sessions.json
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── README.md
├── PROMPTS.md
└── .gitignore

sessions.json is runtime/session data and should remain excluded fromversion control where configured by .gitignore.

🌐 Deployment

Frontend --- Vercel

The static frontend is deployed on Vercel.

Live:

https://ai-interview-agent-iota-two.vercel.app

Backend --- Render

The FastAPI backend is deployed on Render.

Live:

https://ai-interview-agent-api-svqe.onrender.com

Health:

https://ai-interview-agent-api-svqe.onrender.com/health

The frontend communicates with the production backend over HTTPS, withFastAPI CORS configured for the deployed frontend.

🛡️ Error Handling

The application handles:

Backend connection failures

Invalid API responses

Missing interview questions

Invalid sessions

HTTP 404 responses

HTTP 500 responses

Network errors

Empty/invalid interview responses

The frontend also supports production API configuration rather thanrelying on a localhost backend when deployed.

🔍 Why Deterministic Evaluation?

Phase 3.5 intentionally uses a deterministic evaluation layer.

Reproducibility

The same input produces consistent evaluation behavior.

Explainability

Matched concepts and scoring dimensions can be inspected.

Testability

Correct, weak and intentionally irrelevant answers can be tested.

Controlled behavior

Question-specific intent rules reduce false positives from generic topickeywords.

Hackathon-friendly

Judges can inspect the evaluation logic directly in the repository.

🎯 Phase 3.5 Feature Summary

✅ Curriculum-aware interviewing

✅ Adaptive question selection

✅ Easy / Medium / Hard progression

✅ Performance-based difficulty adjustment

✅ Follow-up questions

✅ Weak-area reinforcement

✅ Duplicate-question avoidance

✅ Deterministic answer evaluation

✅ Concept coverage scoring

✅ Technical depth scoring

✅ Practical understanding scoring

✅ Answer depth scoring

✅ Question-specific relevance

✅ Topic-wise scoring

✅ Curriculum-day tracking

✅ Session history

✅ Strength detection

✅ Weak-area detection

✅ Final recommendations

✅ Structured feedback

✅ Production frontend/backend deployment

📸 Recommended Hackathon Demo

Capture screenshots/GIFs of:

Candidate setup

First technical question

Medium/harder adaptive question

Weak-answer evaluation

Curriculum/topic progression

Final result page

Topic-wise scores

Strengths and weak areas

A short demo should show:

Start
  ↓
Question
  ↓
Answer
  ↓
Adaptive Next Question
  ↓
Question 8
  ↓
Final Report

🔮 Future Improvements

LLM-Assisted Semantic Evaluation

Add an LLM as a secondary semantic evaluator while retainingdeterministic guardrails.

Production Database

Move session/candidate data from JSON to PostgreSQL or anotherpersistent database.

Vector Question Retrieval

Use embeddings to retrieve the most appropriate questions from a largercurriculum.

Skill Graph

Model relationships between skills and prerequisites.

Voice Interview

Add speech-to-text and text-to-speech.

Recruiter Dashboard

Add candidate comparison, skill heatmaps, trends and question-levelanalytics.

Authentication

Add recruiter/admin authentication and candidate access control.

Observability

Add structured logs, metrics, latency monitoring and tracing.

🏆 Why This Project?

The project demonstrates the progression:

Static Question Bank
        ↓
Adaptive Interview Engine
        ↓
Question-Aware Evaluation
        ↓
Curriculum-Aware Assessment
        ↓
Actionable Candidate Report

The goal is not to build another quiz.

The goal is to build an interviewer that adapts.

Build the interviewer, not the interview.

📝 AI-Assisted Development

The repository contains:

PROMPTS.md

It documents the AI-assisted development process, including prompts usedfor architecture, adaptive interviewing, evaluation, question-specificrelevance, session management, frontend integration, debugging, testingand final reporting.

📄 License

This project was created as a hackathon/engineering project.

Add an explicit open-source license such as MIT if the project isintended for broader redistribution.

👨‍💻 Project

AI Interview Agent

Built with:

Python · FastAPI · Pydantic · JavaScript · HTML · CSS ·GitHub · Render · Vercel

🔗 Final Links

GitHub:https://github.com/VanshTyagi99/AI-Interview-Agent

Live Demo:https://ai-interview-agent-iota-two.vercel.app

Backend:https://ai-interview-agent-api-svqe.onrender.com

Health Check:https://ai-interview-agent-api-svqe.onrender.com/health
