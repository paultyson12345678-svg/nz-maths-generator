# app.py
import streamlit as st
import json
import os
from google import genai
from curriculum import CURRICULUM_DATA, NZ_THEMES
from exporters import generate_powerpoint_slide, generate_task_card_image

st.set_page_config(page_title="NZ Maths Rich Task Generator", page_icon="🇳🇿", layout="wide")

st.title("🇳🇿 Aotearoa NZ Maths Rich Task Generator")
st.caption("Aligned with the Refreshed NZC Mathematics & Statistics Learning Sequences")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Curriculum Parameters")

# 1. Phase Dropdown
phase = st.sidebar.selectbox("Select Curriculum Phase", list(CURRICULUM_DATA.keys()))

# 2. Year Level Dropdown (Filtered by selected Phase)
year_levels = list(CURRICULUM_DATA[phase].keys())
year_level = st.sidebar.selectbox("Select Year Level", year_levels)

# 3. Strand Dropdown (Filtered by Year Level)
strands = list(CURRICULUM_DATA[phase][year_level].keys())
strand = st.sidebar.selectbox("Select Area / Strand", strands)

# 4. Specific Skills Multiselect (Filtered by Strand)
available_skills = CURRICULUM_DATA[phase][year_level][strand]
skills = st.sidebar.multiselect("Select Specific Skills / Objectives", available_skills)

st.sidebar.header("2. Context & Theme")
selected_theme = st.sidebar.selectbox("Choose a Theme / Event", NZ_THEMES)

if selected_theme == "Custom Context (Enter your own below)":
    custom_theme = st.sidebar.text_input("Custom Context", value="School Bus Schedules & Timetables")
    final_theme = custom_theme
else:
    final_theme = selected_theme

additional_keywords = st.sidebar.text_input("Additional Directives (optional)", placeholder="e.g., multi-step word problem, include chart data")

# API Key Check
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
        Strand/Area: {strand}
        Target Skills: {', '.join(skills)}
        Context/Theme: {final_theme}
        Extra Directives: {additional_keywords}

        Generate 3 distinct rich math tasks using NZ English, Te Ao Māori concepts where natural, and local cultural/practical contexts.
        Return ONLY valid JSON matching this exact structure:
        {{
            "tasks": [
                {{
                    "title": "Task Title",
                    "scenario": "Rich scenario paragraph introducing the problem",
                    "questions": ["Question 1", "Question 2"],
                    "extension": "Extension question for fast finishers"
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
            
            parsed = json.loads(response.text)
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
            st.markdown("---")
            
            # Google Slides (.pptx) Download
            pptx_bytes = generate_powerpoint_slide(
                task['title'], 
                task['scenario'], 
                task['questions'], 
                task['extension'], 
                st.session_state["generated_phase"], 
                st.session_state["generated_theme"]
            )
            st.download_button(
                label="📥 Download Google Slide (.pptx)",
                data=pptx_bytes,
                file_name=f"Maths_Task_{idx + 1}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                key=f"pptx_{idx}"
            )
            
            # PNG Image Download
            img_bytes = generate_task_card_image(
                task['title'], 
                task['scenario'], 
                task['questions'], 
                task['extension']
            )
            st.download_button(
                label="🖼️ Download PNG Image",
                data=img_bytes,
                file_name=f"Maths_Task_{idx + 1}.png",
                mime="image/png",
                key=f"img_{idx}"
            )
