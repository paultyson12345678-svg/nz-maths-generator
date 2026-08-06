import streamlit as st
import random
import os
import io

from curriculum import CURRICULUM_DATA, NZ_THEMES
from exporters import generate_powerpoint_slide, generate_task_pdf, generate_task_card_image

st.set_page_config(page_title="NZ Primary Maths Task Generator", page_icon="🇳🇿", layout="wide")

st.title("🇳🇿 New Zealand Primary Maths Task Generator")
st.markdown("Generate rich, context-aligned rich mathematical tasks for Phase 1 to Phase 3 (Years 1–8).")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("Task Settings")

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
    selected_skill = st.sidebar.text_input("Custom Learning Focus", "Solving real-world problem")

# 5. Theme / Context
selected_theme = st.sidebar.selectbox("Select Cultural / NZ Context", NZ_THEMES)
if selected_theme == "Custom Context (Enter your own below)":
    custom_theme = st.sidebar.text_input("Enter Custom Theme", "School Gala")
    active_theme = custom_theme if custom_theme else "School Gala"
else:
    active_theme = selected_theme

# --- TASK GENERATOR DISPLAY ---
st.header("Generated Learning Task")

col1, col2 = st.columns([2, 1])

with col1:
    task_title = st.text_input("Task Title", f"{active_theme}: {selected_skill if selected_skill else 'Maths Challenge'}")
    scenario_text = st.text_area(
        "Context & Scenario",
        f"At the {active_theme}, students are exploring concepts related to {selected_skill.lower() if selected_skill else 'maths'}. "
        f"They need to work together to solve challenges using their problem-solving strategies.",
        height=100
    )

    q1_input = st.text_area("Question 1 (Main Task)", "How many total items were used, and how did you work it out?", height=70)
    q2_input = st.text_area("Question 2 (Follow-up)", "If the quantity doubled, what would the new total be?", height=70)
    ext_input = st.text_area("Extension Challenge", "Can you write a rule or pattern to explain your findings to another group?", height=70)

with col2:
    st.subheader("Teacher Notes & Guidance")
    ans1_input = st.text_area("Question 1 Solution & Tip", "Encourage students to use visual representations or place value blocks.", height=80)
    ans2_input = st.text_area("Question 2 Solution & Tip", "Look for multiplicative thinking vs repeated addition.", height=80)

questions_list = [q1_input, q2_input]
answers_list = [ans1_input, ans2_input]

st.markdown("---")
st.subheader("📥 Export & Download Deliverables")

exp_col1, exp_col2, exp_col3 = st.columns(3)

# PPTX Export
with exp_col1:
    try:
        pptx_data = generate_powerpoint_slide(
            title=task_title,
            scenario=scenario_text,
            questions=questions_list,
            extension=ext_input,
            phase=phase,
            theme=active_theme,
            answers=answers_list
        )
        st.download_button(
            label="📊 Download PowerPoint (.pptx)",
            data=pptx_data,
            file_name=f"{task_title.replace(' ', '_')}.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
    except Exception as e:
        st.error(f"Error generating PowerPoint: {e}")

# PDF Export
with exp_col2:
    try:
        pdf_data = generate_task_pdf(
            title=task_title,
            scenario=scenario_text,
            questions=questions_list,
            extension=ext_input,
            phase=phase,
            theme=active_theme,
            answers=answers_list
        )
        st.download_button(
            label="📄 Download Worksheet (.pdf)",
            data=pdf_data,
            file_name=f"{task_title.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")

# Task Card PNG Export
with exp_col3:
    try:
        card_data = generate_task_card_image(
            title=task_title,
            scenario=scenario_text,
            questions=questions_list,
            extension=ext_input
        )
        st.download_button(
            label="🖼️ Download Task Card (.png)",
            data=card_data,
            file_name=f"{task_title.replace(' ', '_')}.png",
            mime="image/png"
        )
    except Exception as e:
        st.error(f"Error generating Task Card: {e}")
