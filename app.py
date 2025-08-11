import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import re

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)

# Function to call Groq LLM and get MCQs
def get_mcqs_from_llm(language):
    prompt = (
        f"Generate 10 unique multiple-choice questions (MCQs) on {language} programming. "
        "Each question should have 4 options labeled A, B, C, and D, and also provide the correct answer at the end. "
        "Format:\n\n"
        "Q1. What is Python?\nA) Snake\nB) Programming Language\nC) Car\nD) Game\nAnswer: B\n"
    )

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )

    return response.choices[0].message.content

# --- Caching for MCQ generation ---
import streamlit as st  # ensure st is imported at the top
@st.cache_data(show_spinner=False)
def get_mcqs_from_llm_cached(language):
    return get_mcqs_from_llm(language)

# Function to parse the LLM output
def parse_mcqs(text):
    questions = re.findall(r"Q\d+\..+?(?=Q\d+\.|$)", text, re.DOTALL)
    parsed = []
    for q in questions:
        question_text = re.search(r"Q\d+\.\s*(.*)", q).group(1).strip()
        options = re.findall(r"([A-D])\)\s*(.+)", q)
        answer = re.search(r"Answer:\s*([A-D])", q)
        parsed.append({
            "question": question_text,
            "options": options,
            "answer": answer.group(1) if answer else None
        })
    return parsed

# --- Streamlit App UI ---
st.set_page_config(page_title="Programming Quiz", page_icon="💻")

