import streamlit as st
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="SkillDecayTracker (Smart Prototype)", page_icon="📊", layout="wide")

# --------------------------
# Load data
# --------------------------
with open("skill_data.json", "r") as f:
    skill_data = json.load(f)

st.title("📊 SkillDecayTracker — Smart Prototype")
st.write("Analyze multiple skills at once, view demand trends, and get job-aware recommendations. (Demo data)")

# --------------------------
# Sidebar controls
# --------------------------
st.sidebar.header("Controls")
all_skills = sorted(skill_data.keys())
selected_for_chart = st.sidebar.multiselect("Select skills to view trend chart", all_skills, default=all_skills[:3])

st.sidebar.markdown("---")
st.sidebar.markdown("**Analyze skills for a job**")
job = st.sidebar.text_input("Target job (e.g., Doctor, AI Engineer, Software Developer)", value="AI Engineer")
user_skills_input = st.sidebar.text_input("Enter your current skills (comma separated)", value="Python, React, SQL")

# --------------------------
# Helper functions
# --------------------------
def simulate_time_series(growth_pct, months=12, base=50):
    # Deterministic monthly trend based on growth_pct
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
    # returns a 0..1 urgency value
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

# Job to skills mapping (domain knowledge)
job_skills = {
    "doctor": ["biology", "anatomy", "medical research", "diagnosis", "pharmacology", "patient communication", "clinical trials"],
    "ai engineer": ["python", "machine learning", "deep learning", "pytorch", "tensorflow", "data engineering", "ml ops"],
    "software developer": ["python", "java", "c++", "dsa", "algorithms", "git", "testing", "system design"],
    "web developer": ["html", "css", "javascript", "react", "node.js", "next.js", "typescript"],
    "data analytics": ["sql", "excel", "python", "power bi", "tableau", "statistics", "data cleaning"],
    "data scientist": ["python", "machine learning", "statistics", "sql", "pandas", "scikit-learn", "deep learning"],
    "teacher": ["communication", "lesson planning", "subject expertise", "assessment", "mentoring"]
}

def relevance_feedback(skill, job):
    skill_l = skill.lower()
    job_l = job.lower().strip()
    # Exact match in mapping
    if job_l in job_skills:
        if skill_l in [s.lower() for s in job_skills[job_l]]:
            return "high", f"✅ **{skill}** is highly relevant for a {job}."
        # partial match (e.g., python relevant for many)
        for s in job_skills[job_l]:
            if skill_l in s.lower() or s.lower() in skill_l:
                return "medium", f"⚠️ **{skill}** is somewhat relevant for a {job}."
        # If skill not in domain mapping
        suggestions = ", ".join(job_skills[job_l][:4])
        return "low", f"❌ **{skill}** is not a typical core skill for a {job}. Consider focusing on: {suggestions}."
    else:
        # unknown job
        return "unknown", f"ℹ️ I don't have structured data for the job '{job}' yet."

# --------------------------
# Trend Chart
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
# Analysis: multiple skills
# --------------------------
st.header("🧠 Multi-skill Analysis & Job-aware Recommendations")
if st.button("Analyze"):
    skills = [s.strip() for s in user_skills_input.split(",") if s.strip()]
    if not skills:
        st.warning("Please enter at least one skill.")
    else:
        # Show per-skill analysis
        st.subheader("Skill status")
        scored = []
        for skill in skills:
            info = skill_data.get(skill, None)
            if info:
                days = days_since(info.get("last_used", ""))
                urg = urgency_score_from_days(days)
                growth = info.get("growth", "N/A")
                st.markdown(f"**{skill}** — Trend: {info.get('trend','N/A')} ({growth}) — Last used: {info.get('last_used','unknown')} — Urgency: {int(urg*100)}%")
                st.markdown(f"Suggested adjacent skills: {', '.join(info.get('suggest', []))}")
                st.progress(min(1.0, urg))
                scored.append((skill, urg, days or 999))
                st.write("---")
            else:
                # Unknown skill in dataset
                st.markdown(f"**{skill}** — Not present in demo dataset. Consider adding it to skill_data.json.")
                st.write("---")

        # Overall recommended next actions
        st.subheader("🎯 Recommended immediate actions")
        if scored:
            # sort by urgency then days
            scored.sort(key=lambda x: (x[1], x[2]), reverse=True)
            for skill, urg, days in scored[:5]:
                days_text = f"{days} days inactive" if days != 999 else "unknown last-used"
                st.markdown(f"- **{skill}** — Urgency: {int(urg*100)}% — {days_text}")
        else:
            st.info("No known skills to score from the list provided.")

        # Job-aware relevance block
        st.subheader(f"🔎 Job-aware relevance for: {job}")
        for skill in skills:
            status, msg = relevance_feedback(skill, job)
            if status == "high":
                st.success(msg)
            elif status == "medium":
                st.warning(msg)
            elif status == "low":
                st.error(msg)
            else:
                st.info(msg)

        # Suggest cross-skill roadmap depending on job
        st.subheader("📚 Roadmap suggestions (example)")
        job_l = job.lower().strip()
        if job_l in job_skills:
            staples = job_skills[job_l][:4]
            st.markdown(f"For a **{job}**, focus on: **{', '.join(staples)}**. Start by building one small project combining two of these skills, then publish on GitHub and share for feedback.")
        else:
            st.markdown("Unable to show job-specific roadmap — job not in our demo taxonomy. Consider selecting a common job like 'AI Engineer' or 'Web Developer'.")

        st.success("✅ Analysis complete.")

# --------------------------
# Footer / explanation
# --------------------------
st.markdown("---")
st.caption("Notes: This demo uses simulated trend curves and a domain mapping for job↔skill relevance. For production, integrate real labor-market signals (job boards, GitHub, Stack Overflow) and an NLP-based skill extractor.")
