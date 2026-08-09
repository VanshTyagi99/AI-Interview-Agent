/* =========================================================
   AI INTERVIEW AGENT
   Phase 3.5 Frontend Controller
   ========================================================= */

"use strict";

/* =========================================================
   CONFIG
========================================================= */

const API_BASE_URL = "http://127.0.0.1:8000";
const INTERVIEW_ENDPOINT = `${API_BASE_URL}/api/interview`;

const TOTAL_QUESTIONS = 8;
const SESSION_STORAGE_KEY = "aiInterviewAgentSession";


/* =========================================================
   APPLICATION STATE
========================================================= */

const state = {
    sessionId: "",
    candidate: null,

    questionNumber: 0,
    currentQuestion: "",
    currentTopic: "general",
    currentDifficulty: "easy",
    currentCurriculumDay: null,

    completed: false,
    history: [],

    lastResponse: null,
    isRequestInProgress: false
};


/* =========================================================
   DOM REFERENCES
========================================================= */

const startScreen = document.getElementById("startScreen");
const interviewScreen = document.getElementById("interviewScreen");
const resultScreen = document.getElementById("resultScreen");

const candidateForm = document.getElementById("candidateForm");
const answerForm = document.getElementById("answerForm");

const candidateIdInput = document.getElementById("candidateId");
const candidateNameInput = document.getElementById("candidateName");
const jobRoleInput = document.getElementById("jobRole");
const experienceInput = document.getElementById("experience");

const startInterviewBtn = document.getElementById("startInterviewBtn");
const submitAnswerBtn = document.getElementById("submitAnswerBtn");
const restartInterviewBtn = document.getElementById("restartInterviewBtn");

const startError = document.getElementById("startError");
const answerError = document.getElementById("answerError");

const connectionStatus = document.getElementById("connectionStatus");

const activeCandidateName =
    document.getElementById("activeCandidateName");

const activeCandidateId =
    document.getElementById("activeCandidateId");

const activeSessionId =
    document.getElementById("activeSessionId");

const progressText =
    document.getElementById("progressText");

const progressBar =
    document.getElementById("progressBar");

const questionNumberElement =
    document.getElementById("questionNumber");

const questionTitle =
    document.getElementById("questionTitle");

const topicBadge =
    document.getElementById("topicBadge");

const difficultyBadge =
    document.getElementById("difficultyBadge");

const answerInput =
    document.getElementById("answerInput");

const wordCounter =
    document.getElementById("wordCounter");

const loadingState =
    document.getElementById("loadingState");

const evaluationPanel =
    document.getElementById("evaluationPanel");

const evaluationScore =
    document.getElementById("evaluationScore");

const evaluationFeedback =
    document.getElementById("evaluationFeedback");


/* ================= RESULT DOM ================= */

const overallScore =
    document.getElementById("overallScore");

const performanceBadge =
    document.getElementById("performanceBadge");

const totalQuestions =
    document.getElementById("totalQuestions");

const completionPercentage =
    document.getElementById("completionPercentage");

const curriculumDayCount =
    document.getElementById("curriculumDayCount");

const resultSummary =
    document.getElementById("resultSummary");

const strengthsList =
    document.getElementById("strengthsList");

const weakAreasList =
    document.getElementById("weakAreasList");

const topicScores =
    document.getElementById("topicScores");

const recommendationText =
    document.getElementById("recommendationText");

const nextStepsList =
    document.getElementById("nextStepsList");

const toast =
    document.getElementById("toast");

const toastMessage =
    document.getElementById("toastMessage");


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    setupEventListeners();

    updateConnectionStatus("Ready");
    updateWordCounter();
    restoreSession();

    // Check backend availability without blocking the UI.
    checkBackendHealth();

});


/* =========================================================
   EVENT LISTENERS
========================================================= */

function setupEventListeners() {

    if (candidateForm) {
        candidateForm.addEventListener(
            "submit",
            handleStartInterview
        );
    }

    if (answerForm) {
        answerForm.addEventListener(
            "submit",
            handleSubmitAnswer
        );
    }

    if (answerInput) {
        answerInput.addEventListener(
            "input",
            updateWordCounter
        );
    }

    if (restartInterviewBtn) {
        restartInterviewBtn.addEventListener(
            "click",
            restartInterview
        );
    }

}


