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
st.title("🧠 Programming Quiz")

# Language selection
languages = ["Python", "Java", "C++", "JavaScript", "C#", "Go", "Ruby", "PHP", "Swift"]
selected_lang = st.selectbox("📘 Select your programming language:", languages)

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
        raw_mcqs = get_mcqs_from_llm(selected_lang)
        st.session_state.mcqs = parse_mcqs(raw_mcqs)
        st.session_state.score = 0
        st.session_state.current_q = 0
        st.session_state.answers = []  # to store user answers

mcqs = st.session_state.mcqs
current_q = st.session_state.current_q

# Main Quiz
if current_q < len(mcqs):
    q = mcqs[current_q]
    st.subheader(f"Question {current_q+1}: {q['question']}")

    options = [f"{label}) {text}" for label, text in q['options']]
    selected_option = st.radio("Choose one:", options, key=f"q{current_q}")

    if st.button("Submit Answer"):
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
    st.success(f"🎉 Quiz Completed! You got {st.session_state.score} out of {len(mcqs)} correct.")

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
