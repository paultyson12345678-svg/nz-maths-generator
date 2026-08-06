import streamlit as st
import random
import os
import io
import json
from google import genai

from curriculum import CURRICULUM_DATA, NZ_THEMES
from exporters import generate_powerpoint_slide, generate_task_pdf, generate_task_card_image

st.set_page_config(page_title="NZ Primary Maths Task Generator", page_icon="🇳🇿", layout="wide")

st.title("🇳🇿 New Zealand Primary Maths Task Generator")
st.markdown("Generate rich, context-aligned mathematical tasks for Phase 1 to Phase 3 (Years 1–8).")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("Task Settings")

# API Key input (checks secrets first, otherwise sidebar input)
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

# Initialize Session State for generated tasks
if "generated_tasks" not in st.session_state:
    st.session_state.generated_tasks = None
if "selected_task_index" not in st.session_state:
    st.session_state.selected_task_index = 0


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
                """

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
                st.session_state.selected_task_index = 0
                st.success("Generated 3 tasks successfully!")

            except Exception as e:
                st.error(f"Error generating tasks: {e}")


# --- TASK DISPLAY & SELECTION ---
if st.session_state.generated_tasks:
    st.subheader("Select one of the generated options:")
    
    t_cols = st.columns(3)
    for idx, task in enumerate(st.session_state.generated_tasks):
        with t_cols[idx]:
            if st.button(f"Option {idx + 1}: {task.get('title', 'Task ' + str(idx + 1))}", key=f"select_t_{idx}", use_container_width=True):
                st.session_state.selected_task_index = idx

    current_task = st.session_state.generated_tasks[st.session_state.selected_task_index]

    st.markdown("---")
    st.header(f"Editing Option {st.session_state.selected_task_index + 1}")

    col1, col2 = st.columns([2, 1])

    with col1:
        task_title = st.text_input("Task Title", current_task.get("title", ""))
        scenario_text = st.text_area("Context & Scenario", current_task.get("scenario", ""), height=120)
        q1_input = st.text_area("Question 1 (Main Task)", current_task.get("q1", ""), height=70)
        q2_input = st.text_area("Question 2 (Follow-up)", current_task.get("q2", ""), height=70)
        ext_input = st.text_area("Extension Challenge", current_task.get("extension", ""), height=70)

    with col2:
        st.subheader("Teacher Notes & Guidance")
        ans1_input = st.text_area("Question 1 Solution & Tip", current_task.get("ans1", ""), height=100)
        ans2_input = st.text_area("Question 2 Solution & Tip", current_task.get("ans2", ""), height=100)

    questions_list = [q1_input, q2_input]
    answers_list = [ans1_input, ans2_input]

    st.markdown("---")
    st.subheader("📥 Export & Download Deliverables")

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    # PPTX Export
    with exp_col1:
        try:
            pptx_data = generate_powerpoint_slide(
                title=task_title, scenario=scenario_text, questions=questions_list,
                extension=ext_input, phase=phase, theme=active_theme, answers=answers_list
            )
            st.download_button(
                label="📊 Download PowerPoint (.pptx)",
                data=pptx_data,
                file_name=f"{task_title.replace(' ', '_')}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
        except Exception as e:
            st.error(f"PowerPoint Export Error: {e}")

    # PDF Export
    with exp_col2:
        try:
            pdf_data = generate_task_pdf(
                title=task_title, scenario=scenario_text, questions=questions_list,
                extension=ext_input, phase=phase, theme=active_theme, answers=answers_list
            )
            st.download_button(
                label="📄 Download Worksheet (.pdf)",
                data=pdf_data,
                file_name=f"{task_title.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF Export Error: {e}")

    # Task Card PNG Export
    with exp_col3:
        try:
            card_data = generate_task_card_image(
                title=task_title, scenario=scenario_text, questions=questions_list, extension=ext_input
            )
            st.download_button(
                label="🖼️ Download Task Card (.png)",
                data=card_data,
                file_name=f"{task_title.replace(' ', '_')}.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Task Card Export Error: {e}")

else:
    st.info("👈 Select your parameters in the sidebar and click **'✨ Generate 3 Tasks'** to generate options!")