/* =========================================================
   START INTERVIEW
========================================================= */

async function handleStartInterview(event) {

    event.preventDefault();

    clearError(startError);

    const candidateId =
        candidateIdInput.value.trim();

    const candidateName =
        candidateNameInput.value.trim();

    const jobRole =
        jobRoleInput.value.trim() || "AI Candidate";

    const yearsExperience =
        Number(experienceInput.value || 0);


    /* ---------------- VALIDATION ---------------- */

    if (!candidateId) {
        showError(
            startError,
            "Please enter a Candidate ID."
        );

        candidateIdInput.focus();
        return;
    }


    if (!candidateName) {
        showError(
            startError,
            "Please enter the candidate name."
        );

        candidateNameInput.focus();
        return;
    }


    if (
        Number.isNaN(yearsExperience) ||
        yearsExperience < 0
    ) {
        showError(
            startError,
            "Please enter a valid experience value."
        );

        experienceInput.focus();
        return;
    }


    /* ---------------- STATE ---------------- */

    state.sessionId = candidateId;

    state.candidate = {
        id: candidateId,
        name: candidateName,
        jobRole: jobRole,
        yearsExperience: yearsExperience,
        education: "",
        status: "ACTIVE"
    };

    state.questionNumber = 0;
    state.currentQuestion = "";
    state.currentTopic = "general";
    state.currentDifficulty = "easy";
    state.currentCurriculumDay = null;
    state.completed = false;
    state.history = [];
    state.lastResponse = null;


    saveSession();


    /* ---------------- UI ---------------- */

    setButtonLoading(
        startInterviewBtn,
        true,
        "Starting..."
    );

    state.isRequestInProgress = true;
    updateConnectionStatus("Connecting");


    try {

        /*
         * First request:
         *
         * message = empty string
         *
         * Backend should return the first question.
         */

        let response = await sendInterviewRequest({
            sessionId: state.sessionId,
            message: "",
            candidate: state.candidate
        });

        /*
         * Some backend versions return the answer-validation message when
         * the initial message is empty. Retry once with an explicit start
         * message so the frontend can work with either behavior.
         */
        if (isInvalidQuestionResponse(response)) {
            response = await sendInterviewRequest({
                sessionId: state.sessionId,
                message: "start interview",
                candidate: state.candidate
            });
        }

        handleInterviewResponse(response);


    } catch (error) {

        console.error(
            "Start interview error:",
            error
        );

        showError(
            startError,
            getReadableError(error)
        );

        updateConnectionStatus(
            isNetworkError(error) ? "Offline" : "Error"
        );

    } finally {

        state.isRequestInProgress = false;

        setButtonLoading(
            startInterviewBtn,
            false,
            "Start Interview"
        );

    }

}


/* =========================================================
   SUBMIT ANSWER
========================================================= */

async function handleSubmitAnswer(event) {

    event.preventDefault();

    clearError(answerError);

    const answer =
        answerInput.value.trim();


    if (!answer) {

        showError(
            answerError,
            "Please enter your answer before submitting."
        );

        answerInput.focus();
        return;
    }


    if (!state.sessionId) {

        showError(
            answerError,
            "Interview session not found. Please restart the interview."
        );

        return;
    }


    setButtonLoading(
        submitAnswerBtn,
        true,
        "Evaluating..."
    );

    state.isRequestInProgress = true;
    showLoading(true);
    updateConnectionStatus("Evaluating");


    try {

        const response =
            await sendInterviewRequest({
                sessionId: state.sessionId,
                message: answer,
                candidate: state.candidate
            });


        /*
         * Save current answer locally.
         */

        state.history.push({
            questionNumber: state.questionNumber,
            question: state.currentQuestion,
            topic: state.currentTopic,
            difficulty: state.currentDifficulty,
            curriculumDay: state.currentCurriculumDay,
            answer: answer
        });


        handleInterviewResponse(response);


    } catch (error) {

        console.error(
            "Submit answer error:",
            error
        );

        showError(
            answerError,
            getReadableError(error)
        );

        updateConnectionStatus("Error");

    } finally {

        state.isRequestInProgress = false;
        showLoading(false);

        setButtonLoading(
            submitAnswerBtn,
            false,
            "Submit Answer"
        );

    }

}


/* =========================================================
   API REQUEST
========================================================= */

