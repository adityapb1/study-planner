import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Study Planner Pro", layout="wide")

# ---------------- LOGIN SYSTEM ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Study Planner")
    username = st.text_input("Enter Username")
    if st.button("Login"):
        if username:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
    st.stop()

# ---------------- THEME ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if st.sidebar.button("🌗 Toggle Theme"):
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# ---------------- COUNTDOWN ----------------
board_date = date(date.today().year + (1 if date.today().month > 2 else 0), 2, 1)
days_left = (board_date - date.today()).days
st.sidebar.title("⏳ Countdown")
st.sidebar.write(f"Days left: {days_left}")

st.title(f"🚀 Study Planner - {st.session_state.username}")

# ---------------- DATA ----------------
if "subjects" not in st.session_state:
    st.session_state.subjects = {}

# ---------------- ADD SUBJECT ----------------
with st.sidebar:
    st.header("Add Subject")
    subject_name = st.text_input("Subject Name")
    total_chapters = st.number_input("Total Chapters", min_value=1)

    if st.button("Add Subject"):
        if subject_name:
            st.session_state.subjects[subject_name] = {
                "total": total_chapters,
                "chapters": {i: {"name": f"Chapter {i}", "rev": [False, False, False]} for i in range(1, total_chapters+1)}
            }

# ---------------- TRACKING ----------------
for sub, data in st.session_state.subjects.items():
    st.markdown(f"## ✨ {sub}")

    total_eff = 0
    completed = 0
    weak_chapters = []

    for ch in range(1, data["total"]+1):
        ch_data = data["chapters"][ch]

        col1, col2, col3, col4 = st.columns([3,1,1,1])

        name = col1.text_input("", value=ch_data["name"], key=f"name_{sub}_{ch}")
        ch_data["name"] = name

        rev_count = 0
        for i, col in enumerate([col2, col3, col4]):
            key = f"{sub}_{ch}_rev{i}"
            if key not in st.session_state:
                st.session_state[key] = False

            if col.checkbox("", key=key):
                rev_count += 1

        if rev_count >= 1:
            completed += 1
        if rev_count < 2:
            weak_chapters.append(name)

        total_eff += (rev_count / 3)

    progress = completed / data["total"] if data["total"] else 0
    st.progress(progress)
    st.info(f"Completion: {round(progress*100,1)}%")

    eff = (total_eff / data["total"]) * 100 if data["total"] else 0
    st.success(f"Understanding: {round(eff,1)}%")

    # ---------------- AI SUGGESTION ----------------
    if weak_chapters:
        st.warning(f"⚡ Focus on: {', '.join(weak_chapters[:3])}")
    else:
        st.success("🔥 All chapters strong!")

# ---------------- STUDY LOG ----------------
st.header("📝 Study Log")

if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Date","Subject","Study"])

col1, col2, col3 = st.columns(3)
with col1:
    d = st.date_input("Date")
with col2:
    s = st.selectbox("Subject", list(st.session_state.subjects.keys()) if st.session_state.subjects else [""])
with col3:
    t = st.text_input("What studied")

if st.button("Add"):
    new = pd.DataFrame([[d,s,t]], columns=["Date","Subject","Study"])
    st.session_state.log = pd.concat([st.session_state.log,new], ignore_index=True)

st.dataframe(st.session_state.log, use_container_width=True)

# ---------------- RESET ----------------
if st.button("Reset All"):
    st.session_state.clear()
    st.rerun()

