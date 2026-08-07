import streamlit as st
import random
import os
import io
import json
from google import genai

from curriculum import CURRICULUM_DATA, NZ_THEMES
from exporters import generate_powerpoint_slide, generate_task_pdf, generate_task_card_image

st.set_page_config(page_title="Aotearoa Rich Maths Task Generator", page_icon="🇳🇿", layout="wide")

st.title("🇳🇿 Aotearoa Rich Maths Task Generator")
st.markdown("Generate rich, context-aligned mathematical tasks for Phase 1 to Phase 3 (Years 1–8).")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("Task Settings")

# API Key input
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Enter your Google AI Studio API key to generate tasks.")

# 1. Phase Selection
phase = st.sidebar.selectbox("Select Curriculum Phase", list(CURRICULUM_DATA.keys()))

# 2. Year Level Selection based on Phase
year_levels = list(CURRICULUM_DATA[phase].keys())
year_level = st.sidebar.selectbox("Select Year Level", year_levels)

# 3. Strand Selection
strands = list(CURRICULUM_DATA[phase][year_level].keys())
if strands:
    strand = st.sidebar.selectbox("Select Area / Strand", strands)
    available_skills = CURRICULUM_DATA[phase][year_level].get(strand, [])
else:
    st.sidebar.warning(f"No strands configured for {year_level} yet.")
    strand = None
    available_skills = []

# 4. Specific Skill / Objective Selection
if available_skills:
    selected_skill = st.sidebar.selectbox("Select Learning Focus / Skill", available_skills)
else:
    selected_skill = st.sidebar.text_input("Custom Learning Focus", "Solving real-world problems")

# 5. Theme / Context
selected_theme = st.sidebar.selectbox("Select Cultural / NZ Context", NZ_THEMES)
if selected_theme == "Custom Context (Enter your own below)":
    custom_theme = st.sidebar.text_input("Enter Custom Theme", "School Gala")
    active_theme = custom_theme if custom_theme else "School Gala"
else:
    active_theme = selected_theme

st.sidebar.markdown("---")
generate_btn = st.sidebar.button("✨ Generate 3 Tasks", type="primary", use_container_width=True)

# Initialize Session State
if "generated_tasks" not in st.session_state:
    st.session_state.generated_tasks = None


# --- AI GENERATION LOGIC ---
if generate_btn:
    if not api_key:
        st.error("Please enter a valid Gemini API Key in the sidebar to generate tasks.")
    else:
        with st.spinner("Creating 3 context-rich tasks with Gemini..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                You are an expert New Zealand primary school mathematics teacher.
                Create 3 distinct, engaging, context-rich math learning tasks for:
                - Curriculum Phase: {phase}
                - Year Level: {year_level}
                - Learning Area / Strand: {strand}
                - Specific Skill/Focus: {selected_skill}
                - NZ Context/Theme: {active_theme}

                Return ONLY a JSON array containing exactly 3 objects. Do not include markdown formatting or extra text outside JSON.
                Each object must have these exact keys:
                - "title": Short descriptive title
                - "scenario": Realistic, culturally appropriate NZ scenario paragraph setting up the task
                - "q1": Main discussion/problem-solving question
                - "q2": Follow-up or next-step question
                - "extension": An extension challenge question for fast finishers
                - "ans1": Teacher solution/guidance for Question 1
                - "ans2": Teacher solution/guidance for Question 2
                - "ans_ext": Teacher solution/guidance for Extension Challenge
                """

                # Hardcoded to gemini-3.5-flash
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=prompt,
                )
                
                # Parse JSON output
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()
                    
                st.session_state.generated_tasks = json.loads(raw_text)
                st.success("Generated 3 tasks successfully!")

            except Exception as e:
                st.error(f"Error generating tasks: {e}")


# --- 3-COLUMN SIDE-BY-SIDE DISPLAY ---
if st.session_state.generated_tasks:
    st.markdown("---")
    st.header("Generated Task Options")

    cols = st.columns(3)

    for idx, task in enumerate(st.session_state.generated_tasks):
        with cols[idx]:
            st.subheader(f"Option {idx + 1}")
            
            t_title = task.get("title", f"Task {idx + 1}")
            t_scenario = task.get("scenario", "")
            t_q1 = task.get("q1", "")
            t_q2 = task.get("q2", "")
            t_ext = task.get("extension", "")
            t_ans1 = task.get("ans1", "")
            t_ans2 = task.get("ans2", "")
            t_ans_ext = task.get("ans_ext", "")

            # Static display boxes
            st.markdown(f"### **{t_title}**")
            st.markdown(f"**Context & Scenario:**\n\n{t_scenario}")
            st.markdown(f"**Question 1:**\n\n{t_q1}")
            st.markdown(f"**Question 2:**\n\n{t_q2}")
            st.markdown(f"**Extension Challenge:**\n\n{t_ext}")
            
            with st.expander("Teacher Notes & Solutions"):
                st.markdown(f"**Q1 Solution:**\n{t_ans1}")
                st.markdown(f"**Q2 Solution:**\n{t_ans2}")
                st.markdown(f"**Extension Solution:**\n{t_ans_ext}")

            questions_list = [t_q1, t_q2]
            answers_list = [t_ans1, t_ans2, t_ans_ext]

            st.markdown("---")
            st.markdown("#### 📥 Exports")
            
            # PPTX Export
            try:
                pptx_data = generate_powerpoint_slide(
                    title=t_title, scenario=t_scenario, questions=questions_list,
                    extension=t_ext, phase=phase, theme=active_theme, answers=answers_list
                )
                st.download_button(
                    label="📊 PowerPoint (.pptx)",
                    data=pptx_data,
                    file_name=f"{t_title.replace(' ', '_')}.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    key=f"pptx_btn_{idx}",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PPTX Error: {e}")

            # PDF Export
            try:
                pdf_data = generate_task_pdf(
                    title=t_title, scenario=t_scenario, questions=questions_list,
                    extension=t_ext, phase=phase, theme=active_theme, answers=answers_list
                )
                st.download_button(
                    label="📄 Worksheet (.pdf)",
                    data=pdf_data,
                    file_name=f"{t_title.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key=f"pdf_btn_{idx}",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF Error: {e}")

            # PNG Export
            try:
                card_data = generate_task_card_image(
                    title=t_title, scenario=t_scenario, questions=questions_list, extension=t_ext
                )
                st.download_button(
                    label="🖼️ Task Card (.png)",
                    data=card_data,
                    file_name=f"{t_title.replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"png_btn_{idx}",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PNG Error: {e}")

else:
    st.info("👈 Select your parameters in the sidebar and click **'✨ Generate 3 Tasks'** to generate options!")