async function sendInterviewRequest(payload) {

    const response = await fetch(
        INTERVIEW_ENDPOINT,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },

            body: JSON.stringify(payload)
        }
    );


    let data = null;


    try {
        data = await response.json();
    } catch {
        data = null;
    }


    if (!response.ok) {

        const detail =
            data?.detail ||
            data?.message ||
            data?.error ||
            `Server returned HTTP ${response.status}.`;

        const readableDetail =
            typeof detail === "string"
                ? detail
                : JSON.stringify(detail);

        throw new Error(readableDetail);
    }


    return data;
}


/* =========================================================
   HANDLE INTERVIEW RESPONSE
========================================================= */

function handleInterviewResponse(response) {

    if (!response || typeof response !== "object") {
        throw new Error(
            "Empty or invalid response received from server."
        );
    }

    state.lastResponse = response;

    /*
     * Supported backend response shapes:
     *
     * {
     *   reply: "Question...",
     *   question: "Question...",
     *   nextQuestion: "Question...",
     *   done: false,
     *   difficulty: "easy",
     *   topic: "Embeddings",
     *   curriculumDay: 7
     * }
     *
     * The backend currently uses "reply", but the fallbacks
     * make the frontend safer if the response model evolves.
     */

    if (response.done === true) {
        state.completed = true;
        showFinalResult(response);
        updateConnectionStatus("Completed");
        saveSession();
        return;
    }

    const question = extractQuestionText(response);

    if (!question) {
        throw new Error(
            "Server did not return a valid interview question. " +
            "Check the POST /api/interview response in Swagger."
        );
    }

    /*
     * The first question must be QUESTION 01.
     * Every following non-completed response advances by one.
     */
    const backendQuestionNumber =
        Number(
            response.questionNumber ??
            response.question_number ??
            response.data?.questionNumber ??
            response.data?.question_number
        );

    if (
        Number.isFinite(backendQuestionNumber) &&
        backendQuestionNumber >= 1
    ) {
        state.questionNumber = Math.min(
            backendQuestionNumber,
            TOTAL_QUESTIONS
        );
    } else {
        state.questionNumber = Math.min(
            Math.max(state.questionNumber + 1, 1),
            TOTAL_QUESTIONS
        );
    }

    state.currentQuestion = question;

    const payload =
        response.data &&
        typeof response.data === "object"
            ? response.data
            : response;

    state.currentTopic =
        payload.topic ||
        payload.currentTopic ||
        "general";

    state.currentDifficulty =
        payload.difficulty ||
        payload.currentDifficulty ||
        "easy";

    state.currentCurriculumDay =
        payload.curriculumDay ??
        payload.currentCurriculumDay ??
        null;

    showInterviewScreen();
    renderQuestion({
        ...response,
        ...(
            response.data &&
            typeof response.data === "object"
                ? response.data
                : {}
        )
    });

    updateConnectionStatus("Interview Active");
    saveSession();
}


/* =========================================================
   RENDER QUESTION
========================================================= */

function renderQuestion(response) {

    if (!questionTitle) {
        throw new Error(
            "Question element #questionTitle was not found in index.html."
        );
    }

    const number =
        state.questionNumber;


    const percentage =
        Math.min(
            (number / TOTAL_QUESTIONS) * 100,
            100
        );


    /* ---------------- QUESTION ---------------- */

    // IMPORTANT: only the actual backend question is rendered here.
    // Validation text belongs to answerError, never to questionTitle.
    questionTitle.textContent =
        state.currentQuestion;


    questionNumberElement.textContent =
        `QUESTION ${String(number).padStart(2, "0")}`;


    /* ---------------- TOPIC ---------------- */

    topicBadge.textContent =
        formatTopic(state.currentTopic);


    /* ---------------- DIFFICULTY ---------------- */

    difficultyBadge.textContent =
        capitalize(state.currentDifficulty);


    difficultyBadge.classList.remove(
        "easy",
        "medium",
        "hard"
    );

    difficultyBadge.classList.add(
        String(state.currentDifficulty).toLowerCase()
    );


    /* ---------------- PROGRESS ---------------- */

    progressText.textContent =
        `Question ${number} of ${TOTAL_QUESTIONS}`;


    progressBar.style.width =
        `${percentage}%`;


    /* ---------------- CANDIDATE ---------------- */

    if (state.candidate) {

        if (activeCandidateName) {
            activeCandidateName.textContent =
                state.candidate.name ||
                "Candidate";
        }

        if (activeCandidateId) {
            activeCandidateId.textContent =
                state.candidate.id ||
                "—";
        }
    }

    if (activeSessionId) {
        activeSessionId.textContent =
            state.sessionId || "—";
    }


    /* ---------------- ANSWER ---------------- */

    answerInput.value = "";

    clearError(answerError);

    updateWordCounter();


    /*
     * Backend may send feedback for the previous answer.
     * If available, show it briefly.
     */

    renderEvaluation(response);


    setTimeout(() => {

        answerInput.focus();

    }, 100);

}


