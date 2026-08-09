import streamlit as st
import json
import google.generativeai as genai
from curriculum import NZ_THEMES, CURRICULUM_DATA, STRAND_KEYWORDS, GET_PROMPT

# Import export functions from your existing exporters.py
try:
    from exporters import generate_powerpoint_slide, generate_pdf_worksheet
except ImportError:
    # Fallback to prevent crashes if not found
    def generate_powerpoint_slide(*args, **kwargs): return b""
    def generate_pdf_worksheet(*args, **kwargs): return b""

# Streamlit Page Setup
st.set_page_config(
    page_title="Rich Maths Task Generator",
    page_icon="📐",
    layout="wide"
)

st.title("📐 Rich Maths Task Generator")
st.markdown("Generate contextualised, rich mathematics tasks aligned with Te Mātaiaho (NZ Curriculum).")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Task Parameters")

# 1. Select Phase
phase_options = list(CURRICULUM_DATA.keys())
selected_phase = st.sidebar.selectbox("Select Phase", phase_options)

# 2. Select Year Level (Filtered by Phase)
year_options = list(CURRICULUM_DATA[selected_phase].keys())
selected_year = st.sidebar.selectbox("Select Year Level", year_options)

# 3. Select Strand
strand_options = list(CURRICULUM_DATA[selected_phase][selected_year].keys())
selected_strand = st.sidebar.selectbox("Select Strand", strand_options)

# 4. Select Substrand / Learning Objectives (Optional Filtering)
substrand_options = list(CURRICULUM_DATA[selected_phase][selected_year][selected_strand].keys())
selected_substrand = st.sidebar.selectbox("Select Substrand", substrand_options)

# 5. Select Keywords (Mapped to Strand)
available_keywords = STRAND_KEYWORDS.get(selected_strand, [])
selected_keywords = st.sidebar.multiselect("Select Focus Keywords", available_keywords)

# 6. Select Context Theme
selected_theme = st.sidebar.selectbox("Select Context / Theme", NZ_THEMES)

if selected_theme == "Custom Context (Enter your own below)":
    custom_theme = st.sidebar.text_input("Enter Custom Context", "Local Community Garden")
    active_theme = custom_theme
else:
    active_theme = selected_theme

# Fixed quantity of generated tasks
NUM_TASKS = 3

# API Key Configuration
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# --- GENERATION LOGIC ---
if st.sidebar.button("✨ Generate Tasks", type="primary"):
    if not API_KEY:
        st.error("Gemini API key is missing. Please add `GEMINI_API_KEY` to your Streamlit secrets.")
    else:
        genai.configure(api_key=API_KEY)
        
        # Using gemini-3.5-flash as requested
        model = genai.GenerativeModel("gemini-3.5-flash")

        with st.spinner("Generating 3 rich learning tasks..."):
            try:
                # Construct prompt including Year Level, Substrand, and Keywords
                objectives = CURRICULUM_DATA[selected_phase][selected_year][selected_strand][selected_substrand]
                
                prompt = GET_PROMPT(selected_phase, selected_strand, active_theme, NUM_TASKS)
                prompt += f"\nSpecific Target: {selected_year}, Substrand: {selected_substrand}"
                prompt += f"\nAligned Objectives: {', '.join(objectives)}"
                if selected_keywords:
                    prompt += f"\nFocus Keywords: {', '.join(selected_keywords)}"
                
                # Force the 3 specific cultural contexts
                prompt += f"\n\nCRITICAL INSTRUCTION FOR THE 3 TASKS:"
                prompt += f"\n- Task 1 MUST use a Te Ao Māori context."
                prompt += f"\n- Task 2 MUST use a Pasifika context."
                prompt += f"\n- Task 3 MUST use a general NZ/Kiwi context."
                prompt += f"\nBlend these specific cultural contexts smoothly with the chosen theme: {active_theme}."

                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )

                data = json.loads(response.text)
                st.session_state["generated_tasks"] = data.get("tasks", [])
                st.success("Tasks generated successfully!")

            except Exception as e:
                st.error(f"Error generating tasks: {e}")

# --- DISPLAY OUTPUT ---
if "generated_tasks" in st.session_state and st.session_state["generated_tasks"]:
    st.subheader(f"Generated Tasks ({active_theme})")
    
    # Create the 3 specific tabs
    tab1, tab2, tab3 = st.tabs(["Option 1 (Te Ao Māori)", "Option 2 (Pasifika)", "Option 3 (NZ/Kiwi)"])
    tabs = [tab1, tab2, tab3]
    
    for idx, (tab, task) in enumerate(zip(tabs, st.session_state["generated_tasks"])):
        with tab:
            st.markdown(f"### {task.get('title', f'Maths Task {idx+1}')}")
            
            # Display ONLY Scenario, Teacher Notes, and Misconceptions on screen
            st.markdown(f"**Scenario:**\n{task.get('scenario')}")
            st.divider()
            st.markdown(f"**Teacher Notes:**\n{task.get('teacher_notes')}")
            st.markdown(f"**Common Misconceptions:**\n{task.get('misconceptions')}")
            st.divider()
            
            # Export Buttons
            col1, col2 = st.columns(2)
            
            with col1:
                # Generate PPT data using your specific function arguments
                ppt_data = generate_powerpoint_slide(
                    title=task.get('title', f'Maths Task {idx+1}'),
                    scenario=task.get('scenario', ''),
                    questions=task.get('questions', []),
                    extension=task.get('extension', ''),
                    phase=selected_phase,
                    theme=active_theme,
                    answers=task.get('answers', []),
                    teacher_notes=task.get('teacher_notes', ''),
                    misconceptions=task.get('misconceptions', '')
                )
                
                if ppt_data:
                    st.download_button(
                        label="📥 Download PowerPoint",
                        data=ppt_data,
                        file_name=f"Task_{idx+1}_Presentation.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        key=f"ppt_{idx}"
                    )
                else:
                    st.info("PowerPoint exporter not found/configured.")
                    
            with col2:
                # Generate PDF data using your specific function arguments
                pdf_data = generate_pdf_worksheet(
                    title=task.get('title', f'Maths Task {idx+1}'),
                    scenario=task.get('scenario', ''),
                    questions=task.get('questions', []),
                    extension=task.get('extension', ''),
                    phase=selected_phase,
                    theme=active_theme,
                    answers=task.get('answers', []),
                    teacher_notes=task.get('teacher_notes', ''),
                    misconceptions=task.get('misconceptions', '')
                )
                
                if pdf_data:
                    st.download_button(
                        label="📥 Download Worksheet (PDF)",
                        data=pdf_data,
                        file_name=f"Task_{idx+1}_Worksheet.pdf",
                        mime="application/pdf",
                        key=f"ws_{idx}"
                    )
                else:
                    st.info("Worksheet exporter not found/configured.")
