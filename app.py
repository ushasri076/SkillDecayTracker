
import streamlit as st
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="SkillDecayTracker Prototype", page_icon="📊", layout="wide")

# Load data
with open("skill_data.json", "r") as f:
    skill_data = json.load(f)

st.title("📊 SkillDecayTracker — Prototype")
st.write("A simple working prototype that demonstrates skill demand trends, suggested adjacent skills, and a basic roadmap. Data is simulated for demo purposes.")

# Sidebar: select skills to compare
st.sidebar.header("Demo Controls")
all_skills = sorted(list(skill_data.keys()))
selected_skills = st.sidebar.multiselect("Select skills to view trend", all_skills[:3], default=all_skills[:2])
user_skills_input = st.text_input("Enter your current skills (comma separated):", value="Python, React")
career_goal = st.text_input("Enter your career goal (e.g., AI Engineer, Web Developer):", value="AI Engineer")

def simulate_time_series(growth_pct, months=12, base=50):
    # Generate a simple simulated monthly time series over `months` months.
    # growth_pct is a yearly growth estimate; convert to monthly multiplier approx.
    monthly_rate = (1 + growth_pct) ** (1/12) - 1
    vals = [base]
    for _ in range(months-1):
        change = vals[-1] * monthly_rate
        noise = random.uniform(-1.5, 1.5)  # small noise
        vals.append(max(1, vals[-1] + change + noise))
    return vals

# Show trend chart for selected skills
if selected_skills:
    months = 12
    dates = [(datetime.now() - timedelta(days=30*(months-i-1))).strftime("%b %Y") for i in range(months)]
    plt.figure(figsize=(10, 4))
    for skill in selected_skills:
        info = skill_data.get(skill, None)
        if info:
            ts = simulate_time_series(info.get("growth_pct", 0.0), months=months, base=random.randint(30,70))
            plt.plot(dates, ts, label=f"{skill} ({info.get('trend')})")
    plt.xticks(rotation=45)
    plt.title("Simulated Skill Demand Trends (last 12 months)")
    plt.xlabel("Month")
    plt.ylabel("Normalized demand (simulated index)")
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()

st.header("🧠 Analyze Your Skills")
if st.button("Analyze My Skills"):
    user_skills = [s.strip().title() for s in user_skills_input.split(",") if s.strip()]
    if not user_skills:
        st.warning("Please enter at least one skill.")
    else:
        st.subheader("Skill Demand Analysis")
        for skill in user_skills:
            info = skill_data.get(skill)
            if info:
                st.markdown(f"**{skill}** — Trend: {info['trend']} ({info['growth']})")
                st.markdown(f"Suggested adjacent skills: {', '.join(info['suggest'])}")
                # Show a small simulated half-life / urgency metric
                # If growth negative -> urgency to reskill high
                urgency = 0.5
                if info.get("growth_pct", 0) < -0.05:
                    urgency = 0.9
                elif info.get("growth_pct",0) < 0:
                    urgency = 0.7
                elif info.get("growth_pct",0) < 0.05:
                    urgency = 0.4
                else:
                    urgency = 0.2
                st.progress(urgency)
                st.write("---")
            else:
                st.markdown(f"**{skill}** — No data available in demo dataset.")
                st.progress(0.4)
                st.write("---")

        st.subheader("🎯 Personalized Learning Roadmap (example)")
        st.markdown(f"Based on your goal *{career_goal}* — a quick starter roadmap:")
        st.markdown("""
        1. Pick 1 core skill to deepen (choose from your list). Take a focused course (4-8 weeks).
        2. Pick 1 adjacent skill suggested above and build a mini-project (1–2 weeks).
        3. Publish the project and get feedback (GitHub / Dev.to / LinkedIn).
        4. Join a mentor program or community and iterate.
        5. Re-run SkillDecayTracker prototype every 3 months to monitor changes.
        """)
        st.success("✅ Demo analysis complete.")

st.markdown("---")
st.caption("This is a prototype with simulated trend data. For a full product, integrate real data sources (job boards, GitHub, StackOverflow) and forecasting models (Prophet/LSTM).")