/* =========================================================
   EVALUATION FEEDBACK
========================================================= */

function renderEvaluation(response) {

    const feedback =
        response?.feedback;


    /*
     * Do not display an empty evaluation panel.
     */

    if (!feedback) {

        evaluationPanel.classList.add(
            "hidden"
        );

        return;
    }


    if (evaluationPanel) {
        evaluationPanel.classList.remove(
            "hidden"
        );
    }


    if (typeof feedback === "string") {

        if (evaluationFeedback) {
            evaluationFeedback.textContent = feedback;
        }

        if (evaluationScore) {
            evaluationScore.textContent = "Feedback";
        }

        return;
    }


    if (typeof feedback === "object") {

        if (evaluationFeedback) {
            evaluationFeedback.textContent =
                feedback.summary ||
                feedback.feedback ||
                "Answer evaluated.";
        }

        const score =
            feedback.score ??
            feedback.overall_score;

        if (evaluationScore) {
            evaluationScore.textContent =
                score !== undefined
                    ? `${score}/100`
                    : "Evaluated";
        }
    }

}


/* =========================================================
   FINAL RESULT
========================================================= */

function showFinalResult(response) {

    const result =
        response.result ||
        {};

    const feedback =
        response.feedback ||
        {};


    if (!resultScreen) {
        throw new Error(
            "Result screen #resultScreen was not found in index.html."
        );
    }

    showScreen(resultScreen);


    /* ---------------- SCORE ---------------- */

    const score =
        result.overall_score ??
        result.score ??
        0;


    overallScore.textContent =
        Math.round(Number(score) || 0);


    /* ---------------- PERFORMANCE ---------------- */

    const performance =
        result.performance ||
        "unknown";


    performanceBadge.textContent =
        capitalize(performance);


    performanceBadge.classList.remove(
        "good",
        "average",
        "weak"
    );

    performanceBadge.classList.add(
        String(performance).toLowerCase()
    );


    /* ---------------- STATS ---------------- */

    totalQuestions.textContent =
        result.total_questions ??
        state.questionNumber ??
        TOTAL_QUESTIONS;


    completionPercentage.textContent =
        `${result.completion_percentage ?? 100}%`;


    curriculumDayCount.textContent =
        result.curriculum_day_count ??
        (
            Array.isArray(result.curriculum_days_covered)
                ? result.curriculum_days_covered.length
                : 0
        );


    /* ---------------- SUMMARY ---------------- */

    resultSummary.textContent =
        feedback.summary ||
        result.recommendation ||
        `Interview completed with an overall score of ${score}/100.`;


    /* ---------------- STRENGTHS ---------------- */

    renderList(
        strengthsList,
        result.strengths ||
        feedback.strengths ||
        []
    );


    /* ---------------- WEAK AREAS ---------------- */

    renderList(
        weakAreasList,
        result.weak_areas ||
        feedback.gaps ||
        []
    );


    /* ---------------- TOPICS ---------------- */

    renderTopicScores(
        result.topic_scores ||
        {}
    );


    /* ---------------- RECOMMENDATION ---------------- */

    recommendationText.textContent =
        result.recommendation ||
        feedback.summary ||
        "Continue strengthening the concepts covered during the interview.";


    /* ---------------- NEXT STEPS ---------------- */

    renderList(
        nextStepsList,
        feedback.next ||
        []
    );


    updateConnectionStatus("Completed");

    clearStoredSession();

}


/* =========================================================
   RESULT LIST RENDERER
========================================================= */

