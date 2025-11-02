import streamlit as st
import json
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# --------------------------
# Load skill data
# --------------------------
with open("skill_data.json", "r") as f:
    skill_data = json.load(f)

# --------------------------
# Page title and description
# --------------------------
st.set_page_config(page_title="Skill Decay Tracker", page_icon="📊", layout="centered")
st.title("📈 Skill Decay Tracker")
st.markdown("""
Welcome to **SkillDecayTracker** – an intelligent tool that helps you identify which skills are becoming less relevant 
and which are **in-demand** based on your career goal.  
You can enter multiple skills and your target job, and the AI will analyze them.
""")

# --------------------------
# User Inputs
# --------------------------
skills_input = st.text_input("Enter your skills (comma separated):", placeholder="e.g., Python, React, SQL")
job_input = st.text_input("Enter your desired job:", placeholder="e.g., Data Scientist, Web Developer")

# --------------------------
# Analysis Logic
# --------------------------
def analyze_skills(skills, job):
    report = []
    recommendations = []
    skill_scores = {}
    
    for sk in skills:
        info = skill_data.get(sk, None)
        if info:
            skill_scores[sk] = info.get("growth_pct", 0.0)
            trend = info.get("trend", "Stable")
            report.append(f"**{sk}**: {trend} demand ({info.get('growth_pct', 0.0)}% growth rate)")
        else:
            report.append(f"**{sk}**: Not found in database — may be niche or outdated.")
            skill_scores[sk] = random.uniform(-5, 5)
    
    # Job relevance logic
    job = job.lower()
    job_skill_map = {
        "data scientist": ["Python", "SQL", "Machine Learning", "Data Analysis"],
        "web developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
        "software developer": ["C++", "Java", "DSA", "OOP", "SQL"],
        "ai engineer": ["Python", "TensorFlow", "Machine Learning", "Deep Learning"],
        "teacher": ["Communication", "Creativity", "Adaptability"],
        "doctor": ["Medical Knowledge", "Empathy", "Diagnosis"],
        "data analyst": ["Python", "Excel", "SQL", "Power BI"],
    }
    
    relevant = job_skill_map.get(job, [])
    if relevant:
        missing = [s for s in relevant if s.lower() not in [x.lower() for x in skills]]
        if missing:
            recommendations.append(f"To be a better **{job.title()}**, consider learning: {', '.join(missing)}.")
        else:
            recommendations.append(f"✅ You already have strong skills for a **{job.title()}** role.")
    else:
        recommendations.append(f"Could not find a predefined profile for **{job.title()}**, but here’s your skill insight.")
    
    # Summarize top & low growth
    top = max(skill_scores, key=skill_scores.get)
    low = min(skill_scores, key=skill_scores.get)
    summary = f"Highest trending skill: **{top}** ({skill_scores[top]}%) | Lowest: **{low}** ({skill_scores[low]}%)"
    
    return report, recommendations, skill_scores, summary


# --------------------------
# Display Results
# --------------------------
if st.button("Analyze"):
    if skills_input.strip():
        skills = [s.strip() for s in skills_input.split(",") if s.strip()]
        report, recs, scores, summary = analyze_skills(skills, job_input)
        
        st.subheader("📊 Skill Insights")
        for r in report:
            st.markdown(r)
        
        st.markdown("---")
        st.subheader("🎯 Job Fit Analysis")
        for r in recs:
            st.markdown(r)
        
        st.info(summary)
        
        # Trend chart for selected skills
        st.markdown("---")
        st.subheader("📉 Skill Demand Trend Simulation")
        
        months = 12
        dates = [(datetime.now() - timedelta(days=30 * (months - i - 1))).strftime("%b %Y") for i in range(months)]
        plt.figure(figsize=(10, 4))
        
        for sk in skills:
            info = skill_data.get(sk, {})
            growth = info.get("growth_pct", random.uniform(-5, 10))
            base = 50
            trend_curve = [base + (i * growth * 1.5) + (random.uniform(-3, 3)) for i in range(months)]
            plt.plot(dates, trend_curve, label=f"{sk} ({info.get('trend', 'Unknown')})")
        
        plt.xticks(rotation=45)
        plt.title("Skill Demand Trends (Simulated over 12 months)")
        plt.xlabel("Month")
        plt.ylabel("Relative Demand Index")
        plt.legend()
        plt.tight_layout()
        st.pyplot(plt)
        plt.clf()
        
    else:
        st.warning("Please enter at least one skill!")

# --------------------------
# Footer
# --------------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | © 2025 SkillDecayTracker")
