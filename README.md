AI Interview Agent

An adaptive AI technical interviewer based on a candidate's learningjourney.

AI Interview Agent is a curriculum-aware technical interviewing systemdesigned to evaluate what a candidate actually understands instead ofasking a fixed set of generic interview questions.

🎯 Problem Statement

Traditional technical interviews often use the same questions for everycandidate. This creates several problems:

Questions may not match what the candidate has learned.

Difficulty does not adapt to candidate performance.

Weak technical areas are difficult to identify systematically.

Evaluation can become subjective.

Interview feedback is often too generic.

Candidate learning progress is not connected with interviewperformance.

The Goal

Build an interviewer that can:

Understand the candidate's learning journey.

Select questions from relevant curriculum topics.

Adapt question difficulty.

Ask follow-up questions when required.

Evaluate answers using a deterministic rubric.

Track curriculum and topic coverage.

Identify strengths and weak areas.

Generate a structured final interview report.

💡 Solution

The AI Interview Agent treats the interview as an adaptiveevaluation process.

Candidate
    ↓
Candidate Profile
    ↓
Curriculum
    ↓
Adaptive Question Selection
    ↓
Candidate Answer
    ↓
Deterministic Evaluation
    ↓
Difficulty / Topic Adaptation
    ↓
Next Question
    ↓
Final Evaluation
    ↓
Performance Report

✨ Key Features

1. Curriculum-Aware Interviewing

Questions are selected according to the candidate's curriculum andlearning journey.

The system tracks:

Curriculum day

Curriculum title

Topic

Difficulty

Questions already asked

Curriculum days already covered

2. Adaptive Difficulty

The interviewer can move between:

Easy

Medium

Hard

based on candidate performance.

3. Topic-Aware Question Selection

The system understands the topic associated with each question.

Examples:

Embeddings
Vector Database
RAG / Retrieval
Prompt Engineering
Agents
Data Processing
Frontend
VS Code & Python Environment Setup

4. Follow-Up Questions

The interview can use follow-up questions to investigate understandingbefore moving to a new topic.

5. Deterministic Answer Evaluation

Phase 3.5 evaluates answers across multiple dimensions instead ofrelying only on simple keyword matching.

Dimension                     Weight

Concept Coverage                 30%Technical Depth                  25%Practical Understanding          15%Answer Depth                     15%Question Relevance               15%Total                   100%

The evaluator uses:

Topic-specific rubrics

Question-specific concepts

Technical keywords

Practical keywords

Question intent

Normalized candidate answers

6. Explainable Evaluation

Question-level evaluation can expose:

Matched concepts

Matched technical concepts

Matched practical concepts

Matched question intent

Word count

Individual evaluation scores

Feedback

7. Topic-Wise Scoring

Example:

{
  "Embeddings": {
    "score": 57,
    "attempts": 2
  },
  "Vector Database": {
    "score": 56,
    "attempts": 2
  },
  "Prompt Engineering": {
    "score": 44,
    "attempts": 2
  }
}

8. Curriculum Coverage Tracking

The final result records which curriculum days were covered and whetherthe minimum required coverage was met.

9. Weak Area Detection

Example:

Weak Areas:
- Prompt Engineering
- Agents

10. Final Interview Report

The final result contains:

Overall score

Performance level

Total questions

Answered questions

Completion percentage

Curriculum days covered

Curriculum requirement status

Topic-wise scores

Strengths

Weak areas

Recommendation

Feedback

Next learning actions

🧠 Phase 3.5 --- Deterministic Evaluation Engine

Phase 3.5 is the evaluation layer of the project.

The evaluator receives:

Question
Topic
Candidate Answer
Curriculum Day

It then follows:

Normalize Answer
      ↓
Load Topic Rubric
      ↓
Load Question-Specific Concepts
      ↓
Find Concept Matches
      ↓
Find Technical Matches
      ↓
Find Practical Matches
      ↓
Evaluate Question Relevance
      ↓
Calculate Weighted Score
      ↓
Assign Performance Level
      ↓
Generate Feedback

Example evaluation:

{
  "score": 71,
  "level": "good",
  "matched_concepts": [],
  "matched_technical": [],
  "matched_practical": [],
  "word_count": 45,
  "concept_score": 88,
  "depth_score": 70,
  "technical_score": 17,
  "practical_score": 100,
  "relevance_score": 100,
  "feedback": "Good technical understanding."
}

🏗️ System Architecture

                    ┌──────────────────────┐
                    │      Candidate       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Frontend UI      │
                    │    HTML / CSS / JS   │
                    └──────────┬───────────┘
                               │
                             REST
                               │
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │    Interview API     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │  Curriculum  │ │   Session    │ │  Evaluation  │
      │    Engine    │ │    Engine    │ │    Engine    │
      └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                    ┌──────────────────────┐
                    │    JSON Data Layer   │
                    │ candidates.json      │
                    │ curriculum.json      │
                    │ sessions.json*       │
                    └──────────────────────┘

* Runtime session data is excluded from Git.

📁 Project Structure

AI-Interview-Agent/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── interview.py
│   │
│   └── requirements.txt
│
├── data/
│   ├── candidates.json
│   └── curriculum.json
│
├── frontend/
│   ├── css/
│   ├── js/
│   │   └── app.js
│   └── index.html
│
├── .gitignore
└── README.md

data/sessions.json is runtime-generated session data and should remainlocal.

🛠️ Tech Stack