function renderList(container, items) {

    if (!container) {
        return;
    }


    container.innerHTML = "";


    const values =
        Array.isArray(items)
            ? items
            : [];


    if (values.length === 0) {

        const li =
            document.createElement("li");

        li.textContent =
            "No data available.";

        container.appendChild(li);

        return;
    }


    values.forEach(item => {

        const li =
            document.createElement("li");

        li.textContent =
            typeof item === "string"
                ? item
                : JSON.stringify(item);

        container.appendChild(li);

    });

}


/* =========================================================
   TOPIC SCORE RENDERER
========================================================= */

function renderTopicScores(scores) {

    if (!topicScores) {
        return;
    }


    topicScores.innerHTML = "";


    const entries =
        Object.entries(scores || {});


    if (entries.length === 0) {

        const empty =
            document.createElement("p");

        empty.textContent =
            "No topic performance data available.";

        empty.style.color =
            "var(--text-muted)";

        empty.style.fontSize =
            "12px";

        topicScores.appendChild(empty);

        return;
    }


    entries.forEach(([topic, data]) => {

        const score =
            Number(
                data?.score ??
                data?.overall_score ??
                0
            );


        const row =
            document.createElement("div");

        row.className =
            "topic-score-row";


        const name =
            document.createElement("div");

        name.className =
            "topic-score-name";

        name.textContent =
            topic;


        const track =
            document.createElement("div");

        track.className =
            "topic-score-track";


        const fill =
            document.createElement("div");

        fill.className =
            "topic-score-fill";

        fill.style.width =
            `${Math.max(0, Math.min(score, 100))}%`;


        const value =
            document.createElement("div");

        value.className =
            "topic-score-value";

        value.textContent =
            `${Math.round(score)}`;


        track.appendChild(fill);

        row.appendChild(name);
        row.appendChild(track);
        row.appendChild(value);

        topicScores.appendChild(row);

    });

}


/* =========================================================
   SCREEN MANAGEMENT
========================================================= */

