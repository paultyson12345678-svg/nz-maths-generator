# app.py
import streamlit as st
import json
import os
from google import genai
from curriculum import CURRICULUM_DATA, NZ_THEMES
from exporters import generate_powerpoint_slide, generate_task_card_image, generate_task_pdf

st.set_page_config(page_title="NZ Maths Rich Task Generator", page_icon="🇳🇿", layout="wide")

st.title("🇳🇿 Aotearoa NZ Maths Rich Task Generator")
st.caption("Aligned with the Refreshed NZC Mathematics & Statistics Learning Sequences")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Curriculum Parameters")

phase = st.sidebar.selectbox("Select Curriculum Phase", list(CURRICULUM_DATA.keys()))
year_levels = list(CURRICULUM_DATA[phase].keys())
year_level = st.sidebar.selectbox("Select Year Level", year_levels)
# Safely pull available strands specifically defined for this phase and year level
strands = list(CURRICULUM_DATA.get(phase, {}).get(year_level, {}).keys())

if strands:
    strand = st.sidebar.selectbox("Select Area / Strand", strands)
    available_skills = CURRICULUM_DATA[phase][year_level].get(strand, [])
else:
    st.sidebar.warning(f"No strands configured for {year_level} yet.")
    strand = None
    available_skills = []

st.sidebar.header("2. Context & Theme")
selected_theme = st.sidebar.selectbox("Choose a Theme / Event", NZ_THEMES)

if selected_theme == "Custom Context (Enter your own below)":
    custom_theme = st.sidebar.text_input("Custom Context", value="School Bus Schedules & Timetables")
    final_theme = custom_theme
else:
    final_theme = selected_theme

additional_keywords = st.sidebar.text_input("Additional Directives (optional)", placeholder="e.g., multi-step word problem, include chart data")

api_key = os.environ.get("GEMINI_API_KEY") or st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- GENERATION LOGIC ---
if st.sidebar.button("✨ Generate 3 Rich Task Options", type="primary"):
    if not skills:
        st.warning("Please select at least one skill keyword from the sidebar.")
    elif not api_key:
        st.error("Please enter a valid Gemini API Key.")
    else:
        prompt = f"""
You are an expert Aotearoa New Zealand mathematics educator.
Target Phase: {phase}
Target Year Level: {year_level}
Strand/Area: {strand}
Target Skills: {', '.join(skills)}
Context/Theme: {final_theme}
Extra Directives: {additional_keywords}

Generate 3 distinct rich math tasks appropriate specifically for {year_level} students using NZ English, Te Ao Māori concepts where natural, and local cultural contexts. Include step-by-step answers and teacher notes for each question.

CRITICAL INSTRUCTIONS FOR JSON OUTPUT:
- Return ONLY a valid, raw JSON object.
- Do NOT use double quotes inside strings; use single quotes (') for any quotes or conversation inside scenarios or questions.
- Match this exact JSON structure:

{{
    "tasks": [
        {{
            "title": "Task Title",
            "scenario": "Rich scenario paragraph introducing the problem",
            "questions": ["Question 1", "Question 2"],
            "extension": "Extension question for fast finishers",
            "answers": ["Solution & explanation for Q1", "Solution & explanation for Q2"]
        }}
    ]
}}
"""

        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            
            # Clean up potential markdown formatting code blocks if returned
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            parsed = json.loads(clean_text)
            tasks = parsed.get("tasks", [])
            st.session_state["tasks"] = tasks
            st.session_state["generated_phase"] = phase
            st.session_state["generated_theme"] = final_theme
            
        except Exception as e:
            st.error(f"Error generating tasks: {e}")

# --- DISPLAY OPTIONS & EXPORT ---
if "tasks" in st.session_state and st.session_state["tasks"]:
    st.subheader("Generated Tasks")
    
    tasks = st.session_state["tasks"]
    cols = st.columns(len(tasks))
    
    for idx, (col, task) in enumerate(zip(cols, tasks)):
        with col:
            st.markdown(f"### Option {idx + 1}: {task['title']}")
            st.info(task['scenario'])
            
            st.write("**Questions:**")
            for q_idx, q in enumerate(task['questions'], 1):
                st.write(f"{q_idx}. {q}")
                
            st.success(f"**Extension:** {task['extension']}")
            
            # Show Answer Key Accordion
            if "answers" in task:
                with st.expander("📝 View Teacher Answer Key & Guidance"):
                    for q_idx, ans in enumerate(task['answers'], 1):
                        st.write(f"**Q{q_idx}:** {ans}")
            
            st.markdown("---")
            
            # Printable PDF Worksheet Download (Includes Working Boxes & Teacher Answer Page)
            pdf_bytes = generate_task_pdf(
                task['title'], 
                task['scenario'], 
                task['questions'], 
                task['extension'], 
                st.session_state["generated_phase"], 
                st.session_state["generated_theme"],
                task.get("answers")
            )
            st.download_button(
                label="📄 Download Student Worksheet PDF",
                data=pdf_bytes,
                file_name=f"Maths_Worksheet_Task_{idx + 1}.pdf",
                mime="application/pdf",
                key=f"pdf_{idx}"
            )
            
            # Google Slides (.pptx) Download (Includes Lesson Presentation + Answer Slide)
            pptx_bytes = generate_powerpoint_slide(
                task['title'], 
                task['scenario'], 
                task['questions'], 
                task['extension'], 
                st.session_state["generated_phase"], 
                st.session_state["generated_theme"],
                task.get("answers")
            )
            st.download_button(
                label="📥 Download Lesson Slide (.pptx)",
                data=pptx_bytes,
                file_name=f"Maths_Lesson_Slide_{idx + 1}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                key=f"pptx_{idx}"
            )