# --- Custom CSS for beautiful dark UI ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #232526 0%, #414345 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #232526 0%, #414345 100%);
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        color: #f3f3f3;
    }
    .stButton>button {
        color: #fff;
        background: linear-gradient(90deg, #ff512f 0%, #dd2476 100%);
        border-radius: 8px;
        padding: 0.5em 2em;
        font-size: 1.1em;
        font-weight: bold;
        border: none;
        margin-top: 1em;
        transition: 0.2s;
        box-shadow: 0 2px 8px 0 rgba(221,36,118,0.15);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #dd2476 0%, #ff512f 100%);
        transform: scale(1.05);
    }
    .stRadio>div>label {
        font-size: 1.1em;
        margin-bottom: 0.5em;
        color: #f3f3f3 !important;
    }
    .st-bb {
        background: #232526;
        border-radius: 10px;
        padding: 1em;
        margin-bottom: 1em;
        color: #f3f3f3;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #ff512f 0%, #dd2476 100%);
    }
    /* Dropdown (selectbox) text color and beautification */
    .stSelectbox div[data-baseweb="select"] {
        color: #f3f3f3 !important;
        background: #232526 !important;
        border: 2px solid #ff512f !important;
        border-radius: 6px !important;
        box-shadow: 0 1px 4px 0 rgba(221,36,118,0.10);
        padding: 0.01em 0.5em !important;
        font-size: 0.92em !important;
        transition: border 0.2s;
        min-height: 28px !important;
        line-height: 1.1 !important;
    }
    .stSelectbox div[data-baseweb="select"]:hover {
        border: 2px solid #dd2476 !important;
    }
    .stSelectbox div[data-baseweb="select"] * {
        color: #f3f3f3 !important;
    }
    .stSelectbox div[data-baseweb="select"] span {
        color: #f3f3f3 !important;
    }
    .stSelectbox .css-1dimb5e-singleValue {
        color: #ff512f !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
        letter-spacing: 0.5px;
        min-height: 24px !important;
        line-height: 1.1 !important;
        display: flex;
        align-items: center;
    }
    .stSelectbox .css-11unzgr {
        background: #232526 !important;
    }
    .stSelectbox .css-1n7v3ny-option {
        color: #f3f3f3 !important;
        background: #232526 !important;
        border-radius: 8px !important;
        margin: 2px 0;
        padding: 8px 12px !important;
    }
    .stSelectbox .css-1n7v3ny-option[aria-selected="true"] {
        background: #ff512f !important;
        color: #fff !important;
    }
    /* Remove the dark card (main) background */
    .main { background: none !important; box-shadow: none !important; padding: 0 !important; border-radius: 0 !important; color: inherit !important; }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: rgba(30,32,38,0.85);
        color: #f3f3f3;
        text-align: center;
        padding: 0.5em 0;
        font-size: 1em;
        z-index: 100;
        border-top: 1px solid #333;
    }
    a { color: #ff512f; text-decoration: none; }
    a:hover { color: #dd2476; text-decoration: underline; }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.title("🧠 Programming Quiz")
    st.markdown("<h4 style='color:#ff512f;'>Test your programming knowledge with fun MCQs! 🚀</h4>", unsafe_allow_html=True)

# Language selection
languages = ["Python", "Java", "C++", "JavaScript", "C#", "Go", "Ruby", "PHP", "Swift"]
selected_lang = st.selectbox("📘 Select your programming language:", languages)

# Show the currently selected language
st.markdown(f"<div style='font-size:1.2em; margin-bottom:1em; color:#ff512f;'><b>Selected Language:</b> {selected_lang}</div>", unsafe_allow_html=True)

# Reset session if language changes
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = selected_lang

if selected_lang != st.session_state.selected_lang:
    for key in ["mcqs", "score", "current_q", "answers"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.selected_lang = selected_lang
    st.rerun()

# Init session and load MCQs
if "mcqs" not in st.session_state:
    with st.spinner(f"Generating {selected_lang} quiz from LLM..."):
        raw_mcqs = get_mcqs_from_llm_cached(selected_lang)
        st.session_state.mcqs = parse_mcqs(raw_mcqs)
        st.session_state.score = 0
        st.session_state.current_q = 0
        st.session_state.answers = []  # to store user answers

mcqs = st.session_state.mcqs
current_q = st.session_state.current_q

# --- Progress Bar ---
progress = (current_q) / len(mcqs)
st.progress(progress, text=f"Progress: {current_q} / {len(mcqs)}")

# Main Quiz
if current_q < len(mcqs):
    q = mcqs[current_q]
    st.subheader(f"Question {current_q+1} of {len(mcqs)}")
    st.markdown(f"<b>{q['question']}</b>", unsafe_allow_html=True)

    options = [f"{label}) {text}" for label, text in q['options']]
    selected_option = st.radio("Choose one:", options, key=f"q{current_q}")

    if st.button("✅ Submit Answer"):
        user_ans = selected_option[0]  # A/B/C/D
        correct_ans = q["answer"]

        # Store user answer
        st.session_state.answers.append({
            "question": q["question"],
            "options": q["options"],
            "user_ans": user_ans,
            "correct_ans": correct_ans,
        })

        if user_ans == correct_ans:
            st.success("✅ Correct!")
            st.session_state.score += 1
        else:
            st.error(f"❌ Wrong! Correct answer: {correct_ans})")

        st.session_state.current_q += 1
        st.rerun()

# Result Screen
else:
    st.balloons()
    st.markdown(f"🎉 <b>Quiz Completed!</b> You got <span style='color:#ff512f;'>{st.session_state.score}</span> out of <span style='color:#ff512f;'>{len(mcqs)}</span> correct.", unsafe_allow_html=True)

    with st.expander("📋 View All Questions & Answers"):
        for idx, ans in enumerate(st.session_state.answers):
            q_text = ans['question']
            options = ans['options']
            user_ans = ans['user_ans']
            correct_ans = ans['correct_ans']

            st.markdown(f"**Q{idx+1}. {q_text}**")

            for label, text in options:
                opt_line = f"{label}) {text}"
                if label == correct_ans and label == user_ans:
                    st.markdown(f"<span style='color:green;'>✅ {opt_line}</span>", unsafe_allow_html=True)
                elif label == user_ans and label != correct_ans:
                    st.markdown(f"<span style='color:red;'>❌ {opt_line}</span>", unsafe_allow_html=True)
                elif label == correct_ans:
                    st.markdown(f"<span style='color:green;'>✔️ {opt_line}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"{opt_line}")

            st.markdown("---")

    if st.button("🔁 Restart Quiz"):
        for key in ["mcqs", "score", "current_q", "answers"]:
            del st.session_state[key]
        st.rerun()

# --- Footer ---
st.markdown("""
    <div class='footer'>
        Made with ❤️ using <b>Streamlit</b> | <a href='https://github.com/your-github' target='_blank'>Your Name</a>
    </div>
""", unsafe_allow_html=True)