function showScreen(screen) {

    if (!screen) {
        throw new Error("Requested screen element was not found.");
    }

    if (startScreen) {
        startScreen.classList.add("hidden");
    }

    if (interviewScreen) {
        interviewScreen.classList.add("hidden");
    }

    if (resultScreen) {
        resultScreen.classList.add("hidden");
    }

    screen.classList.remove("hidden");


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


function showInterviewScreen() {

    showScreen(interviewScreen);

}


/* =========================================================
   LOADING
========================================================= */

function showLoading(show) {

    if (!loadingState) {
        return;
    }


    loadingState.classList.toggle(
        "hidden",
        !show
    );

}


/* =========================================================
   BUTTON LOADING
========================================================= */

function setButtonLoading(
    button,
    loading,
    text
) {

    if (!button) {
        return;
    }


    if (loading) {

        button.disabled = true;

        button.dataset.originalText =
            button.querySelector("span")?.textContent ||
            button.textContent.trim() ||
            text;

        const label =
            button.querySelector("span");

        if (label) {
            label.textContent = text;
        }

        return;
    }


    button.disabled = false;

    const label =
        button.querySelector("span");

    if (label) {
        label.textContent =
            text;
    }

}


/* =========================================================
   WORD COUNTER
========================================================= */

function updateWordCounter() {

    if (!wordCounter || !answerInput) {
        return;
    }


    const text =
        answerInput.value.trim();


    if (!text) {

        wordCounter.textContent =
            "0 words";

        return;
    }


    const words =
        text
            .split(/\s+/)
            .filter(Boolean);


    wordCounter.textContent =
        `${words.length} ${words.length === 1 ? "word" : "words"}`;

}


/* =========================================================
   ERROR HANDLING
========================================================= */

function showError(element, message) {

    if (!element) {
        return;
    }


    element.textContent =
        message || "Something went wrong.";

    element.classList.remove(
        "hidden"
    );

}


function clearError(element) {

    if (!element) {
        return;
    }


    element.textContent = "";

    element.classList.add(
        "hidden"
    );

}


/* =========================================================
   CONNECTION STATUS
========================================================= */

function updateConnectionStatus(status) {

    if (!connectionStatus) {
        return;
    }


    connectionStatus.textContent =
        status;


    const dot =
        document.querySelector(".status-dot");


    if (!dot) {
        return;
    }


    dot.style.background =
        getStatusColor(status);

}


function getStatusColor(status) {

    const normalized =
        String(status).toLowerCase();


    if (
        normalized.includes("error") ||
        normalized.includes("offline")
    ) {
        return "#ff6577";
    }


    if (
        normalized.includes("evaluat") ||
        normalized.includes("connect")
    ) {
        return "#f5c451";
    }


    if (
        normalized.includes("complete") ||
        normalized.includes("active")
    ) {
        return "#39d98a";
    }


    return "#39d98a";
}


/* =========================================================
   TOAST
========================================================= */

let toastTimer = null;


function showToast(message) {

    if (!toast || !toastMessage) {
        return;
    }


    toastMessage.textContent =
        message;


    toast.classList.remove(
        "hidden"
    );


    clearTimeout(toastTimer);


    toastTimer =
        setTimeout(() => {

            toast.classList.add(
                "hidden"
            );

        }, 3500);

}


/* =========================================================
   SESSION STORAGE
========================================================= */

function saveSession() {

    try {

        /*
         * IMPORTANT:
         * The backend writes sessions.json when an interview starts.
         * If the frontend is running through Live Server, that file change
         * can cause the browser to reload. Therefore we persist the ACTIVE
         * interview state, not just the candidate profile.
         */
        localStorage.setItem(
            SESSION_STORAGE_KEY,
            JSON.stringify({
                sessionId: state.sessionId,
                candidate: state.candidate,

                questionNumber: state.questionNumber,
                currentQuestion: state.currentQuestion,
                currentTopic: state.currentTopic,
                currentDifficulty: state.currentDifficulty,
                currentCurriculumDay: state.currentCurriculumDay,

                completed: state.completed,
                history: state.history
            })
        );

    } catch (error) {

        console.warn(
            "Unable to save session:",
            error
        );

    }

}


function restoreSession() {

    try {

        const raw =
            localStorage.getItem(
                SESSION_STORAGE_KEY
            );


        if (!raw) {
            return;
        }


        const saved =
            JSON.parse(raw);


        /*
         * Restore candidate fields.
         */
        if (
            saved?.candidate?.id &&
            candidateIdInput
        ) {

            candidateIdInput.value =
                saved.candidate.id;

        }


        if (
            saved?.candidate?.name &&
            candidateNameInput
        ) {

            candidateNameInput.value =
                saved.candidate.name;

        }


        if (
            saved?.candidate?.jobRole &&
            jobRoleInput
        ) {

            jobRoleInput.value =
                saved.candidate.jobRole;

        }


        if (
            saved?.candidate?.yearsExperience !== undefined &&
            experienceInput
        ) {

            experienceInput.value =
                saved.candidate.yearsExperience;

        }


        /*
         * Restore an ACTIVE interview after a browser/Live Server reload.
         * This is the key fix for the "question appears for 0.01 sec and
         * then the start page returns" issue.
         */
        if (
            saved?.sessionId &&
            saved?.candidate &&
            saved?.currentQuestion &&
            !saved?.completed
        ) {

            state.sessionId =
                saved.sessionId;

            state.candidate =
                saved.candidate;

            state.questionNumber =
                Number(saved.questionNumber || 1);

            state.currentQuestion =
                saved.currentQuestion;

            state.currentTopic =
                saved.currentTopic || "general";

            state.currentDifficulty =
                saved.currentDifficulty || "easy";

            state.currentCurriculumDay =
                saved.currentCurriculumDay ?? null;

            state.completed =
                false;

            state.history =
                Array.isArray(saved.history)
                    ? saved.history
                    : [];

            state.lastResponse = null;

            showInterviewScreen();

            renderQuestion({
                reply: state.currentQuestion,
                question: state.currentQuestion,
                topic: state.currentTopic,
                difficulty: state.currentDifficulty,
                curriculumDay: state.currentCurriculumDay
            });

            updateConnectionStatus("Interview Active");

            return;
        }

    } catch (error) {

        console.warn(
            "Unable to restore session:",
            error
        );

    }

}


function clearStoredSession() {

    try {

        localStorage.removeItem(
            SESSION_STORAGE_KEY
        );

    } catch (error) {

        console.warn(
            "Unable to clear local session:",
            error
        );

    }

}


/* =========================================================
   RESTART
========================================================= */

function restartInterview() {

    state.sessionId = "";
    state.candidate = null;

    state.questionNumber = 0;
    state.currentQuestion = "";
    state.currentTopic = "general";
    state.currentDifficulty = "easy";
    state.currentCurriculumDay = null;

    state.completed = false;
    state.history = [];
    state.lastResponse = null;


    clearStoredSession();


    if (candidateForm) {
        candidateForm.reset();
    }


    if (jobRoleInput) {
        jobRoleInput.value =
            "AI Candidate";
    }


    if (experienceInput) {
        experienceInput.value =
            "0";
    }


    if (answerInput) {
        answerInput.value = "";
    }


    updateWordCounter();

    clearError(startError);
    clearError(answerError);


    if (evaluationPanel) {
        evaluationPanel.classList.add(
            "hidden"
        );
    }


    updateConnectionStatus("Ready");

    showScreen(startScreen);

}


/* =========================================================
   HELPERS
========================================================= */

function formatTopic(topic) {

    const value =
        String(topic || "general")
            .trim();


    if (!value) {
        return "General";
    }


    return value
        .replace(/_/g, " ")
        .replace(/\s+/g, " ")
        .replace(/\b\w/g, char =>
            char.toUpperCase()
        );

}


function capitalize(value) {

    const text =
        String(value || "");


    if (!text) {
        return "";
    }


    return (
        text.charAt(0).toUpperCase() +
        text.slice(1)
    );

}


function extractQuestionText(response) {

    /*
     * Phase 3.5 normally returns:
     * {
     *   reply: "What are embeddings ...?",
     *   done: false,
     *   difficulty: "easy",
     *   topic: "Embeddings",
     *   curriculumDay: 7
     * }
     */

    const candidates = [
        response?.question,
        response?.nextQuestion,
        response?.reply,
        response?.currentQuestion,
        response?.data?.question,
        response?.data?.nextQuestion,
        response?.data?.reply,
        response?.result?.question
    ];

    for (const value of candidates) {

        const text =
            typeof value === "string"
                ? value.trim()
                : "";

        if (!text) {
            continue;
        }

        if (isAnswerValidationMessage(text)) {
            continue;
        }

        return text;
    }

    return "";
}


function isAnswerValidationMessage(value) {

    const normalized =
        String(value || "")
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();

    const blockedMessages = [
        "please provide your answer before continuing.",
        "please provide your answer before continuing",
        "please provide an answer before continuing.",
        "please provide an answer before continuing"
    ];

    return blockedMessages.includes(normalized);
}


function isInvalidQuestionResponse(response) {

    if (!response || typeof response !== "object") {
        return true;
    }

    if (response.done === true) {
        return false;
    }

    return !extractQuestionText(response);
}


function isNetworkError(error) {

    const message =
        String(
            error?.message ||
            error ||
            ""
        ).toLowerCase();

    return (
        message.includes("failed to fetch") ||
        message.includes("networkerror") ||
        message.includes("network request failed") ||
        message.includes("load failed")
    );
}


/* =========================================================
   BACKEND HEALTH CHECK
========================================================= */

async function checkBackendHealth() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/health`,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

        if (response.ok) {
            updateConnectionStatus("Ready");
        } else {
            updateConnectionStatus("Offline");
        }

    } catch (error) {

        console.warn(
            "Backend health check failed:",
            error
        );

        updateConnectionStatus("Offline");
    }

}


/* =========================================================
   ERROR HANDLING
========================================================= */

function getReadableError(error) {

    if (!error) {
        return "Something went wrong.";
    }


    const message =
        String(
            error.message ||
            error
        );


    if (
        message.includes("Failed to fetch") ||
        message.includes("NetworkError")
    ) {

        return (
            "Unable to connect to the backend. " +
            "Make sure FastAPI is running on http://127.0.0.1:8000."
        );

    }


    if (
        message.includes("404")
    ) {

        return (
            "Interview API was not found. " +
            "Check that POST /api/interview exists in the backend."
        );

    }


    if (
        message.includes("500")
    ) {

        return (
            "Backend returned an internal server error. " +
            "Check the FastAPI terminal for the actual error."
        );

    }


    return message;

}


/* =========================================================
   DEBUG HELPER
========================================================= */

window.AIInterviewAgent = {
    state,
    restartInterview,
    showToast
};