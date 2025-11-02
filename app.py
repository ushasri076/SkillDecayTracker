import streamlit as st
import json
import random
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Load skill data
with open("skill_data.json", "r") as f:
    skill_data = json.load(f)

st.set_page_config(page_title="Skill Decay Tracker", page_icon="📊", layout="centered")

st.title("📈 Skill Decay Tracker")
st.markdown("Welcome to Skill Decay Tracker! Analyze how relevant your skills are today and discover which ones are rising or fading in demand.")

# Input fields
skill_input = st.text_input("Enter your skill:", placeholder="e.g., Python, React, SQL")
job_input = st.text_input("Enter your desired job:", placeholder="e.g., Web Developer, Data Scientist")

# Function to simulate skill trend
def simulate_time_series(base_growth, months=12, base=50):
    values = []
    for i in range(months):
        change = base_growth * (i / months) + random.uniform(-2, 2)
        base = max(0, base + change)
        values.append(base)
    return values

# Analyze skill and job
if st.button("Analyze"):
    if skill_input.strip():
        skills = [s.strip() for s in skill_input.split(",") if s.strip()]
        results = []
        for skill in skills:
            data = skill_data.get(skill, None)
            if data:
                trend = data.get("trend", "Stable")
                growth = data.get("growth_pct", 0)
                results.append(f"**{skill}**: {trend} demand ({growth}% growth rate).")
            else:
                results.append(f"**{skill}**: No data available. It might be a niche or outdated skill.")
        
        st.subheader("📊 Skill Insights")
        for r in results:
            st.markdown(r)

        # Simulate relation between skill and job
        if job_input.strip():
            st.subheader("🧠 Job-Skill Match Analysis")
            job = job_input.lower()
            skill = skill_input.lower()
            if ("doctor" in job and "python" in skill) or ("ai" in job and "react" in skill):
                st.warning(f"{skill_input.title()} may not be directly required for a {job_input.title()} role.")
            else:
                st.success(f"{skill_input.title()} is useful or indirectly beneficial for a {job_input.title()} role.")
        
        # Trend chart
        st.subheader("📉 Simulated Skill Demand Over Time")
        months = 12
        dates = [(datetime.now() - timedelta(days=30*(months-i-1))).strftime("%b %Y") for i in range(months)]
        plt.figure(figsize=(10, 4))
        for skill in skills:
            info = skill_data.get(skill, {})
            ts = simulate_time_series(info.get("growth_pct", 0.0), months=months, base=50)
            plt.plot(dates, ts, label=f"{skill} ({info.get('trend', 'N/A')})")
        plt.xticks(rotation=45)
        plt.title("Simulated Skill Demand Trends (last 12 months)")
        plt.xlabel("Month")
        plt.ylabel("Normalized demand (simulated index)")
        plt.legend()
        plt.tight_layout()
        st.pyplot(plt)
        plt.clf()
    else:
        st.warning("Please enter at least one skill!")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit | © 2025 SkillDecayTracker")
