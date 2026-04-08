import streamlit as st
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Study Planner", layout="wide")

# ---------------- POPUP ----------------
if "consent" not in st.session_state:
    st.session_state.consent = False

if not st.session_state.consent:
    st.title("Welcome to Study Planner")
    agree = st.checkbox("I promise I will be honest with my study tracking")
    if st.button("Continue"):
        st.session_state.consent = True
    st.stop()

# ---------------- COUNTDOWN ----------------
board_date = date(date.today().year + (1 if date.today().month > 2 else 0), 2, 1)
days_left = (board_date - date.today()).days
st.sidebar.title("⏳ Countdown")
st.sidebar.write(f"Days left till boards: {days_left}")

# ---------------- SUBJECT INPUT ----------------
st.title("📚 Class 12 Study Planner")

if "subjects" not in st.session_state:
    st.session_state.subjects = {}

with st.sidebar:
    st.header("Add Subject")
    subject_name = st.text_input("Subject Name")
    total_chapters = st.number_input("Total Chapters", min_value=1, step=1)
    completed = st.number_input("Chapters Completed", min_value=0, step=1)

    if st.button("Add Subject"):
        if subject_name:
            st.session_state.subjects[subject_name] = {
                "total": total_chapters,
                "completed": completed,
                "chapters": {i: {"rev": [False, False, False]} for i in range(1, total_chapters+1)}
            }

# ---------------- TRACKING ----------------
for sub, data in st.session_state.subjects.items():
    st.subheader(f"{sub}")
    progress = data["completed"] / data["total"] if data["total"] else 0

    st.write(f"Completion: {round(progress*100,2)}%")

    total_effective = 0
    for ch in range(1, data["total"]+1):
        st.write(f"Chapter {ch}")
        cols = st.columns(3)

        for i in range(3):
            key = f"{sub}_{ch}_rev{i}"
            if key not in st.session_state:
                st.session_state[key] = False

           cols[i].checkbox(f"Rev {i+1}", key=key)

        rev_count = sum([st.session_state[f"{sub}_{ch}_rev{i}"] for i in range(3)])

        # effectiveness formula
        eff = (rev_count / 3) * 0.6 + (1 if ch <= data["completed"] else 0) * 0.4
        total_effective += eff

    overall_eff = (total_effective / data["total"]) * 100 if data["total"] else 0
    st.success(f"Effective Understanding: {round(overall_eff,2)}%")

# ---------------- STUDY LOG ----------------
st.header("📝 Daily Study Log")

if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Date", "Subject", "What Studied"])

col1, col2, col3 = st.columns(3)
with col1:
    log_date = st.date_input("Date", datetime.today())
with col2:
    log_subject = st.text_input("Subject (Log)")
with col3:
    log_text = st.text_input("What did you study?")

if st.button("Add Log"):
    new_row = pd.DataFrame([[log_date, log_subject, log_text]], columns=["Date", "Subject", "What Studied"])
    st.session_state.log = pd.concat([st.session_state.log, new_row], ignore_index=True)

st.dataframe(st.session_state.log, use_container_width=True)

# ---------------- CLEAR BUTTON ----------------
if st.button("Reset All Data"):
    st.session_state.clear()
    st.experimental_rerun()
