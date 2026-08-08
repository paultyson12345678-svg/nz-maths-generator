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
    
    # --- STRAND KEYWORDS MULTI-SELECT DROPDOWN ---
    available_keywords = STRAND_KEYWORDS.get(strand, [])
    if available_keywords:
        selected_keywords = st.sidebar.multiselect(
            "Select Strand Keywords / Concepts",
            options=available_keywords,
            default=available_keywords  # Pre-selects all by default; users can remove or pick specific ones
        )
    else:
        selected_keywords = []
else:
    st.sidebar.warning(f"No strands configured for {year_level} yet.")
    strand = None
    available_skills = []
    selected_keywords = []

# 4. Specific Skill / Objective Selection
if available_skills:
    selected_skill = st.sidebar.selectbox("Select Learning Focus / Skill", available_skills)
else:
    selected_skill = st.sidebar.text_input("Custom Learning Focus", "Solving real-world problems")

# 5. Theme / Context
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
            6. Include clear solutions and teacher guidance notes for all questions.
            7. Include a section identifying common student misconceptions for the task and how teachers can proactively address them.
            8. Ensure tone is supportive, culturally responsive, and mathematically sound.
            9. CRITICAL: Do NOT use any unescaped double quotes (") inside your text strings. Use single quotes (') instead to prevent JSON parsing errors.

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
                # Clean up the response text to remove any accidental markdown blocks
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:-3].strip()
                elif raw_text.startswith("