Technology   Purpose

Python       Backend logicFastAPI      REST APIPydantic     Request/response validationUvicorn      ASGI serverHTML         Frontend structureCSS          Frontend stylingJavaScript   Frontend interactionJSON         Curriculum, candidate and runtime dataGit          Version controlGitHub       Source code hosting

🔌 API Endpoints

Health Check

GET /health

Used to verify that the backend is running.

Interview API

POST /api/interview

Request Body

{
  "sessionId": "CAND-018",
  "message": "Candidate answer",
  "candidate": {
    "id": "CAND-018",
    "name": "Test Candidate",
    "jobRole": "AI Candidate",
    "yearsExperience": 0,
    "education": "",
    "status": "TEST"
  }
}

Response Example

{
  "reply": "What are embeddings and how do they represent the semantic meaning of text?",
  "done": false,
  "difficulty": "easy",
  "topic": "Embeddings",
  "curriculumDay": 7,
  "feedback": null,
  "result": null
}

Interview History

GET /api/interview/{session_id}/history

Example:

/api/interview/CAND-018/history

Returns stored interview history when a session exists.

📊 Example Final Result

{
  "sessionId": "submission-test-001",
  "interviewCompleted": true,
  "result": {
    "overall_score": 51,
    "performance": "average",
    "total_questions": 8,
    "answered_questions": 8,
    "completion_percentage": 100,
    "curriculum_days_covered": [
      7,
      8,
      10,
      12,
      13,
      22
    ],
    "curriculum_day_count": 6,
    "minimum_required_days": 4,
    "curriculum_requirement_met": true,
    "weak_areas": [
      "Prompt Engineering",
      "Agents"
    ]
  }
}

🔄 Complete Interview Flow

Candidate starts interview
          ↓
Candidate/session identified
          ↓
Curriculum loaded
          ↓
Question selected
          ↓
Candidate submits answer
          ↓
Answer evaluated
          ↓
Score + topic + difficulty stored
          ↓
Next question selected
          ↓
Interview continues
          ↓
Configured question count completed
          ↓
Final evaluation generated
          ↓
Performance report returned

🧪 Testing

Start the backend:

python -m uvicorn backend.app.main:app --reload

Then open the FastAPI Swagger interface in the browser.

Recommended test:

Candidate ID: CAND-018

Test the following:

Start an interview.

Submit a strong answer.

Submit a weak or partially relevant answer.

Observe the evaluation.

Continue until the configured question count is completed.

Verify final score.

Verify curriculum coverage.

Verify topic scores.

Verify weak areas.

Verify final feedback.

📸 Demo

After the frontend is completed, add screenshots under:

docs/
├── home.png
├── interview.png
├── evaluation.png
├── result.png
└── swagger.png

Example:

## Demo

### Candidate Screen
![Candidate Screen](docs/home.png)

### Interview Screen
![Interview Screen](docs/interview.png)

### Final Evaluation
![Final Evaluation](docs/result.png)

### API Documentation
![Swagger API](docs/swagger.png)

A short 30--45 second GIF should demonstrate:

Candidate ID
      ↓
Start Interview
      ↓
Question
      ↓
Candidate Answer
      ↓
Evaluation
      ↓
Next Question
      ↓
Final Score

🚀 Installation & Setup

1. Clone the Repository

Clone the public GitHub repository to your local machine.

2. Open the Project

cd AI-Interview-Agent

3. Create Virtual Environment

Windows

python -m venv .venv
.venv\Scriptsctivate

macOS / Linux

python3 -m venv .venv
source .venv/bin/activate

4. Install Dependencies

pip install -r backend/requirements.txt

5. Start Backend

python -m uvicorn backend.app.main:app --reload

6. API Documentation

Use the local FastAPI Swagger documentation at:

http://127.0.0.1:8000/docs

7. Frontend

The frontend is located in the frontend/ directory.

Serve it using a local web server and configure it to communicate withthe FastAPI backend.

🔐 Git & Security

Recommended .gitignore entries:

# Python
__pycache__/
*.py[cod]

# Virtual environment
.venv/
venv/
env/

# Runtime session data
data/sessions.json

# Environment variables
.env
.env.*

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

Candidate session data should not be committed to a public repository.

📈 Future Scope

LLM-based semantic evaluation

Voice-based interviews

Speech-to-text integration

Real-time conversational interviewing

Advanced semantic question matching

Vector database integration

RAG-based curriculum retrieval

Candidate comparison dashboard

Recruiter dashboard

Interview analytics

Authentication and role-based access

Production database

Cloud deployment

Model-based question generation

Multi-agent interviewer architecture

🏆 Why This Project?

The core idea is simple:

The interviewer should adapt to the candidate, not force everycandidate through the same interview.

The system connects:

Learning Journey
      +
Curriculum
      +
Adaptive Interview
      +
Deterministic Evaluation
      +
Performance Analytics

This creates a structured, measurable and curriculum-aligned technicalinterview experience.

🎯 Project Highlights

Adaptive

Questions can adapt based on candidate performance.

Curriculum-Aware

Interview coverage is connected to the candidate's learning journey.

Explainable

The evaluator exposes concepts, technical matches, practical matches andquestion relevance.

Measurable

Every interview produces structured scores and performance information.

Actionable

The final report identifies weak areas and provides recommendations forimprovement.

👨‍💻 Author

Vansh Tyagi

B.Tech Computer ScienceIMS Engineering College, Ghaziabad
