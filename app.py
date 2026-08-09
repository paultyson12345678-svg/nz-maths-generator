import streamlit as st
import json
import io
import google.generativeai as genai
from curriculum import CURRICULUM_CONTEXT, GET_PROMPT
from exporters import generate_powerpoint_slide, generate_pdf_worksheet

# Streamlit Page Config
st.set_page_config(
    page_title="NZ Maths Task Generator",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 NZ Curriculum Maths Task Generator")
st.markdown("Generate rich, contextualised mathematics tasks aligned with the NZ Curriculum.")

# Sidebar Controls
st.sidebar.header("Task Parameters")

phase = st.sidebar.selectbox(
    "Curriculum Phase",
    ["Phase 1 (Years 1-3)", "Phase 2 (Years 4-6)", "Phase 3 (Years 7-8)", "Phase 4 (Years 9-10)"]
)

strand = st.sidebar.selectbox(
    "Strand",
    ["Number", "Algebra", "Measurement", "Geometry", "Statistics", "Probability"]
)

theme = st.sidebar.text_input("Context / Theme", value="Sports Day / Whānau Event")

num_tasks = st.sidebar.slider("Number of Tasks to Generate", min_value=1, max_value=5, value=1)

api_key = st.sidebar.text_input("Gemini API Key", type="password")

if not api_key:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]

generate_btn = st.sidebar.button("Generate Tasks", type="primary")


def call_gemini_api(api_key, prompt):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return response.text


if generate_btn:
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar or set it in Streamlit secrets.")
    else:
        with st.spinner("Generating NZ Curriculum aligned maths tasks..."):
            try:
                prompt = GET_PROMPT(phase, strand, theme, num_tasks)
                response_text = call_gemini_api(api_key, prompt)
                tasks_data = json.loads(response_text)
                st.session_state['tasks_data'] = tasks_data
                st.session_state['params'] = {
                    'phase': phase,
                    'strand': strand,
                    'theme': theme
                }
                st.success("Tasks generated successfully!")
            except Exception as e:
                st.error(f"Error generating tasks: {str(e)}")

if 'tasks_data' in st.session_state and st.session_state['tasks_data']:
    tasks_data = st.session_state['tasks_data']
    params = st.session_state.get('params', {})

    tasks = tasks_data.get('tasks', [])

    tabs = st.tabs([f"Task {i+1}: {t.get('title', 'Untitled')}" for i, t in enumerate(tasks)])

    for i, (tab, task) in enumerate(zip(tabs, tasks)):
        with tab:
            st.header(task.get('title', f'Task {i+1}'))
            st.markdown(f"**Scenario:**\n{task.get('scenario', '')}")

            st.subheader("Questions")
            questions = task.get('questions', [])
            for q_idx, q in enumerate(questions, 1):
                st.markdown(f"**{q_idx}.** {q}")

            if task.get('extension'):
                st.subheader("Extension Challenge")
                st.info(task.get('extension'))

            with st.expander("💡 Teacher Notes & Misconceptions"):
                if task.get('teacher_notes'):
                    st.markdown(f"**Teacher Notes:** {task.get('teacher_notes')}")
                if task.get('misconceptions'):
                    st.markdown(
                        f"""
                        <div style="background-color: #2c3e50; padding: 15px; border-radius: 8px;">
                            <p style="color: white; margin: 0;"><b>🚨 Common Misconceptions:</b><br>{task.get('misconceptions')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                if not task.get('teacher_notes') and not task.get('misconceptions'):
                    st.write("No specific notes or misconceptions identified for this task.")

            with st.expander("🔑 Answer Key & Solutions"):
                answers = task.get('answers', [])
                if isinstance(answers, list):
                    for a_idx, ans in enumerate(answers, 1):
                        st.markdown(f"**Q{a_idx}:** {ans}")
                else:
                    st.write(answers)

            st.divider()

            # Export Buttons side-by-side inside the tab
            col1, col2 = st.columns(2)

            with col1:
                spaced_answers = [ans + "\n\n" for ans in task.get('answers', [])]
                pptx_data = generate_powerpoint_slide(
                    title=task.get('title', ''),
                    scenario=task.get('scenario', ''),
                    questions=task.get('questions', []),
                    extension=task.get('extension', ''),
                    phase=params.get('phase', ''),
                    theme=params.get('theme', ''),
                    answers=spaced_answers,
                    teacher_notes=task.get('teacher_notes', ''),
                    misconceptions=task.get('misconceptions', '')
                )

                st.download_button(
                    label="📊 Download for Google Slides / PPTX",
                    help="Download this file and drag it into your Google Drive or PowerPoint.",
                    data=pptx_data,
                    file_name=f"{task.get('title', 'Task').replace(' ', '_')}_Presentation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    key=f"pptx_{i}",
                    use_container_width=True
                )

            with col2:
                pdf_data = generate_pdf_worksheet(
                    title=task.get('title', ''),
                    scenario=task.get('scenario', ''),
                    questions=task.get('questions', []),
                    extension=task.get('extension', ''),
                    phase=params.get('phase', ''),
                    theme=params.get('theme', ''),
                    answers=task.get('answers', []),
                    teacher_notes=task.get('teacher_notes', ''),
                    misconceptions=task.get('misconceptions', '')
                )

                st.download_button(
                    label="📄 Download PDF Worksheet",
                    help="Download printable 2-page PDF worksheet with teacher key.",
                    data=pdf_data,
                    file_name=f"{task.get('title', 'Task').replace(' ', '_')}_Worksheet.pdf",
                    mime="application/pdf",
                    key=f"pdf_{i}",
                    use_container_width=True
                )
