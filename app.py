import streamlit as st
import pandas as pd
from datetime import date, timedelta

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

# SUBJECT BUTTONS
st.sidebar.markdown("### 📚 Subjects")
selected_subject = None

for sub in st.session_state.subjects:
    if st.sidebar.button(sub):
        st.session_state.selected = sub

if "selected" in st.session_state:
    selected_subject = st.session_state.selected

# ADD SUBJECT
st.sidebar.markdown("---")
new_sub = st.sidebar.text_input("Add New Subject", key="sub_input")
chapters = st.sidebar.number_input("No. of Chapters", min_value=1, key="chap_input")

if st.sidebar.button("➕ Add Subject") and new_sub:
    st.session_state.subjects[new_sub] = {
        "total": chapters,
        "chapters": {i: {"name": f"Chapter {i}"} for i in range(1, chapters+1)}
    }
    st.session_state.selected = new_sub
    st.session_state.sub_input = ""
    st.session_state.chap_input = 1
    st.rerun()

# ---------------- HOME PAGE ----------------
st.markdown(f"# 👋 Welcome back to studies, {st.session_state.user} 🚀")

st.markdown("### 🎯 Select what you're studying today")

if st.session_state.subjects:
    cols = st.columns(len(st.session_state.subjects))
    for i, sub in enumerate(st.session_state.subjects):
        if cols[i].button(f"📘 {sub}"):
            st.session_state.selected = sub
            selected_subject = sub
else:
    st.info("No subjects added yet. Add from sidebar 👈")

# ---------------- STUDY LOG IN SIDEBAR ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Study Log")

log_date = st.sidebar.date_input("Date", key="log_date")
log_sub = st.sidebar.selectbox("Subject", list(st.session_state.subjects.keys()) if st.session_state.subjects else [""], key="log_sub")
log_text = st.sidebar.text_input("What studied", key="log_text")

if st.sidebar.button("Add Log"):
    new = pd.DataFrame([[log_date, log_sub, log_text]], columns=["Date","Subject","Study"])
    st.session_state.log = pd.concat([st.session_state.log,new], ignore_index=True)
    st.session_state.log_text = ""

# ---------------- MAIN SUBJECT VIEW ----------------
if selected_subject:
    st.markdown("---")
    data = st.session_state.subjects[selected_subject]
    st.subheader(f"📖 {selected_subject}")

    total_eff = 0
    completed = 0

    for ch in range(1, data["total"]+1):
        ch_data = data["chapters"][ch]
        cols = st.columns([5,1,1,1])

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
    st.markdown(f"### 📊 Completion: {round(progress*100,1)}%")

    eff = (total_eff / data["total"]) * 100
    st.markdown(f"### 🧠 Understanding: {round(eff,1)}%")

# ---------------- TABLE VIEW ----------------
st.markdown("---")
st.header("📊 Study History")
st.dataframe(st.session_state.log, use_container_width=True)

# ---------------- RESET ----------------
if st.button("Reset All"):
    st.session_state.clear()
    st.rerun()
