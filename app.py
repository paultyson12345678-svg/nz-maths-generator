import streamlit as st
import json
import google.generativeai as genai
from curriculum import NZ_THEMES, CURRICULUM_DATA, STRAND_KEYWORDS, GET_PROMPT

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

# API Key Configuration (Uses Streamlit Secrets or Environment Variable)
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# --- GENERATION LOGIC ---
if st.sidebar.button("✨ Generate Tasks", type="primary"):
    if not API_KEY:
        st.error("Gemini API key is missing. Please add `GEMINI_API_KEY` to your Streamlit secrets.")
    else:
        genai.configure(api_key=API_KEY)
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
    
    for idx, task in enumerate(st.session_state["generated_tasks"], start=1):
        with st.expander(f"Task {idx}: {task.get('title', 'Maths Task')}", expanded=True):
            st.markdown(f"**Scenario:**\n{task.get('scenario')}")
            
            st.markdown("**Questions:**")
            for q in task.get("questions", []):
                st.markdown(f"- {q}")
            
            if task.get("extension"):
                st.markdown(f"**Extension Challenge:**\n{task.get('extension')}")
            
            st.divider()
            st.markdown(f"**Teacher Notes:** {task.get('teacher_notes')}")
            st.markdown(f"**Common Misconceptions:** {task.get('misconceptions')}")
            
            st.markdown("**Solutions:**")
            for ans in task.get("answers", []):
                st.markdown(f"- {ans}")
