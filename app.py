import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import re
import uuid

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
st.set_page_config(page_title="Programming Quiz", page_icon="💻", layout="centered")

# --- Custom CSS for New Color Scheme ---
st.markdown("""
    <style>
    body, .stApp {
        background: #0b1524;
        font-family: 'Inter', 'Roboto', sans-serif;
        color: #d1d5db;
    }
    .stApp {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
        background: transparent !important;
    }
    /* Ensure main content area has no white background */
    .main, .st-emotion-cache-uf99v8 {
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        border-radius: 0 !important;
        color: #d1d5db !important;
    }
    h1 {
        font-size: 2.5rem;
        color: #f3f4f6;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    h4 {
        font-size: 1.2rem;
        color: #2dd4bf;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        color: #fff;
        background: linear-gradient(90deg, #2dd4bf 0%, #22d3ee 100%);
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #22d3ee 0%, #2dd4bf 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    }
    .stRadio > div {
        background: #1e293b;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .stRadio > div > label {
        font-size: 1rem;
        color: #d1d5db !important;
        padding: 0.5rem;
        border-radius: 8px;
        transition: background 0.2s;
    }
    .stRadio > div > label:hover {
        background: rgba(45,212,191,0.1);
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #2dd4bf 0%, #22d3ee 100%);
    }
    /* Enhanced Selectbox Styling */
    .stSelectbox div[data-baseweb="select"] {
        background: #1e293b !important;
        border: 2px solid #2dd4bf !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .stSelectbox div[data-baseweb="select"]:hover {
        border-color: #22d3ee !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stSelectbox div[data-baseweb="select"] > div {
        color: #d1d5db !important;
    }
    .stSelectbox .css-1dimb5e-singleValue {
        color: #2dd4bf !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    .stSelectbox .css-11unzgr {
        background: #1e293b !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .stSelectbox .css-1n7v3ny-option {
        color: #d1d5db !important;
        background: #1e293b !important;
        padding: 0.75rem !important;
        transition: all 0.2s;
    }
    .stSelectbox .css-1n7v3ny-option:hover,
    .stSelectbox .css-1n7v3ny-option[aria-selected="true"] {
        background: #2dd4bf !important;
        color: #fff !important;
    }
    .stSpinner > div {
        color: #2dd4bf !important;
    }
    .stSuccess, .stError {
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stExpander {
        background: #1e293b;
        border-radius: 10px;
        border: 1px solid #2dd4bf;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .stExpander > div > div {
        color: #d1d5db !important;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: rgba(15,23,42,0.9);
        color: #d1d5db;
        text-align: center;
        padding: 0.75rem 0;
        font-size: 0.9rem;
        border-top: 1px solid #2dd4bf;
        z-index: 100;
    }
    a {
        color: #2dd4bf;
        text-decoration: none;
    }
    a:hover {
        color: #22d3ee;
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.title("🧠 Programming Quiz")
    st.markdown("<h4>Test your coding skills with interactive MCQs! 🚀</h4>", unsafe_allow_html=True)

# Language selection
languages = ["Python", "Java", "C++", "JavaScript", "C#", "Go", "Ruby", "PHP", "Swift"]
selected_lang = st.selectbox(
    "📘 Choose a Programming Language:",
    languages,
    help="Select a language to start the quiz",
    key="lang_select"
)

# Show the currently selected language with a subtle animation
st.markdown(
    f"<div style='font-size:1.1rem; margin:1rem 0; color:#2dd4bf; opacity:0; animation: fadeIn 0.5s ease forwards;'><b>Selected Language:</b> {selected_lang}</div>",
    unsafe_allow_html=True
)
st.markdown("""
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

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
    with st.spinner(f"Generating {selected_lang} quiz..."):
        raw_mcqs = get_mcqs_from_llm_cached(selected_lang)
        st.session_state.mcqs = parse_mcqs(raw_mcqs)
        st.session_state.score = 0
        st.session_state.current_q = 0
        st.session_state.answers = []

mcqs = st.session_state.mcqs
current_q = st.session_state.current_q

# --- Progress Bar ---
progress = (current_q) / len(mcqs)
st.progress(progress, text=f"Question {current_q+1} of {len(mcqs)}")

# Main Quiz
if current_q < len(mcqs):
    q = mcqs[current_q]
    st.subheader(f"Question {current_q+1} of {len(mcqs)}")
    st.markdown(f"<div style='font-size:1.1rem; font-weight:600; margin-bottom:1rem;'>{q['question']}</div>", unsafe_allow_html=True)

    options = [f"{label}) {text}" for label, text in q['options']]
    selected_option = st.radio("Choose one:", options, key=f"q{current_q}_{st.session_state.selected_lang}")

    if st.button("✅ Submit Answer"):
        user_ans = selected_option[0]
        correct_ans = q["answer"]

        # Store user answer
        st.session_state.answers.append({
            "question": q["question"],
            "options": q["options"],
            "user_ans": user_ans,
            "correct_ans": correct_ans,
        })

        if user_ans == correct_ans:
            st.success("✅ Correct! Well done!")
            st.session_state.score += 1
        else:
            correct_text = next(text for label, text in q['options'] if label == correct_ans)
            st.error(f"❌ Incorrect! The correct answer is {correct_ans}: {correct_text}")

        st.session_state.current_q += 1
        st.rerun()

# Result Screen
else:
    st.balloons()
    st.markdown(
        f"<div style='text-align:center; font-size:1.5rem; margin:1rem 0;'>"
        f"🎉 <b>Quiz Completed!</b><br>"
        f"You scored <span style='color:#2dd4bf;'>{st.session_state.score}</span> out of <span style='color:#2dd4bf;'>{len(mcqs)}</span> correct."
        f"</div>",
        unsafe_allow_html=True
    )

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
      <b> Github | </b> <a href='https://github.com/Zuhairkhan13' target='_blank'>Zuhair Khan</a>
    </div>
""", unsafe_allow_html=True)