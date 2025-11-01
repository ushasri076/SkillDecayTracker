# SkillDecayTracker (Prototype)

A working Streamlit prototype that simulates skill demand trends and recommends adjacent skills and a simple learning roadmap.

## What this includes
- `app.py` — Streamlit application (demo)
- `skill_data.json` — sample skill data used to simulate trends
- `requirements.txt` — Python dependencies

## How to use
1. Upload the repository to GitHub.
2. Deploy on Hugging Face Spaces (Streamlit) or Streamlit Cloud:
   - For Hugging Face Spaces: create a new Space, choose Streamlit, and upload the repo files.
   - For Streamlit Cloud: connect your GitHub repo and deploy.

## Run locally (optional)
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run:
   ```
   streamlit run app.py
   ```

## Notes
- The trend chart is simulated from simple growth percentages and random noise — intended for demo purposes.
- To convert this to a real system, integrate real-time data ingestion, NLP-based skill extraction, and forecasting models.
