import streamlit as st
import pandas as pd
from datetime import date, timedelta
import random

st.set_page_config(page_title="Study Planner Ultimate", layout="wide")

# ---------------- USER ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("🚀 Study Planner")
    st.radio("New or Existing?", ["New User", "Existing User"])
    username = st.text_input("Enter UNIQUE username")
    if st.button("Continue") and username:
        st.session_state.user = username
        st.rerun()
    st.stop()

# ---------------- DATA ----------------
if "subjects" not in st.session_state:
    st.session_state.subjects = {}

if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Date","Subject","Study"])

# ---------------- STREAK ----------------
def calculate_streak(df):
    if df.empty:
        return 0
    dates = sorted(set(pd.to_datetime(df["Date"]).dt.date), reverse=True)
    today = date.today()
    streak = 1
    last = dates[0]
    for d in dates[1:]:
        if last - d == timedelta(days=1):
            streak += 1
            last = d
        else:
            break
    if (today - last).days > 2:
        return 0
    return streak

streak = calculate_streak(st.session_state.log)

# ---------------- SIDEBAR ----------------
st.sidebar.title(f"👋 {st.session_state.user}")
st.sidebar.markdown(f"🔥 Streak: {streak}")

# SUBJECT BUTTONS (FIXED)
st.sidebar.markdown("### 📚 Subjects")
selected_subject = None

for sub in st.session_state.subjects:
    if st.sidebar.button(sub):
        st.session_state.selected = sub

if "selected" in st.session_state:
    selected_subject = st.session_state.selected

# ADD SUBJECT
st.sidebar.markdown("---")
new_sub = st.sidebar.text_input("Add New Subject")
chapters = st.sidebar.number_input("No. of Chapters", min_value=1)

if st.sidebar.button("➕ Add Subject") and new_sub:
    st.session_state.subjects[new_sub] = {
        "total": chapters,
        "chapters": {i: {"name": f"Chapter {i}"} for i in range(1, chapters+1)}
    }
    st.session_state.selected = new_sub
    st.rerun()

# ---------------- MAIN ----------------
st.title("🚀 Study Planner")

if selected_subject:
    data = st.session_state.subjects[selected_subject]
    st.subheader(f"✨ {selected_subject}")

    total_eff = 0
    completed = 0

    for ch in range(1, data["total"]+1):
        ch_data = data["chapters"][ch]
        cols = st.columns([4,1,1,1])

        name = cols[0].text_input("", value=ch_data.get("name", f"Chapter {ch}"), key=f"name_{selected_subject}_{ch}")
        ch_data["name"] = name

        rev_count = 0
        for i in range(3):
            key = f"{selected_subject}_{ch}_rev{i}"
            if key not in st.session_state:
                st.session_state[key] = False
            if cols[i+1].checkbox("", key=key):
                rev_count += 1

        if rev_count >= 1:
            completed += 1

        total_eff += (rev_count / 3)

    progress = completed / data["total"]
    st.progress(progress)
    st.info(f"📊 Completion: {round(progress*100,1)}%")

    eff = (total_eff / data["total"]) * 100
    st.success(f"🧠 Understanding: {round(eff,1)}%")

# ---------------- STUDY LOG ----------------
st.markdown("---")
st.header("📝 Study Log")

col1, col2, col3 = st.columns(3)
with col1:
    d = st.date_input("Date")
with col2:
    s = st.selectbox("Subject", list(st.session_state.subjects.keys()) if st.session_state.subjects else [""])
with col3:
    t = st.text_input("What studied")

if st.button("Add Log"):
    new = pd.DataFrame([[d,s,t]], columns=["Date","Subject","Study"])
    st.session_state.log = pd.concat([st.session_state.log,new], ignore_index=True)
    st.toast("🔥 Progress saved!")

st.dataframe(st.session_state.log)

# ---------------- RESET ----------------
if st.button("Reset All"):
    st.session_state.clear()
    st.rerun()

