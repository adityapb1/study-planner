import streamlit as st
import pandas as pd
from datetime import date, timedelta
import random

st.set_page_config(page_title="Study Planner Pro Max", layout="wide")

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
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Date","Subject","Study"])

if "goal" not in st.session_state:
    st.session_state.goal = 2  # default hours

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

# ---------------- BADGE + CONFETTI ----------------
def get_badge(streak):
    if streak >= 30:
        return "🏆 Beast"
    elif streak >= 14:
        return "🔥 Warrior"
    elif streak >= 7:
        return "⚡ Starter"
    return None

badge = get_badge(streak)

if badge:
    st.balloons()
    st.success(f"🎉 Achievement Unlocked: {badge}")

# ---------------- SIDEBAR ----------------
st.sidebar.title(f"👋 {st.session_state.user}")
st.sidebar.markdown(f"🔥 Streak: {streak}")
st.sidebar.markdown(f"🎯 Daily Goal: {st.session_state.goal} hrs")

# Goal setter
new_goal = st.sidebar.slider("Set Daily Goal (hrs)", 1, 10, st.session_state.goal)
st.session_state.goal = new_goal

# ---------------- MAIN ----------------
st.title("📊 Weekly Progress")

if not st.session_state.log.empty:
    df = st.session_state.log.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    weekly = df.groupby(df["Date"].dt.date).count()
    st.line_chart(weekly)

# ---------------- STUDY LOG ----------------
st.header("📝 Study Log")
col1, col2, col3 = st.columns(3)

with col1:
    d = st.date_input("Date")
with col2:
    s = st.text_input("Subject")
with col3:
    t = st.text_input("What studied")

if st.button("Add Log"):
    new = pd.DataFrame([[d,s,t]], columns=["Date","Subject","Study"])
    st.session_state.log = pd.concat([st.session_state.log,new], ignore_index=True)
    st.toast("🔥 Progress saved!")

st.dataframe(st.session_state.log)

# ---------------- LEADERBOARD (MOCK) ----------------
st.markdown("---")
st.header("🏆 Leaderboard (Friends)")

leaderboard = pd.DataFrame({
    "Name": ["You", "Aman", "Riya"],
    "Streak": [streak, random.randint(1,20), random.randint(1,20)]
})

st.dataframe(leaderboard)

# ---------------- RESET ----------------
if st.button("Reset All"):
    st.session_state.clear()
    st.rerun()
