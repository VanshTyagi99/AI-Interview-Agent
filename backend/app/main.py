from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.models.interview import (
    InterviewRequest,
    InterviewResponse,
)


app = FastAPI(
    title="AI Interview Agent",
    description="Curriculum-aware adaptive AI technical interviewer",
    version="3.5.0",
)

# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# CONFIGURATION
# =========================================================

TOTAL_QUESTIONS = 8
MIN_CURRICULUM_DAYS = 4
MAX_FOLLOW_UPS = 2


# =========================================================
# SESSION STORAGE
# =========================================================
# Sessions are persisted to disk so a server reload/restart does
# not immediately destroy an active interview session.
# This keeps the API usable during development and demo testing.

sessions = {}


# =========================================================
# DATA LOADING
# =========================================================

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

SESSION_FILE = DATA_DIR / "sessions.json"


def load_sessions():
    """Load persisted interview sessions from disk."""
    if not SESSION_FILE.exists():
        return {}

    try:
        with open(
            SESSION_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (json.JSONDecodeError, OSError):
        # A damaged session file should never prevent the API
        # from starting. Start with a clean in-memory store.
        return {}


def save_sessions():
    """Persist all active sessions atomically."""
    try:
        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        temp_file = SESSION_FILE.with_suffix(".tmp")

        with open(
            temp_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                sessions,
                file,
                ensure_ascii=False,
                indent=2
            )

        temp_file.replace(SESSION_FILE)

    except (OSError, TypeError):
        # Persistence must not crash an otherwise healthy interview API.
        pass


def load_json_file(filename):

    path = DATA_DIR / filename

    if not path.exists():
        return {}

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_candidates():

    data = load_json_file(
        "candidates.json"
    )

    return data.get(
        "candidates",
        []
    )


def load_curriculum():

    return load_json_file(
        "curriculum.json"
    )


# Restore sessions created before a development-server restart.
sessions.update(load_sessions())


# =========================================================
# CANDIDATE ENGINE
# =========================================================

def find_candidate(candidate_input):
    """
    Supports:
    1. Full candidate object
    2. {"member": {...}, "missions": [...]}
    3. {"id": "CAND-018"}
    4. "CAND-018"
    """

    if isinstance(candidate_input, dict):

        if "member" in candidate_input:
            return candidate_input

        candidate_id = candidate_input.get("id")

        if candidate_id:
            candidate_input = candidate_id

    if isinstance(candidate_input, str):

        for candidate in load_candidates():

            member = candidate.get("member", {})

            if member.get("id") == candidate_input:
                return candidate

    return None


def get_candidate_profile(candidate):
    if not candidate:
        return {
            "id": "UNKNOWN",
            "name": "Candidate",
            "jobRole": "AI Candidate",
            "yearsExperience": 0,
            "education": "",
            "status": "UNKNOWN",
        }

    member = candidate.get("member", {})

    return {
        "id": member.get("id", "UNKNOWN"),
        "name": member.get("name", "Candidate"),
        "jobRole": member.get("jobRole", "AI Candidate"),
        "yearsExperience": member.get("yearsExperience", 0),
        "education": member.get("education", ""),
        "status": member.get("status", "UNKNOWN"),
    }


def get_missions(candidate):
    if not candidate:
        return []

    return candidate.get("missions", [])


def get_mission_map(candidate):
    return {
        mission.get("day"): mission
        for mission in get_missions(candidate)
        if mission.get("day") is not None
    }


def get_failed_days(candidate):
    return [
        mission["day"]
        for mission in get_missions(candidate)
        if mission.get("passed") is False
        and not mission.get("skipped", False)
    ]


def get_skipped_days(candidate):
    return [
        mission["day"]
        for mission in get_missions(candidate)
        if mission.get("skipped") is True
    ]


def get_passed_days(candidate):
    return [
        mission["day"]
        for mission in get_missions(candidate)
        if mission.get("passed") is True
    ]


# =========================================================
# CURRICULUM ENGINE
# =========================================================

def get_curriculum_days():
    curriculum = load_curriculum()
    return curriculum.get("days", [])


def get_curriculum_day(day_number):
    for day in get_curriculum_days():

        if day.get("day") == day_number:
            return day

    return None


def curriculum_topic(day):
    """
    Converts curriculum titles into stable interview topics.
    """

    if not day:
        return "General AI"

    title = day.get("title", "").lower()

    if "embedding" in title:
        return "Embeddings"

    if "vector" in title:
        return "Vector Database"

    if "retrieval" in title:
        return "RAG / Retrieval"

    if "rag" in title:
        return "RAG"

    if "prompt" in title:
        return "Prompt Engineering"

    if "function calling" in title or "structured output" in title:
        return "Function Calling"

    if "fine-tuning" in title or "fine tuning" in title:
        return "Fine-Tuning"

    if "agent" in title:
        return "Agents"

    if "mcp" in title.lower():
        return "MCP"

    if "memory" in title or "context management" in title:
        return "Conversation Memory"

    if "streaming" in title:
        return "Streaming"

    if "security" in title or "guardrail" in title:
        return "Security & Guardrails"

    if "docker" in title or "kubernetes" in title:
        return "Deployment"

    if "monitoring" in title or "observability" in title:
        return "Observability"

    if "production" in title:
        return "Production Readiness"

    if "capstone" in title:
        return "Capstone"

    if "frontend" in title:
        return "Frontend"

    if "backend" in title or "api" in title:
        return "Backend & APIs"

    if "data" in title:
        return "Data Processing"

    return title or "General AI"


# =========================================================
# CURRICULUM QUESTION BANK
# =========================================================

CURRICULUM_QUESTIONS = {

    1: [
        "How would you set up a reliable Python development environment for an AI project?",
    ],

    2: [
        "What are the advantages of using a local LLM and AI coding assistant during development?",
    ],

    3: [
        "How would you connect a FastAPI backend with a React frontend in an AI application?",
    ],

    4: [
        "How would you clean and process structured CSV data before using it in an AI application?",
    ],

    5: [
        "How would you extract and normalize text from PDFs, Word documents, and scanned documents?",
    ],

    6: [
        "Why is chunking and metadata important when building a retrieval knowledge base?",
    ],

    7: [
        "What are embeddings and how do they represent the semantic meaning of text?",
    ],

    8: [
        "What is the role of a vector database in a RAG application?",
    ],

    9: [
        "How would you populate a vector database and verify that semantic retrieval is working correctly?",
    ],

    10: [
        "How would you design a retrieval engine that can choose between SQL, vector search, and hybrid retrieval?",
    ],

    11: [
        "Explain the complete RAG pipeline from retrieval to a grounded LLM response.",
    ],

    12: [
        "How would you design and evaluate a production-ready system prompt?",
    ],

    13: [
        "How does function calling allow an LLM to safely interact with external tools?",
    ],

    14: [
        "When would you choose fine-tuning instead of prompting or RAG?",
    ],

    15: [
        "What are LoRA and QLoRA, and why are they useful for fine-tuning LLMs?",
    ],

    16: [
        "How would you design a FastAPI chat endpoint with session-based conversation management?",
    ],

    17: [
        "How would you connect a chatbot frontend to a backend API while preserving conversation history?",
    ],

    18: [
        "How do streaming responses improve the user experience of an AI chatbot?",
    ],

    19: [
        "How would you add citations and structured outputs to make an AI response more trustworthy?",
    ],

    20: [
        "How would you maintain conversation memory while controlling token usage in a long-running chat?",
    ],

    21: [
        "What is an AI agent and how does tool selection work in a ReAct-style workflow?",
    ],

    22: [
        "How would you design a multi-agent system with specialized agents and a router agent?",
    ],

    23: [
        "Explain the architecture of MCP and how an AI agent can use MCP tools.",
    ],

    24: [
        "How would you combine agents, MCP, retrieval, and memory into a production-style pipeline?",
    ],

    25: [
        "How would you evaluate an AI chatbot for accuracy, grounding, retrieval quality, and consistency?",
    ],

    26: [
        "How would you reduce latency and token cost in a production AI application?",
    ],

    27: [
        "How would you protect an AI application against prompt injection, unauthorized access, and sensitive-data leakage?",
    ],

    28: [
        "How would you containerize and deploy an AI application using Docker and Kubernetes?",
    ],

    29: [
        "What should you monitor and log in a production AI system?",
    ],

    30: [
        "What checks would you perform before declaring an AI application production-ready?",
    ],

    31: [
        "How would you demonstrate a complete production-style AI project from architecture to deployment?",
    ],
}


# =========================================================
# FOLLOW-UP QUESTIONS BY TOPIC
# =========================================================

FOLLOW_UP_QUESTIONS = {

    "Embeddings": [
        "How would you evaluate whether an embedding model is producing useful representations?",
    ],

    "Vector Database": [
        "How does similarity search find the most relevant vectors for a query?",
    ],

    "RAG / Retrieval": [
        "What problems can occur when the retrieved context is irrelevant?",
        "How would you improve retrieval quality using chunking, reranking, or hybrid search?",
    ],

    "RAG": [
        "How would you reduce hallucinations in a production RAG system?",
    ],

    "Prompt Engineering": [
        "What makes a production prompt reliable and consistent?",
    ],

    "Function Calling": [
        "How would you validate and safely execute tool calls generated by an LLM?",
    ],

    "Fine-Tuning": [
        "How would you determine whether fine-tuning actually improved the model?",
    ],

    "Agents": [
        "How can an agent recover when a tool call fails?",
        "How would you maintain context during a multi-step agent workflow?",
    ],

    "MCP": [
        "What is the role of an MCP server and how does an MCP client communicate with it?",
    ],

    "Conversation Memory": [
        "How would you summarize long conversations without losing important context?",
    ],

    "Security & Guardrails": [
        "How would you test an AI application against prompt injection and jailbreak attempts?",
    ],

    "Deployment": [
        "What production concerns should you handle when deploying an AI service on Kubernetes?",
    ],

    "Observability": [
        "Which metrics would you monitor to detect failures or performance degradation?",
    ],

    "Production Readiness": [
        "What would be your final checklist before releasing the AI application?",
    ],
}


# =========================================================
# QUESTION DIFFICULTY
# =========================================================

def difficulty_for_question(
    score=None,
    candidate_experience=0
):

    if score is None:

        if candidate_experience >= 8:
            return "medium"

        return "easy"

    if score >= 85:
        return "hard"

    if score >= 50:
        return "medium"

    return "easy"


# =========================================================
# BUILD CURRICULUM QUESTION
# =========================================================

def build_question(day_number, difficulty="medium"):

    day = get_curriculum_day(
        day_number
    )

    questions = CURRICULUM_QUESTIONS.get(
        day_number,
        []
    )

    if questions:

        question = questions[0]

    elif day:

        objectives = day.get(
            "objectives",
            []
        )

        if objectives:

            question = (
                f"Can you explain how you would "
                f"approach this objective: "
                f"{objectives[0]}?"
            )

        else:

            question = (
                f"What are the key concepts "
                f"you would learn from Day {day_number}?"
            )

    else:

        question = (
            "Can you explain one important "
            "technical concept you learned?"
        )


    return {

        "day":
            day_number,

        "topic":
            curriculum_topic(day),

        "question":
            question,

        "difficulty":
            difficulty,

        "curriculum_title":
            day.get("title", "")
            if day
            else "",

        "curriculum_type":
            day.get("type", "")
            if day
            else "",

    }


# =========================================================
# CANDIDATE DAY PRIORITY
# =========================================================

def get_priority_days(
    candidate,
    session
):

    mission_map = get_mission_map(
        candidate
    )

    covered_days = set(
        session.get(
            "curriculum_days_covered",
            []
        )
    )


    failed = []
    skipped = []
    passed = []


    for day_number, mission in mission_map.items():

        if day_number in covered_days:
            continue

        if mission.get("skipped") is True:

            skipped.append(
                day_number
            )

        elif mission.get("passed") is False:

            failed.append(
                day_number
            )

        elif mission.get("passed") is True:

            passed.append(
                day_number
            )


    # Failed → skipped → passed
    # Candidate history is used to identify areas needing attention.
    return failed + skipped + passed


# =========================================================
# FIND WEAKEST CURRICULUM DAY
# =========================================================

def get_weakest_day(session):

    topic_data = session.get(
        "curriculum_scores",
        {}
    )

    weakest_day = None
    weakest_score = 101


    for day, data in topic_data.items():

        score = data.get(
            "score"
        )

        if score is None:
            continue

        if score < weakest_score:

            weakest_score = score
            weakest_day = int(day)


    return weakest_day


# =========================================================
# CREATE SESSION
# =========================================================

def create_session(candidate):

    profile = get_candidate_profile(
        candidate
    )

    return {

        "candidate": profile,

        "candidate_data": candidate,

        "question_number": 0,

        "difficulty": "easy",

        "current_topic": None,

        "current_question": None,

        "current_day": None,

        "history": [],

        "asked_questions": [],

        "follow_up_count": 0,

        "completed": False,

        "started": False,

        "curriculum_days_covered": [],

        "curriculum_scores": {},

        "topics": {},

    }


# =========================================================
# QUESTION SELECTION
# =========================================================

def select_next_question(
    session,
    difficulty,
    preferred_day=None
):

    candidate = session.get(
        "candidate_data"
    )

    covered_days = set(
        session.get(
            "curriculum_days_covered",
            []
        )
    )

    asked_questions = set(
        session.get(
            "asked_questions",
            []
        )
    )


    # =====================================================
    # 1. PREFERRED DAY
    # =====================================================

    if preferred_day is not None:

        question = build_question(
            preferred_day,
            difficulty
        )

        if question["question"] not in asked_questions:

            return question


    # =====================================================
    # 2. FORCE 4 DIFFERENT CURRICULUM DAYS
    # =====================================================

    if len(covered_days) < MIN_CURRICULUM_DAYS:

        priority_days = get_priority_days(
            candidate,
            session
        )

        for day_number in priority_days:

            if day_number in covered_days:
                continue

            question = build_question(
                day_number,
                difficulty
            )

            if (
                question["question"]
                not in asked_questions
            ):

                return question


    # =====================================================
    # 3. WEAKEST DAY
    # =====================================================

    weakest_day = get_weakest_day(
        session
    )

    if weakest_day is not None:

        question = build_question(
            weakest_day,
            difficulty
        )

        if (
            question["question"]
            not in asked_questions
        ):

            return question


    # =====================================================
    # 4. CANDIDATE RELEVANT UNUSED DAY
    # =====================================================

    priority_days = get_priority_days(
        candidate,
        session
    )

    for day_number in priority_days:

        question = build_question(
            day_number,
            difficulty
        )

        if (
            question["question"]
            not in asked_questions
        ):

            return question


    # =====================================================
    # 5. ANY UNUSED CURRICULUM DAY
    # =====================================================

    for day in get_curriculum_days():

        day_number = day.get(
            "day"
        )

        if day_number in covered_days:
            continue

        question = build_question(
            day_number,
            difficulty
        )

        if (
            question["question"]
            not in asked_questions
        ):

            return question


    # =====================================================
    # 6. FALLBACK
    # =====================================================

    return {

        "day":
            None,

        "topic":
            "General AI",

        "question":
            "Can you explain one important technical concept you learned during the AI cohort?",

        "difficulty":
            difficulty,

        "curriculum_title":
            "",

        "curriculum_type":
            "",

    }


# =========================================================
# KEYWORDS FOR EVALUATION
# =========================================================

TOPIC_KEYWORDS = {

    "Embeddings": [
        "embedding",
        "vector",
        "semantic",
        "representation",
        "similarity",
    ],

    "Vector Database": [
        "vector",
        "embedding",
        "similarity",
        "search",
        "database",
        "semantic",
        "index",
    ],

    "RAG / Retrieval": [
        "retrieval",
        "query",
        "embedding",
        "vector",
        "document",
        "context",
        "reranking",
    ],

    "RAG": [
        "retrieval",
        "augmented",
        "generation",
        "context",
        "document",
        "embedding",
        "language model",
    ],

    "Prompt Engineering": [
        "prompt",
        "instruction",
        "context",
        "model",
        "output",
        "role",
        "constraint",
        "example",
    ],

    "Function Calling": [
        "function",
        "tool",
        "schema",
        "pydantic",
        "structured",
        "validation",
        "api",
    ],

    "Fine-Tuning": [
        "fine-tuning",
        "lora",
        "qlora",
        "dataset",
        "training",
        "model",
        "evaluation",
    ],

    "Agents": [
        "agent",
        "goal",
        "tool",
        "planning",
        "action",
        "reasoning",
        "environment",
    ],

    "MCP": [
        "mcp",
        "model context protocol",
        "tool",
        "server",
        "client",
        "resource",
        "protocol",
    ],

    "Conversation Memory": [
        "memory",
        "context",
        "conversation",
        "history",
        "summary",
        "tokens",
    ],

    "Security & Guardrails": [
        "security",
        "authentication",
        "validation",
        "prompt injection",
        "jailbreak",
        "privacy",
        "sensitive",
        "guardrail",
    ],

    "Deployment": [
        "docker",
        "kubernetes",
        "container",
        "deployment",
        "health",
        "environment",
        "scaling",
    ],

    "Observability": [
        "logging",
        "monitoring",
        "metrics",
        "latency",
        "prometheus",
        "grafana",
        "observability",
    ],

    "Production Readiness": [
        "testing",
        "deployment",
        "documentation",
        "security",
        "monitoring",
        "performance",
        "production",
    ],

}


# =========================================================
# PHASE 3.5 — ADVANCED ANSWER EVALUATION
# =========================================================

EVALUATION_RUBRIC = {

    "Embeddings": {
        "concepts": [
            "embedding", "vector", "semantic", "representation",
            "similarity", "meaning"
        ],
        "technical": [
            "vector space", "high dimensional", "cosine similarity",
            "euclidean distance", "distance", "dimension"
        ],
        "practical": [
            "vector database", "semantic search", "rag",
            "retrieval", "search"
        ],
    },

    "vs code & python environment setup": {
        "concepts": [
            "python", "virtual environment", "dependency",
            "package", "interpreter", "environment"
        ],
        "technical": [
            "venv", "virtualenv", "requirements.txt", "pip",
            "python version", "environment variable", "venv"
        ],
        "practical": [
            "vs code", "git", "api key", "project setup",
            "isolated environment"
        ],
    },

    "local llm & ai coding assistant setup": {
        "concepts": [
            "local llm", "privacy", "offline", "coding assistant",
            "development", "local model"
        ],
        "technical": [
            "model", "gpu", "ram", "local inference", "api",
            "hardware", "latency"
        ],
        "practical": [
            "code generation", "debugging", "refactoring",
            "autocomplete", "code completion"
        ],
    },

    "Frontend": {
        "concepts": [
            "frontend", "backend", "api", "http", "json",
            "request", "response"
        ],
        "technical": [
            "fastapi", "react", "rest", "cors", "axios", "fetch",
            "endpoint"
        ],
        "practical": [
            "user interface", "deployment", "browser",
            "client", "server"
        ],
    },

    "Data Processing": {
        "concepts": [
            "data", "csv", "cleaning", "missing", "duplicate",
            "processing", "dataset"
        ],
        "technical": [
            "pandas", "data type", "normalization", "validation",
            "transformation", "preprocessing"
        ],
        "practical": [
            "pipeline", "dataset", "quality", "outlier",
            "null", "missing value"
        ],
    },

    "building the knowledge base": {
        "concepts": [
            "chunking", "metadata", "document", "knowledge base",
            "retrieval", "chunk"
        ],
        "technical": [
            "chunk size", "overlap", "embedding", "vector database",
            "semantic search", "retriever"
        ],
        "practical": [
            "page number", "source", "filtering", "rag",
            "citation"
        ],
    },

    "RAG / Retrieval": {
        "concepts": [
            "retrieval", "query", "embedding", "vector",
            "document", "context", "relevance"
        ],
        "technical": [
            "vector database", "similarity search", "reranking",
            "chunking", "retriever", "hybrid search", "top k"
        ],
        "practical": [
            "hallucination", "grounded", "knowledge base",
            "rag", "filtering"
        ],
    },

    "RAG": {
        "concepts": [
            "retrieval", "augmented", "generation", "context",
            "document", "embedding", "language model"
        ],
        "technical": [
            "vector database", "similarity search", "reranking",
            "chunking", "retriever", "prompt"
        ],
        "practical": [
            "hallucination", "grounded", "knowledge base",
            "rag", "source"
        ],
    },

    "Vector Database": {
        "concepts": [
            "vector", "embedding", "similarity", "search",
            "database", "semantic", "index"
        ],
        "technical": [
            "cosine similarity", "euclidean distance", "nearest neighbor",
            "approximate nearest neighbor", "index", "hnsw", "top k"
        ],
        "practical": [
            "rag", "retrieval", "filtering", "metadata",
            "semantic search"
        ],
    },

    "Prompt Engineering": {
        "concepts": [
            "prompt", "instruction", "context", "model",
            "output", "role", "constraint", "example"
        ],
        "technical": [
            "system prompt", "few shot", "structured output",
            "json", "temperature", "schema", "validation"
        ],
        "practical": [
            "testing", "edge case", "production", "evaluation",
            "examples", "guardrail"
        ],
    },

    "Function Calling": {
        "concepts": [
            "function", "tool", "schema", "structured",
            "validation", "api"
        ],
        "technical": [
            "function calling", "tool calling", "json schema",
            "pydantic", "validation", "arguments"
        ],
        "practical": [
            "external tool", "api", "database", "authentication",
            "error handling"
        ],
    },

    "Fine-Tuning": {
        "concepts": [
            "fine-tuning", "dataset", "training", "model",
            "evaluation", "lora", "qlora"
        ],
        "technical": [
            "lora", "qlora", "parameter efficient", "learning rate",
            "epochs", "quantization", "training data"
        ],
        "practical": [
            "domain", "cost", "gpu", "deployment",
            "benchmark", "production"
        ],
    },

    "Agents": {
        "concepts": [
            "agent", "goal", "tool", "planning", "action",
            "reasoning", "environment"
        ],
        "technical": [
            "tool calling", "memory", "workflow", "orchestration",
            "react", "state", "planner"
        ],
        "practical": [
            "api", "external tool", "decision", "multi step",
            "failure", "retry"
        ],
    },

    "MCP": {
        "concepts": [
            "mcp", "model context protocol", "tool", "server",
            "client", "resource", "protocol"
        ],
        "technical": [
            "mcp server", "mcp client", "tool", "resource",
            "prompt", "transport"
        ],
        "practical": [
            "external tool", "agent", "api", "permission",
            "authentication"
        ],
    },

    "Conversation Memory": {
        "concepts": [
            "memory", "context", "conversation", "history",
            "summary", "tokens"
        ],
        "technical": [
            "context window", "token", "summarization",
            "conversation state", "short term memory"
        ],
        "practical": [
            "long conversation", "database", "session",
            "persistent memory", "cost"
        ],
    },

    "Security & Guardrails": {
        "concepts": [
            "security", "authentication", "validation",
            "prompt injection", "jailbreak", "privacy",
            "sensitive", "guardrail"
        ],
        "technical": [
            "authorization", "input validation", "sanitization",
            "access control", "rate limiting", "secret"
        ],
        "practical": [
            "data leakage", "api key", "user input",
            "monitoring", "attack", "permission"
        ],
    },

    "Deployment": {
        "concepts": [
            "docker", "kubernetes", "container", "deployment",
            "health", "environment", "scaling"
        ],
        "technical": [
            "dockerfile", "image", "pod", "service",
            "ingress", "replica", "environment variable"
        ],
        "practical": [
            "production", "rollback", "monitoring",
            "load balancing", "availability"
        ],
    },

    "Observability": {
        "concepts": [
            "logging", "monitoring", "metrics", "latency",
            "observability"
        ],
        "technical": [
            "prometheus", "grafana", "trace", "tracing",
            "error rate", "response time"
        ],
        "practical": [
            "alert", "dashboard", "production", "failure",
            "performance"
        ],
    },

    "Production Readiness": {
        "concepts": [
            "testing", "deployment", "documentation", "security",
            "monitoring", "performance", "production"
        ],
        "technical": [
            "load testing", "authentication", "logging",
            "health check", "ci/cd", "rollback"
        ],
        "practical": [
            "scaling", "latency", "cost", "reliability",
            "incident", "backup"
        ],
    },
}


# Question-specific aliases make evaluation robust without requiring
# an exact keyword match. The evaluator remains deterministic.
QUESTION_ALIASES = {
    "python development environment": [
        "virtual environment", "venv", "requirements",
        "dependency", "pip", "interpreter", "python version",
        "environment variable", "api key", "vs code", "git"
    ],
    "local llm": [
        "privacy", "offline", "local model", "gpu", "ram",
        "hardware", "inference", "coding assistant",
        "code generation", "debugging", "refactoring"
    ],
    "fastapi backend with a react frontend": [
        "fastapi", "react", "rest", "api", "http", "json",
        "fetch", "axios", "cors", "request", "response",
        "frontend", "backend"
    ],
    "structured csv data": [
        "csv", "pandas", "missing", "duplicate", "data type",
        "clean", "validation", "normalization", "transformation",
        "preprocessing", "outlier", "dataset"
    ],
    "pdfs, word documents, and scanned documents": [
        "pdf", "word", "docx", "ocr", "scanned", "text extraction",
        "normalize", "encoding", "header", "footer", "metadata"
    ],
    "chunking and metadata": [
        "chunk", "chunking", "metadata", "embedding",
        "vector database", "retrieval", "source", "page",
        "filtering", "rag", "overlap"
    ],
    "embeddings": [
        "embedding", "vector", "semantic", "representation",
        "similarity", "vector database", "retrieval"
    ],
}

# =========================================================
# PHASE 3.5.1 — STRICT QUESTION INTENT RULES
# =========================================================
# These rules prevent generic topic words from being treated
# as proof that an answer actually addressed the question.

QUESTION_INTENT = {
    # Day 1
    "how would you set up a reliable python development environment for an ai project?": [
        "python", "virtual environment", "venv", "pip", "dependency",
        "requirements", "interpreter", "python version", "vs code",
        "environment variable", "git"
    ],

    # Day 2
    "what are the advantages of using a local llm and ai coding assistant during development?": [
        "local llm", "local model", "privacy", "offline", "latency",
        "gpu", "ram", "hardware", "coding assistant", "code generation",
        "debugging", "refactoring", "autocomplete"
    ],

    # Day 3
    "how would you connect a fastapi backend with a react frontend in an ai application?": [
        "fastapi", "react", "api", "http", "json", "fetch", "axios",
        "cors", "request", "response", "endpoint"
    ],

    # Day 4
    "how would you clean and process structured csv data before using it in an ai application?": [
        "csv", "pandas", "missing", "duplicate", "data type", "clean",
        "validation", "normalization", "transformation", "preprocessing",
        "outlier", "null"
    ],

    # Day 5
    "how would you extract and normalize text from pdfs, word documents, and scanned documents?": [
        "pdf", "word", "docx", "ocr", "scanned", "text extraction",
        "normalize", "encoding", "header", "footer", "metadata"
    ],

    # Day 6
    "why is chunking and metadata important when building a retrieval knowledge base?": [
        "chunk", "chunking", "metadata", "chunk size", "overlap",
        "source", "page", "retrieval", "knowledge base", "filter",
        "embedding", "vector database"
    ],

    # Day 7
    "what are embeddings and how do they represent the semantic meaning of text?": [
        "embedding", "vector", "semantic", "representation", "meaning",
        "vector space", "similar texts", "similarity"
    ],

    "how would you evaluate whether an embedding model is producing useful representations?": [
        "evaluate", "evaluation", "benchmark", "test", "semantic similarity",
        "similar texts", "dissimilar texts", "retrieval quality", "precision",
        "recall", "top-k", "accuracy", "downstream", "human evaluation"
    ],

    # Day 8
    "what is the role of a vector database in a rag application?": [
        "vector database", "embedding", "similarity search", "semantic search",
        "nearest neighbor", "retrieval", "metadata", "rag"
    ],

    "how does similarity search find the most relevant vectors for a query?": [
        "query embedding", "embedding", "cosine similarity", "euclidean distance",
        "nearest neighbor", "similarity", "top k", "index", "hnsw"
    ],

    # Day 9
    "how would you populate a vector database and verify that semantic retrieval is working correctly?": [
        "documents", "chunking", "embedding", "vector database", "upsert",
        "index", "query", "similarity", "top k", "retrieval", "evaluation"
    ],

    # Day 10
    "how would you design a retrieval engine that can choose between sql, vector search, and hybrid retrieval?": [
        "sql", "vector search", "hybrid search", "retrieval", "router",
        "query type", "structured", "semantic", "keyword", "reranking"
    ],

    # Day 11
    "explain the complete rag pipeline from retrieval to a grounded llm response.": [
        "retrieval", "query", "embedding", "vector database", "context",
        "prompt", "llm", "grounded", "source", "generation"
    ],

    # Day 12
    "how would you design and evaluate a production-ready system prompt?": [
        "system prompt", "instruction", "role", "constraint", "output",
        "evaluation", "test", "edge case", "guardrail", "versioning"
    ],

    # Day 13
    "how does function calling allow an llm to safely interact with external tools?": [
        "function calling", "tool calling", "schema", "json schema",
        "arguments", "validation", "external tool", "api", "authentication",
        "error handling", "permission"
    ],

    # Day 14
    "when would you choose fine-tuning instead of prompting or rag?": [
        "fine-tuning", "prompting", "rag", "domain", "training data",
        "behavior", "cost", "latency", "knowledge", "evaluation"
    ],

    # Day 15
    "what are lora and qlora, and why are they useful for fine-tuning llms?": [
        "lora", "qlora", "fine-tuning", "parameter efficient",
        "low rank", "quantization", "memory", "gpu", "training"
    ],

    # Day 16
    "how would you design a fastapi chat endpoint with session-based conversation management?": [
        "fastapi", "endpoint", "session", "conversation", "history",
        "request", "response", "database", "state", "session id"
    ],

    # Day 17
    "how would you connect a chatbot frontend to a backend api while preserving conversation history?": [
        "frontend", "backend", "api", "conversation history", "session",
        "request", "response", "state", "database"
    ],

    # Day 18
    "how do streaming responses improve the user experience of an ai chatbot?": [
        "streaming", "tokens", "latency", "time to first token",
        "response", "user experience", "websocket", "server sent events"
    ],

    # Day 19
    "how would you add citations and structured outputs to make an ai response more trustworthy?": [
        "citations", "source", "structured output", "json", "schema",
        "validation", "grounding", "traceability", "trust"
    ],

    # Day 20
    "how would you maintain conversation memory while controlling token usage in a long-running chat?": [
        "conversation memory", "history", "summary", "summarization",
        "token", "context window", "short term memory", "persistent memory",
        "database"
    ],

    # Day 21
    "what is an ai agent and how does tool selection work in a react-style workflow?": [
        "agent", "goal", "tool", "tool selection", "planning", "action",
        "reasoning", "react", "environment", "observation"
    ],

    # Day 22
    "how would you design a multi-agent system with specialized agents and a router agent?": [
        "multi-agent", "specialized agents", "router agent", "routing",
        "orchestration", "tool", "state", "workflow", "handoff"
    ],

    # Day 23
    "explain the architecture of mcp and how an ai agent can use mcp tools.": [
        "mcp", "model context protocol", "mcp server", "mcp client",
        "tool", "resource", "protocol", "agent", "transport"
    ],

    # Day 24
    "how would you combine agents, mcp, retrieval, and memory into a production-style pipeline?": [
        "agent", "mcp", "retrieval", "memory", "orchestration",
        "pipeline", "tool", "vector database", "state", "monitoring"
    ],

    # Day 25
    "how would you evaluate an ai chatbot for accuracy, grounding, retrieval quality, and consistency?": [
        "accuracy", "grounding", "retrieval quality", "consistency",
        "evaluation", "benchmark", "precision", "recall", "faithfulness",
        "human evaluation"
    ],

    # Day 26
    "how would you reduce latency and token cost in a production ai application?": [
        "latency", "token cost", "caching", "model selection",
        "smaller model", "streaming", "batching", "prompt", "tokens"
    ],

    # Day 27
    "how would you protect an ai application against prompt injection, unauthorized access, and sensitive-data leakage?": [
        "prompt injection", "unauthorized access", "authentication",
        "authorization", "sensitive data", "data leakage", "input validation",
        "sanitization", "rate limiting", "secrets"
    ],

    # Day 28
    "how would you containerize and deploy an ai application using docker and kubernetes?": [
        "docker", "dockerfile", "container", "image", "kubernetes",
        "pod", "service", "deployment", "ingress", "replica", "scaling"
    ],

    # Day 29
    "what should you monitor and log in a production ai system?": [
        "monitoring", "logging", "metrics", "latency", "error rate",
        "token usage", "cost", "tracing", "alerts", "performance"
    ],

    # Day 30
    "what checks would you perform before declaring an ai application production-ready?": [
        "testing", "security", "performance", "monitoring", "deployment",
        "health check", "load testing", "authentication", "rollback",
        "documentation"
    ],

    # Day 31
    "how would you demonstrate a complete production-style ai project from architecture to deployment?": [
        "architecture", "implementation", "testing", "deployment",
        "security", "monitoring", "documentation", "ci/cd", "production"
    ],
}


def strict_question_relevance(question, answer):
    """
    Returns (score, matched_terms, is_strict_rule)
    for questions with an explicit intent rubric.
    """
    normalized_question = normalize_text(question)
    expected = QUESTION_INTENT.get(normalized_question)

    if not expected:
        return None, [], False

    answer_lower = normalize_text(answer)

    matched = [
        term
        for term in expected
        if normalize_text(term) in answer_lower
    ]

    if not matched:
        return 0, [], True

    return round(
        len(matched) / len(expected) * 100
    ), matched, True



def normalize_text(text):
    return " ".join(
        str(text).lower().strip().split()
    )


def find_matches(answer, keywords):
    answer_lower = normalize_text(answer)
    return [
        keyword
        for keyword in keywords
        if normalize_text(keyword) in answer_lower
    ]


def question_specific_keywords(question):
    q = normalize_text(question)
    matched = []

    for phrase, keywords in QUESTION_ALIASES.items():
        if normalize_text(phrase) in q:
            matched.extend(keywords)

    return list(dict.fromkeys(matched))


def evaluate_answer(
    question,
    topic,
    answer,
    day_number=None
):
    """
    Phase 3.5 deterministic evaluator.

    Scores:
      - concept coverage: 30%
      - technical depth: 25%
      - practical understanding: 15%
      - answer depth: 15%
      - question relevance: 15% (strict question intent where defined)

    It uses topic rubric + question-specific concepts, so a
    technically correct answer is not penalized merely because
    it uses different wording from the topic label.
    """

    answer = str(answer or "").strip()
    answer_lower = normalize_text(answer)
    question = str(question or "")

    rubric = EVALUATION_RUBRIC.get(
        topic,
        {}
    )

    concept_keywords = list(
        rubric.get("concepts", [])
    )
    technical_keywords = list(
        rubric.get("technical", [])
    )
    practical_keywords = list(
        rubric.get("practical", [])
    )

    specific_keywords = question_specific_keywords(
        question
    )

    # Add question-specific terms to concept pool.
    concept_keywords = list(
        dict.fromkeys(
            concept_keywords
            + specific_keywords
        )
    )

    matched_concepts = find_matches(
        answer,
        concept_keywords
    )

    matched_technical = find_matches(
        answer,
        technical_keywords
    )

    matched_practical = find_matches(
        answer,
        practical_keywords
    )

    # =====================================================
    # CONCEPT SCORE
    # =====================================================

    if concept_keywords:
        concept_score = round(
            len(matched_concepts)
            / len(concept_keywords)
            * 100
        )
    else:
        concept_score = 50

    # =====================================================
    # TECHNICAL SCORE
    # =====================================================

    if technical_keywords:
        technical_score = round(
            len(matched_technical)
            / len(technical_keywords)
            * 100
        )
    else:
        technical_score = 50

    # =====================================================
    # PRACTICAL SCORE
    # =====================================================

    if practical_keywords:
        practical_score = round(
            len(matched_practical)
            / len(practical_keywords)
            * 100
        )
    else:
        practical_score = 50

    # =====================================================
    # DEPTH SCORE
    # =====================================================

    word_count = len(
        answer.split()
    )

    if word_count < 10:
        depth_score = 20
    elif word_count < 25:
        depth_score = 45
    elif word_count < 50:
        depth_score = 70
    elif word_count < 100:
        depth_score = 85
    else:
        depth_score = 95

    # =====================================================
    # QUESTION-AWARE RELEVANCE
    # =====================================================

    strict_score, matched_question_intent, is_strict = (
        strict_question_relevance(
            question,
            answer,
        )
    )

    if is_strict:
        relevance_score = strict_score

    elif specific_keywords:
        matched_specific = find_matches(
            answer,
            specific_keywords
        )

        relevance_score = round(
            len(matched_specific)
            / len(specific_keywords)
            * 100
        )

    elif matched_concepts:
        relevance_score = min(
            100,
            35 + len(matched_concepts) * 10
        )

    else:
        relevance_score = 20

    # =====================================================
    # LOW-ANSWER GUARD
    # =====================================================

    if word_count < 5:
        concept_score = min(
            concept_score,
            20
        )
        technical_score = min(
            technical_score,
            20
        )
        practical_score = min(
            practical_score,
            20
        )
        relevance_score = min(
            relevance_score,
            25
        )

    # =====================================================
    # FINAL SCORE
    # =====================================================

    final_score = round(
        (concept_score * 0.30)
        + (technical_score * 0.25)
        + (practical_score * 0.15)
        + (depth_score * 0.15)
        + (relevance_score * 0.15)
    )

    # =====================================================
    # STRICT RELEVANCE GUARD
    # =====================================================
    # If a question has an explicit intent rubric and the answer
    # does not address that intent at all, it must not receive a
    # misleadingly high score just because it contains generic
    # topic words.
    if is_strict and relevance_score == 0:
        final_score = min(final_score, 35)

    # =====================================================
    # LEVEL
    # =====================================================

    if final_score >= 85:
        level = "excellent"
    elif final_score >= 70:
        level = "good"
    elif final_score >= 50:
        level = "average"
    else:
        level = "weak"

    # =====================================================
    # FEEDBACK
    # =====================================================

    if final_score >= 85:
        feedback = (
            "Excellent understanding with strong technical "
            "depth, relevance, and practical awareness."
        )
    elif final_score >= 70:
        feedback = (
            "Good technical understanding. The candidate can "
            "improve depth and add more production-level examples."
        )
    elif final_score >= 50:
        feedback = (
            "Average understanding. The candidate should improve "
            "technical depth, clarity, and practical examples."
        )
    else:
        feedback = (
            "Weak or partially relevant answer. The candidate "
            "should revisit the core concepts and explain the "
            "topic more directly."
        )

    return {
        "score": final_score,
        "level": level,
        "matched_concepts": matched_concepts,
        "matched_technical": matched_technical,
        "matched_practical": matched_practical,
        "word_count": word_count,
        "concept_score": concept_score,
        "depth_score": depth_score,
        "technical_score": technical_score,
        "practical_score": practical_score,
        "relevance_score": relevance_score,
        "matched_question_intent": matched_question_intent,
        "feedback": feedback,
        "curriculum_day": day_number,
    }


# =========================================================
# FOLLOW-UP SELECTION
# =========================================================

def select_follow_up_question(
    topic,
    asked_questions
):

    questions = FOLLOW_UP_QUESTIONS.get(
        topic,
        []
    )

    for question in questions:

        if question not in asked_questions:

            return question

    return None


# =========================================================
# FINAL RESULT
# =========================================================

def generate_final_result(session):

    history = session.get(
        "history",
        []
    )


    if not history:

        return {

            "overall_score": 0,

            "performance": "not_evaluated",

            "total_questions":
                TOTAL_QUESTIONS,

            "answered_questions": 0,

            "completion_percentage": 0,

            "curriculum_days_covered": [],

            "curriculum_day_count": 0,

            "minimum_required_days":
                MIN_CURRICULUM_DAYS,

            "curriculum_requirement_met":
                False,

            "topic_scores": {},

            "strengths": [],

            "weak_areas": [],

            "recommendation":
                "No answers were submitted.",

        }


    scores = [
        item.get(
            "evaluation",
            {}
        ).get(
            "score",
            0
        )
        for item in history
    ]

    overall_score = round(
        sum(scores) / len(scores)
    )


    if overall_score >= 85:

        performance = "excellent"

    elif overall_score >= 70:

        performance = "good"

    elif overall_score >= 50:

        performance = "average"

    else:

        performance = "weak"


    # =====================================================
    # TOPIC SCORES
    # =====================================================

    topic_data = {}

    for item in history:

        topic = item.get(
            "topic",
            "General AI"
        )

        score = item.get(
            "evaluation",
            {}
        ).get(
            "score",
            0
        )

        topic_data.setdefault(
            topic,
            []
        ).append(score)


    topic_scores = {

        topic: {

            "score": round(
                sum(scores)
                / len(scores)
            ),

            "attempts":
                len(scores),

        }

        for topic, scores
        in topic_data.items()

    }


    strengths = [
        topic
        for topic, data
        in topic_scores.items()
        if data["score"] >= 70
    ]


    weak_areas = [
        topic
        for topic, data
        in topic_scores.items()
        if data["score"] < 50
    ]


    covered_days = session.get(
        "curriculum_days_covered",
        []
    )


    if overall_score >= 70:

        recommendation = (
            "Good interview performance. "
            "Continue improving depth, production reasoning, "
            "and system-design explanations."
        )

    elif overall_score >= 50:

        recommendation = (
            "Candidate has a basic technical foundation "
            "but needs stronger depth, clarity, and examples."
        )

    else:

        recommendation = (
            "Candidate needs significant improvement "
            "in core concepts and technical explanation."
        )


    return {

        "overall_score":
            overall_score,

        "performance":
            performance,

        "total_questions":
            TOTAL_QUESTIONS,

        "answered_questions":
            len(history),

        "completion_percentage":
            min(
                100,
                round(
                    len(history)
                    / TOTAL_QUESTIONS
                    * 100
                )
            ),

        "curriculum_days_covered":
            covered_days,

        "curriculum_day_count":
            len(covered_days),

        "minimum_required_days":
            MIN_CURRICULUM_DAYS,

        "curriculum_requirement_met":
            len(covered_days)
            >= MIN_CURRICULUM_DAYS,

        "topic_scores":
            topic_scores,

        "strengths":
            strengths,

        "weak_areas":
            weak_areas,

        "recommendation":
            recommendation,

    }


# =========================================================
# FINAL TECHNICAL-SPEC FEEDBACK
# =========================================================

def build_final_feedback(session, result):

    strengths = result.get(
        "strengths",
        []
    )

    gaps = result.get(
        "weak_areas",
        []
    )

    next_steps = []


    if not strengths:

        next_steps.append(
            "Strengthen the core concepts covered during the interview."
        )


    if gaps:

        for topic in gaps[:3]:

            next_steps.append(
                f"Review {topic} and practice explaining it with a real-world example."
            )


    if not next_steps:

        next_steps.append(
            "Practice production-level system design and implementation trade-offs."
        )


    summary = (
        f"Candidate completed the interview with an overall score of "
        f"{result['overall_score']}/100 and a "
        f"{result['performance']} performance level. "
        f"The interview covered {result['curriculum_day_count']} "
        f"curriculum days."
    )


    return {

        "summary":
            summary,

        "strengths":
            strengths,

        "gaps":
            gaps,

        "next":
            next_steps,

    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():

    return {
        "status": "ok"
    }


# =========================================================
# MAIN INTERVIEW ENDPOINT
# =========================================================

@app.post("/api/interview", response_model=InterviewResponse)
async def interview(request: InterviewRequest):

    body = request.model_dump()


    session_id = body.get(
        "sessionId"
    )

    if not session_id:

        return {
            "error":
                "sessionId is required"
        }


    # =====================================================
    # START / CREATE SESSION
    # =====================================================

    if session_id not in sessions:

        candidate_input = body.get(
            "candidate"
        )

        candidate = find_candidate(
            candidate_input
        )


        # Allow old testing flow without candidate
        if candidate is None:

            candidate = {
                "member": {
                    "id": "UNKNOWN",
                    "name": "Test Candidate",
                    "jobRole": "AI Candidate",
                    "yearsExperience": 0,
                    "education": "",
                    "status": "TEST",
                },
                "missions": [],
                "signals": {},
            }


        session = create_session(
            candidate
        )

        sessions[
            session_id
        ] = session


        # =================================================
        # SELECT FIRST CURRICULUM DAY
        # =================================================

        priority_days = get_priority_days(
            candidate,
            session
        )


        if priority_days:

            first_day = priority_days[0]

        else:

            first_day = 7


        experience = session[
            "candidate"
        ].get(
            "yearsExperience",
            0
        )


        first_difficulty = (
            difficulty_for_question(
                None,
                experience
            )
        )


        first_question = build_question(
            first_day,
            first_difficulty
        )


        # =================================================
        # SESSION STATE
        # =================================================

        session["question_number"] = 1

        session["difficulty"] = (
            first_difficulty
        )

        session["current_topic"] = (
            first_question["topic"]
        )

        session["current_question"] = (
            first_question["question"]
        )

        session["current_day"] = (
            first_question["day"]
        )

        session["started"] = True


        session[
            "asked_questions"
        ].append(
            first_question["question"]
        )

        save_sessions()


        # =================================================
        # NOTE:
        # Day is only counted after an answer is evaluated.
        # =================================================

        return {

            "reply": first_question["question"],

            "done": False,

            "difficulty":
                first_difficulty,

            "topic":
                first_question["topic"],

            "curriculumDay":
                first_question["day"],

            "curriculumTitle":
                first_question[
                    "curriculum_title"
                ],

        }


    # =====================================================
    # EXISTING SESSION
    # =====================================================

    session = sessions[
        session_id
    ]


    # =====================================================
    # COMPLETED SESSION
    # =====================================================

    if session["completed"]:

        result = generate_final_result(
            session
        )

        feedback = build_final_feedback(
            session,
            result
        )

        save_sessions()

        return {

            "reply":
                "Interview completed.",

            "done":
                True,

            "feedback":
                feedback,

            "result":
                result,

        }


    # =====================================================
    # GET CANDIDATE ANSWER
    # =====================================================

    message = str(
        body.get(
            "message",
            ""
        )
    ).strip()


    if not message:

        return {

            "reply": (
                "Please provide your answer "
                "before continuing."
            ),

            "done": False,

            "difficulty":
                session["difficulty"],

            "topic":
                session["current_topic"],

            "curriculumDay":
                session["current_day"],

        }


    # =====================================================
    # CURRENT QUESTION DATA
    # =====================================================

    current_day = session[
        "current_day"
    ]

    current_topic = session[
        "current_topic"
    ]

    current_question = session[
        "current_question"
    ]

    current_difficulty = session[
        "difficulty"
    ]

    current_number = session[
        "question_number"
    ]


    # =====================================================
    # EVALUATE
    # =====================================================

    evaluation = evaluate_answer(
        question=current_question,
        topic=current_topic,
        answer=message,
        day_number=current_day,
    )


    score = evaluation[
        "score"
    ]


    # =====================================================
    # TRACK CURRICULUM DAY
    # =====================================================

    if (
        current_day is not None
        and current_day
        not in session[
            "curriculum_days_covered"
        ]
    ):

        session[
            "curriculum_days_covered"
        ].append(
            current_day
        )


    # =====================================================
    # CURRICULUM DAY SCORE
    # =====================================================

    if current_day is not None:

        key = str(
            current_day
        )

        session[
            "curriculum_scores"
        ].setdefault(
            key,
            {
                "scores": [],
                "score": None,
            }
        )

        session[
            "curriculum_scores"
        ][key]["scores"].append(
            score
        )

        day_scores = session[
            "curriculum_scores"
        ][key]["scores"]

        session[
            "curriculum_scores"
        ][key]["score"] = round(
            sum(day_scores)
            / len(day_scores)
        )


    # =====================================================
    # TOPIC STATISTICS
    # =====================================================

    session[
        "topics"
    ].setdefault(
        current_topic,
        {
            "attempts": 0,
            "last_score": None,
            "last_difficulty":
                current_difficulty,
        }
    )


    session[
        "topics"
    ][current_topic][
        "attempts"
    ] += 1


    session[
        "topics"
    ][current_topic][
        "last_score"
    ] = score


    session[
        "topics"
    ][current_topic][
        "last_difficulty"
    ] = current_difficulty


    # =====================================================
    # SAVE HISTORY
    # =====================================================

    session[
        "history"
    ].append({

        "question_number":
            current_number,

        "question":
            current_question,

        "curriculum_day":
            current_day,

        "curriculum_title":
            get_curriculum_day(
                current_day
            ).get("title", "")
            if current_day
            else "",

        "topic":
            current_topic,

        "difficulty":
            current_difficulty,

        "candidate_message":
            message,

        "evaluation":
            evaluation,

    })

    save_sessions()


    # =====================================================
    # INTERVIEW COMPLETE?
    # =====================================================

    if current_number >= TOTAL_QUESTIONS:

        session[
            "completed"
        ] = True


        result = generate_final_result(
            session
        )

        feedback = build_final_feedback(
            session,
            result
        )

        save_sessions()


        return {

            "reply":
                "Interview completed.",

            "done":
                True,

            "feedback":
                feedback,

            "result":
                result,

        }


    # =====================================================
    # NEXT DIFFICULTY
    # =====================================================

    next_difficulty = (
        difficulty_for_question(
            score,
            session[
                "candidate"
            ].get(
                "yearsExperience",
                0
            )
        )
    )


    # =====================================================
    # FOLLOW-UP DECISION
    # =====================================================

    next_question = None


    if (
        session[
            "follow_up_count"
        ] < MAX_FOLLOW_UPS
    ):

        # Follow-up for answers that show enough
        # understanding to explore the topic further.
        if score >= 50:

            follow_up = (
                select_follow_up_question(
                    current_topic,
                    session[
                        "asked_questions"
                    ]
                )
            )


            if follow_up:

                next_question = {

                    "day":
                        current_day,

                    "topic":
                        current_topic,

                    "question":
                        follow_up,

                    "difficulty":
                        next_difficulty,

                    "curriculum_title":
                        get_curriculum_day(
                            current_day
                        ).get("title", "")
                        if current_day
                        else "",

                    "curriculum_type":
                        get_curriculum_day(
                            current_day
                        ).get("type", "")
                        if current_day
                        else "",

                }

                session[
                    "follow_up_count"
                ] += 1


    # =====================================================
    # WEAK ANSWER → SAME CURRICULUM AREA FIRST
    # =====================================================

    if next_question is None and score < 50:

        same_day_question = build_question(
            current_day,
            "easy"
        ) if current_day else None


        if (
            same_day_question
            and
            same_day_question[
                "question"
            ] not in session[
                "asked_questions"
            ]
        ):

            next_question = same_day_question


    # =====================================================
    # NORMAL ADAPTIVE QUESTION
    # =====================================================

    if next_question is None:

        next_question = select_next_question(

            session=
                session,

            difficulty=
                next_difficulty,

            preferred_day=None,

        )


    # =====================================================
    # UPDATE SESSION
    # =====================================================

    session[
        "question_number"
    ] += 1

    session[
        "difficulty"
    ] = next_question[
        "difficulty"
    ]

    session[
        "current_topic"
    ] = next_question[
        "topic"
    ]

    session[
        "current_question"
    ] = next_question[
        "question"
    ]

    session[
        "current_day"
    ] = next_question[
        "day"
    ]


    if (
        next_question[
            "question"
        ]
        not in session[
            "asked_questions"
        ]
    ):

        session[
            "asked_questions"
        ].append(
            next_question[
                "question"
            ]
        )

    save_sessions()


    # =====================================================
    # RETURN NEXT QUESTION
    # =====================================================

    return {

        "reply":
            next_question[
                "question"
            ],

        "done":
            False,

        "difficulty":
            next_question[
                "difficulty"
            ],

        "topic":
            next_question[
                "topic"
            ],

        "curriculumDay":
            next_question[
                "day"
            ],

        "curriculumTitle":
            next_question[
                "curriculum_title"
            ],

    }


# =========================================================
# SESSION STATUS
# =========================================================

@app.get(
    "/api/interview/{session_id}"
)
def get_interview_session(
    session_id: str
):
    """
    Lightweight session status endpoint.
    Useful for checking whether a session exists after a
    development-server reload.
    """

    if session_id not in sessions:
        return {
            "sessionId": session_id,
            "exists": False,
            "error": "Session not found",
        }

    session = sessions[session_id]

    return {
        "sessionId": session_id,
        "exists": True,
        "candidate": session.get("candidate"),
        "questionNumber": session.get("question_number"),
        "currentQuestion": session.get("current_question"),
        "currentTopic": session.get("current_topic"),
        "currentDay": session.get("current_day"),
        "completed": session.get("completed"),
        "curriculumDaysCovered": session.get(
            "curriculum_days_covered",
            []
        ),
    }


# =========================================================
# INTERVIEW HISTORY
# =========================================================

@app.get(
    "/api/interview/{session_id}/history"
)
def get_interview_history(
    session_id: str
):

    if session_id not in sessions:

        return {
            "error":
                "Session not found"
        }


    session = sessions[
        session_id
    ]


    return {

        "sessionId":
            session_id,

        "candidate":
            session[
                "candidate"
            ],

        "questionNumber":
            session[
                "question_number"
            ],

        "currentQuestion":
            session[
                "current_question"
            ],

        "currentTopic":
            session[
                "current_topic"
            ],

        "currentDay":
            session[
                "current_day"
            ],

        "difficulty":
            session[
                "difficulty"
            ],

        "completed":
            session[
                "completed"
            ],

        "followUpCount":
            session[
                "follow_up_count"
            ],

        "curriculumDaysCovered":
            session[
                "curriculum_days_covered"
            ],

        "askedQuestions":
            session[
                "asked_questions"
            ],

        "history":
            session[
                "history"
            ],

        "topics":
            session[
                "topics"
            ],

    }


# =========================================================
# FINAL RESULT ENDPOINT
# =========================================================

@app.get(
    "/api/interview/{session_id}/result"
)
def get_interview_result(
    session_id: str
):

    if session_id not in sessions:

        return {
            "error":
                "Session not found"
        }


    session = sessions[
        session_id
    ]


    result = generate_final_result(
        session
    )

    feedback = build_final_feedback(
        session,
        result
    )

    save_sessions()


    return {

        "sessionId":
            session_id,

        "interviewCompleted":
            session[
                "completed"
            ],

        "result":
            result,

        "feedback":
            feedback,

    }