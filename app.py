import streamlit as st
import pandas as pd
import sqlite3
import os
import time
import json
from dotenv import load_dotenv
from openai import OpenAI
import plotly.express as px
from streamlit_autorefresh import st_autorefresh


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PrepAI",
    page_icon="🤖",
    layout="wide"
)

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if API_KEY:
    client = OpenAI(api_key=API_KEY)
else:
    client = None


# ============================================================
# PREPAI CUSTOM UI
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(91, 52, 255, 0.18), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(0, 153, 255, 0.15), transparent 30%),
        linear-gradient(135deg, #050b1f 0%, #0b1230 50%, #09051f 100%);
    color: white;
}

section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #071027 0%, #080b20 100%);
    border-right: 1px solid rgba(130, 100, 255, 0.25);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p {
    color: white;
}

section[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 10px;
    margin: 5px 0;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: linear-gradient(
        90deg,
        rgba(81, 69, 255, 0.45),
        rgba(150, 60, 255, 0.35)
    );
}

h1 {
    font-weight: 800 !important;
    background: linear-gradient(
        90deg,
        #ffffff,
        #a98cff,
        #6ab7ff
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

h2, h3 {
    color: #ffffff !important;
}

.prepai-card {
    background:
        linear-gradient(
            135deg,
            rgba(35, 45, 100, 0.72),
            rgba(31, 15, 70, 0.72)
        );

    border: 1px solid rgba(145, 105, 255, 0.35);
    border-radius: 22px;
    padding: 28px;
    margin: 15px 0;

    box-shadow:
        0 10px 40px rgba(0,0,0,0.35),
        inset 0 1px 1px rgba(255,255,255,0.05);
}

.question-card {
    background:
        linear-gradient(
            135deg,
            rgba(15, 25, 65, 0.95),
            rgba(26, 15, 65, 0.95)
        );

    border: 1px solid rgba(117, 93, 255, 0.6);
    border-radius: 18px;
    padding: 28px;
    margin-top: 15px;

    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.question-label {
    color: #a993ff;
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.question-text {
    font-size: 23px;
    font-weight: 700;
    color: white;
    margin-top: 10px;
}

.answer-card {
    background:
        linear-gradient(
            135deg,
            rgba(10, 18, 48, 0.96),
            rgba(20, 12, 50, 0.96)
        );

    border: 1px solid rgba(120, 95, 255, 0.5);
    border-radius: 20px;

    padding: 25px;
    margin-top: 18px;

    box-shadow:
        0 15px 40px rgba(0,0,0,0.35);
}

textarea {
    background-color: #080f27 !important;
    color: #f7f5ff !important;

    border: 1px solid #6652d9 !important;
    border-radius: 15px !important;

    font-size: 16px !important;
    line-height: 1.7 !important;

    padding: 18px !important;

    min-height: 220px !important;

    box-shadow:
        inset 0 0 20px rgba(80,60,200,0.12);
}

textarea:focus {
    border: 2px solid #8d6bff !important;

    box-shadow:
        0 0 20px rgba(110, 70, 255, 0.3) !important;
}

.stButton > button {
    border-radius: 13px !important;

    border: 1px solid rgba(140,110,255,0.6) !important;

    background:
        linear-gradient(
            90deg,
            #4c5cff,
            #8b35f4
        ) !important;

    color: white !important;

    font-weight: 700 !important;
    font-size: 15px !important;

    padding: 12px 20px !important;

    transition: all 0.25s ease !important;

    box-shadow:
        0 8px 25px rgba(85,55,255,0.25);
}

.stButton > button:hover {
    transform: translateY(-2px);

    box-shadow:
        0 12px 35px rgba(120,70,255,0.45);

    border-color: #b79cff !important;
}

div[data-testid="stProgress"] > div > div {
    background:
        linear-gradient(
            90deg,
            #4d61ff,
            #9a42ff
        ) !important;
}

div[data-testid="stMetric"] {
    background:
        linear-gradient(
            135deg,
            rgba(35, 40, 100, 0.7),
            rgba(45, 20, 90, 0.7)
        );

    border: 1px solid rgba(130,100,255,0.3);
    border-radius: 15px;
    padding: 15px;
}

div[data-testid="stAlert"] {
    border-radius: 14px;
}

div[data-baseweb="select"] > div {
    background-color: #10183b !important;
    border: 1px solid #6652d9 !important;
    border-radius: 12px !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE
# ============================================================

DB_PATH = "database/prepai.db"

os.makedirs("database", exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aptitude_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER,
            total INTEGER,
            percentage REAL,
            quantitative REAL,
            logical REAL,
            verbal REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_type TEXT,
            overall_score REAL,
            technical_score REAL,
            communication_score REAL,
            relevance_score REAL,
            clarity_score REAL,
            feedback TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


initialize_database()


# ============================================================
# LOAD QUESTIONS
# ============================================================

@st.cache_data
def load_questions():

    return pd.read_csv(
        "data/aptitude_questions.csv"
    )


questions = load_questions()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {

    "page": "Home",

    "test_started": False,
    "current_question": 0,
    "score": 0,
    "answers": [],
    "test_start_time": None,
    "test_finished": False,

    "interview_started": False,
    "interview_question": 0,
    "interview_questions": [],
    "interview_answers": [],
    "interview_scores": [],
    "interview_feedback": [],
    "interview_finished": False,

    "interview_type": "HR Interview",
    "interview_result_saved": False,
}


for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# SAVE APTITUDE RESULT
# ============================================================

def save_aptitude_result(
    score,
    total,
    percentage,
    category_scores
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO aptitude_results
        (
            score,
            total,
            percentage,
            quantitative,
            logical,
            verbal
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        score,
        total,
        percentage,
        category_scores.get("Quantitative", 0),
        category_scores.get("Logical", 0),
        category_scores.get("Verbal", 0)
    ))

    conn.commit()
    conn.close()


# ============================================================
# SAVE INTERVIEW RESULT
# ============================================================

def save_interview_result(
    interview_type,
    scores,
    feedback
):

    if not scores:
        return

    overall = sum(
        item["overall"]
        for item in scores
    ) / len(scores)

    technical = sum(
        item["technical"]
        for item in scores
    ) / len(scores)

    communication = sum(
        item["communication"]
        for item in scores
    ) / len(scores)

    relevance = sum(
        item["relevance"]
        for item in scores
    ) / len(scores)

    clarity = sum(
        item["clarity"]
        for item in scores
    ) / len(scores)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interview_results
        (
            interview_type,
            overall_score,
            technical_score,
            communication_score,
            relevance_score,
            clarity_score,
            feedback
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        interview_type,
        overall,
        technical,
        communication,
        relevance,
        clarity,
        json.dumps(feedback)
    ))

    conn.commit()
    conn.close()


# ============================================================
# AI ANSWER EVALUATION
# ============================================================

def evaluate_answer(question, answer):

    if not answer.strip():

        return {
            "overall": 0,
            "technical": 0,
            "communication": 0,
            "relevance": 0,
            "clarity": 0,
            "feedback": "No answer was provided."
        }


    # --------------------------------------------------------
    # AI EVALUATION
    # --------------------------------------------------------

    if client:

        prompt = f"""
You are an expert technical and HR interviewer.

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate the candidate's answer.

Return ONLY valid JSON using this structure:

{{
    "overall": number between 0 and 10,
    "technical": number between 0 and 10,
    "communication": number between 0 and 10,
    "relevance": number between 0 and 10,
    "clarity": number between 0 and 10,
    "feedback": "short useful feedback"
}}

Evaluate fairly for a college student preparing for placements.
"""

        try:

            response = client.chat.completions.create(

                model="gpt-4o-mini",

                messages=[
                    {
                        "role": "system",
                        "content": "You are an interview evaluation assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.3
            )

            content = response.choices[0].message.content

            content = content.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            ).strip()

            result = json.loads(content)

            return result

        except Exception:

            st.warning(
                "AI evaluation failed. Using basic evaluation."
            )


    # --------------------------------------------------------
    # FALLBACK EVALUATION
    # --------------------------------------------------------

    words = len(answer.split())

    if words < 5:

        score = 3

    elif words < 15:

        score = 6

    else:

        score = 8


    return {

        "overall": score,
        "technical": score,
        "communication": score,
        "relevance": score,
        "clarity": score,

        "feedback":
        "Good attempt. Try to give a more structured and detailed answer."
    }


# ============================================================
# INTERVIEW QUESTIONS
# ============================================================

def generate_interview_questions(interview_type):

    question_bank = {

        "HR Interview": [

            "Tell me about yourself.",

            "What are your strengths and weaknesses?",

            "Why should we hire you?",

            "Where do you see yourself in five years?",

            "Tell me about a challenge you faced and how you solved it."

        ],

        "Technical Interview": [

            "What is object-oriented programming?",

            "What is the difference between a stack and a queue?",

            "What is a database?",

            "What is the difference between a primary key and a foreign key?",

            "What is the difference between a process and a thread?"

        ],

        "Python Interview": [

            "What is the difference between a list and a tuple in Python?",

            "What are dictionaries in Python?",

            "What is the difference between == and is in Python?",

            "What is exception handling in Python?",

            "What are functions in Python and why are they useful?"

        ],

        "Data Science Interview": [

            "What is data science?",

            "What is the difference between supervised and unsupervised learning?",

            "What is overfitting?",

            "What is the purpose of data preprocessing?",

            "Explain the difference between classification and regression."

        ]
    }

    return question_bank[interview_type]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🤖 PrepAI")

st.sidebar.write(
    "AI-powered placement preparation"
)

page = st.sidebar.radio(

    "Navigation",

    [
        "Home",
        "Aptitude Test",
        "AI Mock Interview",
        "Dashboard"
    ]
)


# ============================================================
# HOME
# ============================================================

if page == "Home":

    st.title("🤖 PrepAI")

    st.subheader(
        "AI-Powered Mock Interview & Aptitude Platform"
    )

    st.write(
        "Prepare for placements through aptitude tests, "
        "AI-powered mock interviews and personalized performance analysis."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.header("🧮 Aptitude Practice")

        st.write(
            "Practice Quantitative Aptitude, "
            "Logical Reasoning and Verbal Ability."
        )

        if st.button(
            "Start Aptitude Test",
            use_container_width=True
        ):

            st.session_state.page = "Aptitude Test"
            st.rerun()

    with col2:

        st.header("🤖 AI Mock Interview")

        st.write(
            "Practice HR, Technical, Python "
            "and Data Science interviews."
        )

        if st.button(
            "Start AI Interview",
            use_container_width=True
        ):

            st.session_state.page = "AI Mock Interview"
            st.rerun()

    st.divider()

    st.header("✨ Platform Features")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Aptitude Questions",
            len(questions)
        )

    with col2:

        st.metric(
            "Interview Types",
            4
        )

    with col3:

        st.metric(
            "AI Evaluation",
            "Yes"
        )

    with col4:

        st.metric(
            "Performance Tracking",
            "Yes"
        )


# ============================================================
# APTITUDE TEST
# ============================================================

elif page == "Aptitude Test":

    st.title("🧮 Aptitude Test")

    if not st.session_state.test_started:

        st.info(
            "You will have 10 questions to answer."
        )

        st.write(
            "Categories: Quantitative, Logical Reasoning and Verbal Ability"
        )

        st.write(
            "⏱️ Time limit: 10 minutes"
        )

        if st.button(
            "🚀 Start Test",
            use_container_width=True
        ):

            st.session_state.test_started = True

            st.session_state.current_question = 0

            st.session_state.score = 0

            st.session_state.answers = []

            st.session_state.test_start_time = time.time()

            st.session_state.test_finished = False

            st.rerun()


    elif st.session_state.test_finished:

        st.success(
            "🎉 Aptitude Test Completed!"
        )

        score = st.session_state.score

        total = len(questions)

        percentage = (
            score / total
        ) * 100

        st.metric(
            "Final Score",
            f"{score}/{total}"
        )

        st.metric(
            "Percentage",
            f"{percentage:.0f}%"
        )

        if percentage >= 80:

            st.success(
                "🔥 Excellent performance!"
            )

        elif percentage >= 60:

            st.info(
                "👍 Good performance. Keep practicing!"
            )

        else:

            st.warning(
                "💪 You need more practice."
            )

        st.divider()

        st.subheader(
            "📊 Category Performance"
        )

        category_scores = {}

        for category in [
            "Quantitative",
            "Logical",
            "Verbal"
        ]:

            category_answers = [
                a for a in st.session_state.answers
                if a["category"] == category
            ]

            if category_answers:

                correct = sum(
                    a["correct"]
                    for a in category_answers
                )

                category_percentage = (
                    correct /
                    len(category_answers)
                ) * 100

                category_scores[
                    category
                ] = category_percentage

        for category, value in category_scores.items():

            st.write(
                f"**{category}: {value:.0f}%**"
            )

            st.progress(
                int(value)
            )

        save_aptitude_result(
            score,
            total,
            percentage,
            category_scores
        )

        st.divider()

        if st.button(
            "🔄 Take Test Again"
        ):

            st.session_state.test_started = False

            st.session_state.test_finished = False

            st.session_state.current_question = 0

            st.session_state.score = 0

            st.session_state.answers = []

            st.rerun()


    else:

        elapsed = (
            time.time()
            - st.session_state.test_start_time
        )

        remaining = (
            600 - int(elapsed)
        )

        if remaining <= 0:

            st.session_state.test_finished = True

            st.rerun()

        minutes = remaining // 60

        seconds = remaining % 60

        st_autorefresh(
            interval=1000,
            key="aptitude_timer"
        )

        st.warning(
            f"⏱️ Time Remaining: "
            f"{minutes:02d}:{seconds:02d}"
        )

        index = st.session_state.current_question

        question = questions.iloc[index]

        st.progress(
            (index + 1) / len(questions)
        )

        st.write(
            f"### Question {index + 1} "
            f"of {len(questions)}"
        )

        st.caption(
            f"{question['category']} • "
            f"{question['difficulty']}"
        )

        st.subheader(
            question["question"]
        )

        options = [

            question["option_a"],
            question["option_b"],
            question["option_c"],
            question["option_d"]

        ]

        answer = st.radio(
            "Choose your answer:",
            options,
            key=f"answer_{index}"
        )

        if st.button(
            "Next ➡️",
            use_container_width=True
        ):

            selected_index = options.index(
                answer
            )

            selected_letter = chr(
                ord("A") + selected_index
            )

            correct = (
                selected_letter
                ==
                question["correct_answer"]
            )

            if correct:

                st.session_state.score += 1

            st.session_state.answers.append({

                "category":
                question["category"],

                "correct":
                correct

            })

            if index + 1 >= len(questions):

                st.session_state.test_finished = True

            else:

                st.session_state.current_question += 1

            st.rerun()


# ============================================================
# AI MOCK INTERVIEW
# ============================================================

elif page == "AI Mock Interview":

    st.title("🤖 AI Mock Interview")

    st.subheader(
        "Practice. Improve. Get Hired."
    )

    st.write(
        "Answer AI-powered interview questions and receive "
        "instant feedback on your technical knowledge, "
        "communication and clarity."
    )

    st.divider()


    # ========================================================
    # START INTERVIEW
    # ========================================================

    if not st.session_state.interview_started:

        st.header("🎯 Choose Your Interview")

        st.write(
            "Select the type of interview you want to practice. "
            "PrepAI will ask you five questions and evaluate "
            "your answers using AI."
        )

        interview_type = st.selectbox(
            "Interview Type",
            [
                "HR Interview",
                "Technical Interview",
                "Python Interview",
                "Data Science Interview"
            ]
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.markdown("""
            <div class="prepai-card">
            <h3>👔 HR</h3>
            <p style="color:#bbb;">
            Personality, strengths,
            weaknesses and career questions.
            </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:

            st.markdown("""
            <div class="prepai-card">
            <h3>💻 Technical</h3>
            <p style="color:#bbb;">
            Core CS concepts and
            technical interview questions.
            </p>
            </div>
            """, unsafe_allow_html=True)

        with col3:

            st.markdown("""
            <div class="prepai-card">
            <h3>🐍 Python</h3>
            <p style="color:#bbb;">
            Python concepts,
            functions and programming.
            </p>
            </div>
            """, unsafe_allow_html=True)

        with col4:

            st.markdown("""
            <div class="prepai-card">
            <h3>📊 Data Science</h3>
            <p style="color:#bbb;">
            ML, data science and
            analytics concepts.
            </p>
            </div>
            """, unsafe_allow_html=True)


        if st.button(
            "🚀 Start Interview",
            use_container_width=True
        ):

            st.session_state.interview_started = True

            st.session_state.interview_question = 0

            st.session_state.interview_questions = (
                generate_interview_questions(
                    interview_type
                )
            )

            st.session_state.interview_answers = []

            st.session_state.interview_scores = []

            st.session_state.interview_feedback = []

            st.session_state.interview_finished = False

            st.session_state.interview_result_saved = False

            st.session_state.interview_type = interview_type

            st.rerun()


    # ========================================================
    # INTERVIEW FINISHED
    # ========================================================

    elif st.session_state.interview_finished:

        st.success(
            "🎉 Interview Completed!"
        )

        scores = st.session_state.interview_scores

        if scores:

            overall = sum(
                s["overall"]
                for s in scores
            ) / len(scores)

            technical = sum(
                s["technical"]
                for s in scores
            ) / len(scores)

            communication = sum(
                s["communication"]
                for s in scores
            ) / len(scores)

            relevance = sum(
                s["relevance"]
                for s in scores
            ) / len(scores)

            clarity = sum(
                s["clarity"]
                for s in scores
            ) / len(scores)


            st.markdown(
                f"""
                <div class="prepai-card"
                     style="text-align:center;">

                    <h2>YOUR INTERVIEW SCORE</h2>

                    <div style="
                        font-size:60px;
                        font-weight:800;
                        color:white;
                    ">
                        {overall:.1f}
                        <span style="font-size:28px;">
                            /10
                        </span>
                    </div>

                    <p style="color:#bbb;">
                        Keep practicing and improve every attempt 🚀
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )


            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "💻 Technical",
                    f"{technical:.1f}/10"
                )

            with col2:

                st.metric(
                    "🗣️ Communication",
                    f"{communication:.1f}/10"
                )

            with col3:

                st.metric(
                    "🎯 Relevance",
                    f"{relevance:.1f}/10"
                )

            with col4:

                st.metric(
                    "✨ Clarity",
                    f"{clarity:.1f}/10"
                )


            st.divider()

            st.header("💡 AI Feedback")

            for i, feedback in enumerate(
                st.session_state.interview_feedback
            ):

                st.markdown(
                    f"""
                    <div class="question-card">

                        <div class="question-label">
                            QUESTION {i + 1}
                        </div>

                        <div style="
                            color:#ddd;
                            margin-top:12px;
                            font-size:16px;
                        ">
                            {feedback}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # Save result only once

            if not st.session_state.interview_result_saved:

                save_interview_result(
                    st.session_state.interview_type,
                    scores,
                    st.session_state.interview_feedback
                )

                st.session_state.interview_result_saved = True


        st.write("")

        if st.button(
            "🔄 Start New Interview",
            use_container_width=True
        ):

            st.session_state.interview_started = False

            st.session_state.interview_finished = False

            st.session_state.interview_question = 0

            st.session_state.interview_scores = []

            st.session_state.interview_feedback = []

            st.session_state.interview_answers = []

            st.session_state.interview_result_saved = False

            st.rerun()


    # ========================================================
    # ACTIVE INTERVIEW
    # ========================================================

    else:

        index = st.session_state.interview_question

        total_questions = len(
            st.session_state.interview_questions
        )

        question = (
            st.session_state.interview_questions[index]
        )


        progress = (
            (index + 1) /
            total_questions
        )

        st.progress(progress)

        col1, col2 = st.columns([3, 1])

        with col1:

            st.caption(
                f"🤖 {st.session_state.interview_type}"
            )

        with col2:

            st.markdown(
                f"""
                <div style="
                    text-align:right;
                    color:#d5cfff;
                    font-weight:700;
                ">
                    Question {index + 1}/{total_questions}
                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown(
            f"""
            <div class="question-card">

                <div class="question-label">
                    INTERVIEW QUESTION
                </div>

                <div class="question-text">
                    {question}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            """
            <div class="answer-card">

                <h3>✍️ Your Answer</h3>

                <p style="color:#aaa;">
                    Take your time. Give a clear and structured answer.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )


        answer = st.text_area(
            "Your Answer",
            height=250,
            placeholder=(
                "Start typing your answer here...\n\n"
                "💡 Tip: Explain your answer clearly and "
                "use examples whenever possible."
            ),
            key=f"interview_answer_{index}",
            label_visibility="collapsed"
        )


        character_count = len(answer)

        st.markdown(
            f"""
            <div style="
                color:#8e88ad;
                font-size:13px;
                text-align:right;
                margin-top:-10px;
                margin-bottom:15px;
            ">
                ✍️ {character_count}/2000 characters
            </div>
            """,
            unsafe_allow_html=True
        )


        with st.expander("💡 Interview Tips"):

            st.markdown("""
            **Make your answer stronger:**

            ✅ Be clear and concise

            ✅ Give real-world examples

            ✅ Explain your reasoning

            ✅ Use technical terms correctly

            ✅ Structure your answer logically

            🚫 Avoid one-word answers
            """)


        if st.button(
            "🚀 Submit Answer →",
            use_container_width=True
        ):

            if not answer.strip():

                st.error(
                    "⚠️ Please enter an answer before submitting."
                )

            else:

                with st.spinner(
                    "🤖 PrepAI is analyzing your answer..."
                ):

                    result = evaluate_answer(
                        question,
                        answer
                    )


                st.session_state.interview_answers.append(
                    answer
                )

                st.session_state.interview_scores.append(
                    result
                )

                st.session_state.interview_feedback.append(
                    result["feedback"]
                )


                if index + 1 >= total_questions:

                    st.session_state.interview_finished = True

                else:

                    st.session_state.interview_question += 1


                st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

elif page == "Dashboard":

    st.title("📊 Performance Dashboard")

    conn = get_connection()

    aptitude_data = pd.read_sql_query(
        """
        SELECT *
        FROM aptitude_results
        ORDER BY date
        """,
        conn
    )

    interview_data = pd.read_sql_query(
        """
        SELECT *
        FROM interview_results
        ORDER BY date
        """,
        conn
    )

    conn.close()


    # ========================================================
    # APTITUDE
    # ========================================================

    st.header("🧮 Aptitude Performance")

    if not aptitude_data.empty:

        latest = aptitude_data.iloc[-1]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Latest Score",
                f"{latest['percentage']:.0f}%"
            )

        with col2:

            st.metric(
                "Attempts",
                len(aptitude_data)
            )

        with col3:

            st.metric(
                "Best Score",
                f"{aptitude_data['percentage'].max():.0f}%"
            )

        chart = px.line(
            aptitude_data,
            y="percentage",
            x=aptitude_data.index + 1,
            markers=True,
            title="Aptitude Score Improvement"
        )

        chart.update_layout(
            xaxis_title="Attempt",
            yaxis_title="Percentage"
        )

        st.plotly_chart(
            chart,
            use_container_width=True
        )

    else:

        st.info(
            "Take an aptitude test to see your performance."
        )


    # ========================================================
    # INTERVIEW
    # ========================================================

    st.header("🤖 Interview Performance")

    if not interview_data.empty:

        latest_interview = (
            interview_data.iloc[-1]
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Latest Score",
                f"{latest_interview['overall_score']:.1f}/10"
            )

        with col2:

            st.metric(
                "Interviews",
                len(interview_data)
            )

        with col3:

            st.metric(
                "Best Score",
                f"{interview_data['overall_score'].max():.1f}/10"
            )

        chart = px.line(
            interview_data,
            y="overall_score",
            x=interview_data.index + 1,
            markers=True,
            title="Interview Score Improvement"
        )

        chart.update_layout(
            xaxis_title="Attempt",
            yaxis_title="Score"
        )

        st.plotly_chart(
            chart,
            use_container_width=True
        )

    else:

        st.info(
            "Complete an AI interview to see your performance."
        )


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.divider()

    st.header("💡 Personalized Recommendations")

    recommendations = []

    if not aptitude_data.empty:

        latest = aptitude_data.iloc[-1]

        categories = {

            "Quantitative":
            latest["quantitative"],

            "Logical Reasoning":
            latest["logical"],

            "Verbal Ability":
            latest["verbal"]

        }

        weakest = min(
            categories,
            key=categories.get
        )

        recommendations.append(
            f"Focus more on **{weakest}**."
        )


    if not interview_data.empty:

        latest = interview_data.iloc[-1]

        if latest["communication_score"] < 7:

            recommendations.append(
                "Practice structured and confident communication."
            )

        if latest["technical_score"] < 7:

            recommendations.append(
                "Revise your core technical concepts."
            )

        if latest["clarity_score"] < 7:

            recommendations.append(
                "Try giving shorter and more structured answers."
            )


    if recommendations:

        for recommendation in recommendations:

            st.write(
                "• " + recommendation
            )

    else:

        st.info(
            "Complete some tests and interviews to receive recommendations."
        )