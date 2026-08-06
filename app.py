# app.py
import streamlit as st
import json
import os
from openai import OpenAI
from curriculum import CURRICULUM_DATA, NZ_THEMES
from exporters import generate_powerpoint_slide, generate_task_card_image

st.set_page_config(page_title="NZ Maths Rich Task Generator", page_icon="🇳🇿", layout="wide")

st.title("🇳🇿 Aotearoa NZ Maths Rich Task Generator")
st.caption("Aligned with the Refreshed NZC Mathematics & Statistics Learning Sequences")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Curriculum Parameters")

phase = st.sidebar.selectbox("Select Phase / Year Level", list(CURRICULUM_DATA.keys()))
strand = st.sidebar.selectbox("Select Area / Strand", list(CURRICULUM_DATA[phase].keys()))
skills = st.sidebar.multiselect("Select Specific Skills / Objectives", CURRICULUM_DATA[phase][strand])

st.sidebar.header("2. Context & Theme")
selected_theme = st.sidebar.selectbox("Choose a Theme / Event", NZ_THEMES)

if selected_theme == "Custom Context (Enter your own below)":
    custom_theme = st.sidebar.text_input("Custom Context", value="School Bus Schedules & Timetables")
    final_theme = custom_theme
else:
    final_theme = selected_theme

additional_keywords = st.sidebar.text_input("Additional Directives (optional)", placeholder="e.g., multi-step word problem, include chart data")

# API Key Check
api_key = os.environ.get("OPENAI_API_KEY") or st.sidebar.text_input("Enter OpenAI API Key", type="password")

# --- GENERATION LOGIC ---
if st.sidebar.button("✨ Generate 3 Rich Task Options", type="primary"):
    if not skills:
        st.warning("Please select at least one skill keyword from the sidebar.")
    elif not api_key:
        st.error("Please add your OPENAI_API_KEY to secrets or enter it in the sidebar.")
    else:
        prompt = f"""
        You are an expert Aotearoa New Zealand mathematics educator.
        Target Phase: {phase}
        Strand/Area: {strand}
        Target Skills: {', '.join(skills)}
        Context/Theme: {final_theme}
        Extra Directives: {additional_keywords}

        Generate 3 distinct rich math tasks using NZ English, Te Ao Māori concepts where natural, and local cultural/practical contexts.
        Return ONLY valid JSON with this structure:
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
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            parsed = json.loads(response.choices[0].message.content)
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
