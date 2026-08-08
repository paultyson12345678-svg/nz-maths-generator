import streamlit as st
import random
import os
import io
import json
import time
from google import genai
from curriculum import CURRICULUM_DATA, NZ_THEMES
from exporters import generate_powerpoint_slide, generate_task_pdf

# Set page configuration first
st.set_page_config(page_title="Rich Maths Task Generator", page_icon="🇳🇿", layout="wide")

# --- ACCESS CONTROL GATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Remember access across refreshes/bookmarks
if st.query_params.get("auth") == "approved":
    st.session_state.authenticated = True

if not st.session_state.authenticated:
    st.title("🔒 Restricted Access")
    st.write("This generator is currently in testing for Marshland School staff and invited teachers.")
    
    email = st.text_input("Enter your school email address:").strip().lower()
    guest_code = st.text_input("Guest Passcode (for external reviewers):", type="password").strip()
    
    if st.button("Access Generator", type="primary"):
        # Automatically approve Marshland staff domain OR correct guest code
        if email.endswith("@marshland.school.nz") or guest_code == "KiaOra2026":
            st.session_state.authenticated = True
            st.query_params["auth"] = "approved"  # Remembers authentication in URL
            st.rerun()
        else:
            st.error("Access denied. Please enter a valid Marshland School email address or guest passcode.")
            
    st.stop()  # Prevents the rest of the app from loading until authenticated
# ---------------------------

st.title("🇳🇿 Rich Maths Task Generator")
st.markdown("Generate rich, context-aligned mathematical tasks for Phase 1 to Phase 3 (Years 1–8).")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("Task Settings")

# Check if secret exists in Streamlit Cloud Secrets
default_api_key = st.secrets.get("GEMINI_API_KEY", "")

if default_api_key:
    api_key = default_api_key
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Enter your Google AI Studio API key.")

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
    custom_theme = st.sidebar.text_input("Enter Custom Context / Local Story", "Community Garden Project")
    theme_context = custom_theme
else:
    theme_context = selected_theme

# --- GENERATION LOGIC ---
if st.sidebar.button("✨ Generate 3 Tasks", type="primary"):
    if not api_key:
        st.error("Please enter a valid Gemini API Key in the sidebar or configure it in secrets.")
    else:
        try:
            # Using the modern SDK without API version overrides, pointing to the current stable model
            client = genai.Client(api_key=api_key)
            
            prompt = f"""
            You are an expert primary school mathematics specialist in Aotearoa New Zealand.
            Generate 3 rich, authentic mathematical tasks for New Zealand classrooms using the updated NZ Curriculum parameters below:

            - Curriculum Phase: {phase} ({year_level})
            - Learning Focus / Skill: {selected_skill}
            - Cultural / Local Context: {theme_context}

            Guidelines for Tasks:
            1. Integrate local NZ contexts, te reo Māori terms (e.g., tamariki, waka, kai, marae, whānau) appropriately with correct macrons.
            2. Each task must have 2 main questions and 1 extension challenge that progress in depth/complexity.
            3. Include clear solutions and teacher guidance notes for all questions.
            4. Ensure tone is supportive, culturally responsive, and mathematically sound.

            Output strictly as a JSON array containing exactly 3 objects.
            Format structure:
            [
              {{
                "title": "Task Title",
                "scenario": "Rich context paragraph describing the situation...",
                "questions": [
                  "Question 1 text...",
                  "Question 2 text..."
                ],
                "extension": "Extension challenge text...",
                "answers": [
                  "Detailed solution for Question 1...",
                  "Detailed solution for Question 2...",
                  "Detailed solution for Extension..."
                ]
              }}
            ]
            """

            response = None
            
            with st.spinner("Crafting rich mathematical tasks with Gemini AI..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=prompt,
                        config={'response_mime_type': 'application/json'}
                    )
                except Exception as err:
                    st.error(f"Generation failed: {err}")

            if response and response.text:
                tasks = json.loads(response.text)
                st.session_state['generated_tasks'] = tasks
                st.session_state['current_params'] = {
                    'phase': phase,
                    'year_level': year_level,
                    'theme': theme_context
                }
            elif not response:
                st.error("Could not generate tasks. Please verify your API key in Google AI Studio.")

        except Exception as e:
            st.error(f"Error initializing AI client: {str(e)}")

# --- DISPLAY GENERATED TASKS & EXPORTS ---
if 'generated_tasks' in st.session_state and st.session_state['generated_tasks']:
    tasks = st.session_state['generated_tasks']
    params = st.session_state.get('current_params', {'phase': phase, 'year_level': year_level, 'theme': theme_context})

    st.markdown("---")
    st.header("Generated Task Options")

    for i, task in enumerate(tasks):
        with st.container():
            st.subheader(f"Option {i + 1}: {task['title']}")
            
            st.markdown(f"**Context & Scenario:**\n{task['scenario']}")
            
            for q_idx, q in enumerate(task['questions']):
                st.markdown(f"**Question {q_idx + 1}:** {q}")
            
            if task.get('extension'):
                st.markdown(f"**Extension Challenge:** {task['extension']}")
            
            with st.expander("Teacher Notes & Solutions"):
                for a_idx, ans in enumerate(task.get('answers', [])):
                    label = f"Q{a_idx + 1} Solution:" if a_idx < len(task['questions']) else "Extension Solution:"
                    st.markdown(f"**{label}** {ans}")

            col1, col2 = st.columns(2)
            with col1:
                pptx_data = generate_powerpoint_slide(
                    title=task['title'],
                    scenario=task['scenario'],
                    questions=task['questions'],
                    extension=task.get('extension', ''),
                    phase=params['phase'],
                    theme=params['theme'],
                    answers=task.get('answers', [])
                )
                st.download_button(
                    label="📊 Download PowerPoint (.pptx)",
                    data=pptx_data,
                    file_name=f"{task['title'].replace(' ', '_')}_Presentation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    key=f"pptx_{i}"
                )

            with col2:
                pdf_data = generate_task_pdf(
                    title=task['title'],
                    scenario=task['scenario'],
                    questions=task['questions'],
                    extension=task.get('extension', ''),
                    phase=params['phase'],
                    theme=params['theme'],
                    answers=task.get('answers', [])
                )
                st.download_button(
                    label="📄 Download Worksheet (.pdf)",
                    data=pdf_data,
                    file_name=f"{task['title'].replace(' ', '_')}_Worksheet.pdf",
                    mime="application/pdf",
                    key=f"pdf_{i}"
                )
            
            st.markdown("---")
