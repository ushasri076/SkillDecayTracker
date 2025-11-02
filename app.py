import streamlit as st
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="SkillDecayTracker (Smart Prototype)", page_icon="📊", layout="wide")

# --------------------------
# Load skill dataset
# --------------------------
with open("skill_data.json", "r") as f:
    skill_data = json.load(f)

st.title("📊 SkillDecayTracker — Smart Prototype")
st.write("Now supports smart mode: enter skills, a job, or both to analyze compatibility, demand, and re-skilling urgency.")

# --------------------------
# Sidebar inputs
# --------------------------
st.sidebar.header("Controls")
all_skills = sorted(skill_data.keys())
selected_for_chart = st.sidebar.multiselect("Select skills to view trend chart", all_skills, default=all_skills[:3])

st.sidebar.markdown("---")
st.sidebar.markdown("**Skill & Job Inputs**")
job = st.sidebar.text_input("Target Job (optional, e.g., AI Engineer, Doctor, Web Developer)")
user_skills_input = st.sidebar.text_input("Enter your current skills (comma separated)", value="Python, React, SQL")

# --------------------------
# Helper functions
# --------------------------
def simulate_time_series(growth_pct, months=12, base=50):
    monthly_rate = (1 + growth_pct) ** (1/12) - 1
    vals = [base]
    for _ in range(months - 1):
        change = vals[-1] * monthly_rate
        vals.append(max(1, vals[-1] + change))
    return vals

def days_since(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return (datetime.now() - d).days
    except:
        return None

def urgency_score_from_days(days):
    if days is None:
        return 0.25
    if days > 180:
        return 0.98
    if days > 120:
        return 0.88
    if days > 60:
        return 0.72
    if days > 30:
        return 0.45
    return 0.15

# Job to skills mapping
job_skills = {
    "doctor": ["biology", "anatomy", "medical research", "diagnosis", "pharmacology", "patient communication"],
    "ai engineer": ["python", "machine learning", "deep learning", "pytorch", "tensorflow", "data engineering"],
    "software developer": ["python", "java", "c++", "dsa", "algorithms", "git", "testing"],
    "web developer": ["html", "css", "javascript", "react", "node.js", "typescript"],
    "data analytics": ["sql", "excel", "python", "power bi", "tableau", "statistics"],
    "data scientist": ["python", "machine learning", "statistics", "sql", "pandas", "deep learning"],
    "teacher": ["communication", "lesson planning", "subject expertise", "assessment", "mentoring"]
}

# --------------------------
# Smart mode functions
# --------------------------
def suggest_jobs_from_skills(skills):
    job_matches = []
    for job, needed in job_skills.items():
        overlap = len(set([s.lower() for s in skills]) & set([n.lower() for n in needed]))
        score = overlap / len(needed)
        if score > 0:
            job_matches.append((job.title(), score))
    return sorted(job_matches, key=lambda x: x[1], reverse=True)

def relevance_feedback(skill, job):
    skill_l = skill.lower()
    job_l = job.lower().strip()
    if job_l in job_skills:
        if skill_l in [s.lower() for s in job_skills[job_l]]:
            return "high", f"✅ **{skill}** is highly relevant for a {job}."
        for s in job_skills[job_l]:
            if skill_l in s.lower() or s.lower() in skill_l:
                return "medium", f"⚠️ **{skill}** is somewhat relevant for a {job}."
        suggestions = ", ".join(job_skills[job_l][:4])
        return "low", f"❌ **{skill}** isn’t typical for a {job}. Try focusing on: {suggestions}."
    else:
        return "unknown", f"ℹ️ No data for the job '{job}' yet."

# --------------------------
# Trend chart
# --------------------------
if selected_for_chart:
    months = 12
    dates = [(datetime.now() - timedelta(days=30*(months-i-1))).strftime("%b %Y") for i in range(months)]
    plt.figure(figsize=(10, 4))
    for sk in selected_for_chart:
        info = skill_data.get(sk, {})
        ts = simulate_time_series(info.get("growth_pct", 0.0), months=months, base=50)
        plt.plot(dates, ts, label=f"{sk} ({info.get('trend', 'N/A')})")
    plt.xticks(rotation=45)
    plt.title("Simulated Skill Demand Trends (last 12 months)")
    plt.xlabel("Month")
    plt.ylabel("Normalized demand (simulated index)")
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()

# --------------------------
# Analysis section
# --------------------------
st.header("🧠 Smart Skill & Job Analysis")

if st.button("Analyze"):
    skills = [s.strip() for s in user_skills_input.split(",") if s.strip()]
    job_input = job.strip()

    if not skills and not job_input:
        st.warning("Please enter at least one skill or a job title.")
    elif skills and not job_input:
        st.subheader("💼 Suggested Jobs Based on Your Skills")
        matches = suggest_jobs_from_skills(skills)
        if matches:
            for j, score in matches[:5]:
                st.markdown(f"- **{j}** — match score: {int(score*100)}%")
        else:
            st.info("No strong job matches found for the given skills.")
    elif job_input and not skills:
        st.subheader(f"🧩 Core Skills for {job_input.title()}")
        if job_input.lower() in job_skills:
            st.markdown(", ".join(job_skills[job_input.lower()]))
        else:
            st.info("No data available for this job yet.")
    else:
        # full compatibility mode (same as before)
        st.subheader(f"🔎 Compatibility Analysis for {job_input}")
        scored = []
        for skill in skills:
            info = skill_data.get(skill, None)
            if info:
                days = days_since(info.get("last_used", ""))
                urg = urgency_score_from_days(days)
                growth = info.get("growth", "N/A")
                st.markdown(f"**{skill}** — Trend: {info.get('trend','N/A')} ({growth}) — Urgency: {int(urg*100)}%")
                st.progress(min(1.0, urg))
                scored.append((skill, urg, days or 999))
            else:
                st.markdown(f"**{skill}** — Not found in dataset.")
        st.write("---")
        st.subheader(f"Relevance Feedback for {job_input.title()}")
        for skill in skills:
            status, msg = relevance_feedback(skill, job_input)
            if status == "high":
                st.success(msg)
            elif status == "medium":
                st.warning(msg)
            elif status == "low":
                st.error(msg)
            else:
                st.info(msg)

        st.success("✅ Full compatibility analysis complete!")

# --------------------------
# Footer
# --------------------------
st.markdown("---")
st.caption("Smart mode powered demo — detects job↔skill context automatically. For production, connect live APIs for job trends & real market data.")
