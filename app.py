import streamlit as st
import random
import os
import io
import json
import time
from google import genai
from curriculum import CURRICULUM_DATA, NZ_THEMES, STRAND_KEYWORDS
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
st.markdown("Generate rich, context-aligned mathematical tasks for Phase 1 to Phase 4 (Years 1–10).")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("Task Settings")

# --- DONATION / SUPPORT BUTTON ---
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 15px;">
        <p style="font-size: 0.85em; color: #666; margin-bottom: 8px;">Help keep this generator free for teachers!</p>
        <a href="https://www.buymeacoffee.com/paultyson" target="_blank">
            <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important; width: 145px !important;" >
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

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

# 5. Strand Keywords Selection (Checkboxes, collapsed/contracted by default)
available_keywords = STRAND_KEYWORDS.get(strand, []) if strand else []
selected_keywords = []

if available_keywords:
    st.sidebar.write("**Select Keywords:**")
    with st.sidebar.expander("View Keywords", expanded=False):
        for kw in available_keywords:
            if st.checkbox(kw, value=False, key=f"kw_{strand}_{kw}"):
                selected_keywords.append(kw)

# 6. Theme / Context
selected_theme = st.sidebar.selectbox("Select Context", NZ_THEMES)
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
            client = genai.Client(api_key=api_key)
            
            # Format selected keywords for the prompt
            keywords_str = ", ".join(selected_keywords) if selected_keywords else "None selected"
            
            prompt = f"""
            You are an expert primary school mathematics specialist in Aotearoa New Zealand.
            Generate 3 rich, authentic mathematical tasks for New Zealand classrooms using the updated NZ Curriculum parameters below:

            - Curriculum Phase: {phase} ({year_level})
            - Area / Strand: {strand}
            - Targeted Strand Keywords / Concepts: {keywords_str}
            - Learning Focus / Skill: {selected_skill}
            - Theme / Context: {theme_context}

            Guidelines for Tasks:
            1. Task 1 MUST feature a Māori bicultural context, integrating te reo Māori terms (e.g., tamariki, waka, kai, marae) appropriately with correct macrons.
            2. Task 2 MUST feature a Pasifika cultural context (e.g., Samoan, Tongan, Cook Island Māori, Fijian) reflecting Pacific communities in Aotearoa.
            3. Task 3 MUST feature a general Kiwi/European New Zealand context (e.g., typical NZ school life, farming, local sports, or community events).
            4. Explicitly integrate and focus on the selected targeted strand keywords ({keywords_str}) across the task scenarios, questions, and solutions where relevant.
            5. Each task must have 2 main questions and 1 extension challenge that progress in depth/complexity.
            
            CRITICAL EXTENSION TASK PROTOCOL (LOW FLOOR, HIGH CEILING):
            - The extension challenge MUST follow a Low Floor, High Ceiling model.
            - It MUST be open-ended with multiple valid approaches, strategies, or solutions (NOT a single fixed numerical answer).
            - Low Floor: The entry point should be clear and accessible so all students can start immediately.
            - High Ceiling: Offers depth, generalisation, or multiple solution paths for advanced students.
            - Use prompts like: "Find at least three different ways...", "Design a scenario where...", "What happens if...", or "Create a general rule that...".

            SOLUTION & TEACHER GUIDANCE FORMATTING:
            - For Question 1 & Question 2: Provide a step-by-step worked solution and final answer.
            - For Extension Challenge:
              - Explicitly state that answers will vary due to the open-ended nature.
              - Provide 2-3 sample valid solutions / exemplary student responses.
              - Include brief Teacher Guidance on key mathematical strategies or generalisations to look out for during assessment.

            6. Include a section identifying common student misconceptions for the task and how teachers can proactively address them.
            7. Ensure tone is supportive, culturally responsive, and mathematically sound.
            8. CRITICAL: Do NOT use any unescaped double quotes (") inside your text strings. Use single quotes (') instead to prevent JSON parsing errors.

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
                "misconceptions": "Common student misconceptions and how to guide them...",
                "answers": [
                  "Detailed solution for Question 1...",
                  "Detailed solution for Question 2...",
                  "Sample solutions & teacher guidance for Extension..."
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
                # Clean up the response text to remove any accidental markdown blocks
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:-3].strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text[3:-3].strip()
                
                try:
                    tasks = json.loads(raw_text)
                    st.session_state['generated_tasks'] = tasks
                    st.session_state['current_params'] = {
                        'phase': phase,
                        'year_level': year_level,
                        'theme': theme_context
                    }
                except json.JSONDecodeError as json_err:
                    st.error("The AI generated invalid text formatting. Please click 'Generate 3 Tasks' again to retry.")
            elif not response:
                st.error("Could not generate tasks. Please verify your API key in Google AI Studio.")

        except Exception as e:
            st.error(f"Error initializing AI client: {str(e)}")

# --- DISPLAY GENERATED TASKS & EXPORTS ---
if 'generated_tasks' in st.session_state and st.session_state['generated_tasks']:
    tasks = st.session_state['generated_tasks']
    params = st.session_state.get('current_params', {'phase': phase, 'year_level': year_level, 'theme': theme_context})

    st.markdown("---")
    st.header("✨ Generated Task Options")
    st.write("Review the scenarios and teacher notes below. Download the slides or worksheet to access the full tasks and answers!")

    # Create Tabs instead of columns
    tab_list = st.tabs([f"Option {i+1}" for i in range(len(tasks))])

for i, (tab, task) in enumerate(zip(tab_list, tasks)):
        with tab:
            with st.container(border=True): 
                st.subheader(task['title'])
                
                st.markdown(f"**Scenario:**\n{task['scenario']}")
                
                with st.expander("👩‍🏫 Teacher Notes & Misconceptions"):
                    if task.get('misconceptions'):
                        st.markdown(
                            f"""
                            <div style="background-color: #2c3e50; padding: 15px; border-radius: 8px;">
                                <p style="color: white; margin: 0;"><b>💡 Common Misconceptions:</b><br>{task['misconceptions']}</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    else:
                        st.write("No specific misconceptions identified for this task.")

                st.divider()

                # --- CORRECTED INDENTATION & FILE NAMES START HERE ---
                
                # We replace spaces with underscores so the file name is clean
                safe_title = task.get('title', f'Maths_Task_Option_{i+1}').replace(' ', '_')
                
               # Export Buttons (Now properly indented inside the tab container!)
                col1, col2 = st.columns(2)
                
                with col1:
                    # Generate PPT data safely fetching phase/theme from PARAMS
                    ppt_data = generate_powerpoint_slide(
                        title=task.get('title', 'Maths Task'),
                        scenario=task.get('scenario', ''),
                        questions=task.get('questions', []),
                        extension=task.get('extension', ''),
                        phase=params.get('phase', 'N/A'),     # <--- CHANGED TO params
                        theme=params.get('theme', 'General'), # <--- CHANGED TO params
                        answers=task.get('answers', []),
                        teacher_notes=task.get('teacher_notes', ''),
                        misconceptions=task.get('misconceptions', '')
                    )
                    if ppt_data:
                        st.download_button(
                            label="📥 Download PowerPoint",
                            data=ppt_data,
                            file_name=f"{safe_title}.pptx", 
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            key=f"download_ppt_{i}"
                        )
                    else:
                        st.info("PowerPoint exporter not found/configured.")

                with col2:
                    # Generate PDF data safely fetching phase/theme from PARAMS
                    pdf_data = generate_task_pdf(
                        title=task.get('title', 'Maths Task'),
                        scenario=task.get('scenario', ''),
                        questions=task.get('questions', []),
                        extension=task.get('extension', ''),
                        phase=params.get('phase', 'N/A'),     # <--- CHANGED TO params
                        theme=params.get('theme', 'General'), # <--- CHANGED TO params
                        answers=task.get('answers', [])
                    )
                    if pdf_data:
                        st.download_button(
                            label="📥 Download Worksheet (PDF)",
                            data=pdf_data,
                            file_name=f"{safe_title}.pdf", 
                            mime="application/pdf",
                            key=f"download_pdf_{i}"
                        )
                    else:
                        st.info("Worksheet exporter not found/configured.")
