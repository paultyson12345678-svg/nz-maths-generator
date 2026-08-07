import io
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def get_macron_font():
    """
    Registers the DejaVuSans TTF font uploaded to the repository
    to ensure proper rendering of Māori macrons (ā, ē, ī, ō, ū).
    """
    font_name = 'DejaVuSans'
    font_bold_name = 'DejaVuSans-Bold'
    font_path = "DejaVuSans.ttf"  # Local file in repository root

    # Check if font is already registered in ReportLab
    if 'DejaVuSans' in pdfmetrics.getRegisteredFontNames():
        return font_name, font_name

    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
            return font_name, font_name
        except Exception as e:
            print(f"Error registering local font: {e}")

    # Fallback to standard Helvetica if local file isn't found
    return 'Helvetica', 'Helvetica-Bold'


def generate_powerpoint_slide(title, scenario, questions, extension, phase, theme, answers):
    """
    Generates a 16:9 widescreen PowerPoint presentation (.pptx) containing two slides:
    Slide 1: Student Task Card
    Slide 2: Teacher Answers & Solutions
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # --- SLIDE 1: STUDENT TASK ---
    slide1 = prs.slides.add_slide(blank_slide_layout)

    # Header Box
    header_box = slide1.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.0))
    tf_header = header_box.text_frame
    tf_header.word_wrap = True
    
    p_phase = tf_header.paragraphs[0]
    p_phase.text = f"AOTEAROA RICH MATHS TASK • {phase.upper()} • {theme.upper()}"
    p_phase.font.size = Pt(12)
    p_phase.font.bold = True
    p_phase.font.color.rgb = RGBColor(0, 102, 204)

    p_title = tf_header.add_paragraph()
    p_title.text = title
    p_title.font.size = Pt(28)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(30, 30, 30)

    # Scenario Box
    scenario_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(1.5))
    tf_scenario = scenario_box.text_frame
    tf_scenario.word_wrap = True
    
    p_scen_hdr = tf_scenario.paragraphs[0]
    p_scen_hdr.text = "Context & Scenario:"
    p_scen_hdr.font.size = Pt(14)
    p_scen_hdr.font.bold = True
    p_scen_hdr.font.color.rgb = RGBColor(70, 70, 70)

    p_scen_txt = tf_scenario.add_paragraph()
    p_scen_txt.text = scenario
    p_scen_txt.font.size = Pt(14)
    p_scen_txt.font.color.rgb = RGBColor(50, 50, 50)

    # Questions Box
    q_box = slide1.shapes.add_textbox(Inches(0.8), Inches(3.3), Inches(11.733), Inches(3.6))
    tf_q = q_box.text_frame
    tf_q.word_wrap = True

    for q_idx, q_text in enumerate(questions):
        p_q = tf_q.add_paragraph() if q_idx > 0 or len(tf_q.paragraphs[0].text) > 0 else tf_q.paragraphs[0]
        p_q.text = f"Question {q_idx + 1}: {q_text}"
        p_q.font.size = Pt(16)
        p_q.font.bold = True
        p_q.font.color.rgb = RGBColor(20, 20, 20)

    if extension:
        p_ext = tf_q.add_paragraph()
        p_ext.text = f"Extension Challenge: {extension}"
        p_ext.font.size = Pt(15)
        p_ext.font.bold = True
        p_ext.font.color.rgb = RGBColor(180, 50, 50)

    # --- SLIDE 2: TEACHER SOLUTIONS ---
    slide2 = prs.slides.add_slide(blank_slide_layout)

    header_box2 = slide2.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.0))
    tf_header2 = header_box2.text_frame
    tf_header2.word_wrap = True

    p_title2 = tf_header2.paragraphs[0]
    p_title2.text = f"Teacher Solutions: {title}"
    p_title2.font.size = Pt(26)
    p_title2.font.bold = True
    p_title2.font.color.rgb = RGBColor(0, 102, 204)

    ans_box = slide2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tf_ans = ans_box.text_frame
    tf_ans.word_wrap = True

    if answers:
        for a_idx, a_text in enumerate(answers):
            p_a = tf_ans.add_paragraph() if a_idx > 0 or len(tf_ans.paragraphs[0].text) > 0 else tf_ans.paragraphs[0]
            label = f"Q{a_idx + 1} Solution:" if a_idx < len(questions) else "Extension Solution:"
            p_a.text = f"{label} {a_text}"
            p_a.font.size = Pt(14)
            p_a.font.color.rgb = RGBColor(40, 40, 40)

    pptx_io = io.BytesIO()
    prs.save(pptx_io)
    pptx_io.seek(0)
    return pptx_io


def generate_task_pdf(title, scenario, questions, extension, phase, theme, answers):
    """
    Generates a PDF worksheet containing both the student task section
    and teacher notes/solutions, formatted with macron-supporting fonts.
    """
    font_name, font_bold_name = get_macron_font()

    pdf_io = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_io,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    style_header = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName=font_bold_name,
        fontSize=10,
        textColor=colors.HexColor('#0066CC'),
        spaceAfter=4
    )

    style_title = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=font_bold_name,
        fontSize=20,
        textColor=colors.HexColor('#1E1E1E'),
        spaceAfter=12
    )

    style_section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName=font_bold_name,
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )

    style_body = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#222222'),
        spaceAfter=10
    )

    style_extension = ParagraphStyle(
        'ExtensionStyle',
        parent=styles['Normal'],
        fontName=font_bold_name,
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#B43232'),
        spaceAfter=10
    )

    style_teacher_hdr = ParagraphStyle(
        'TeacherHeader',
        parent=styles['Heading2'],
        fontName=font_bold_name,
        fontSize=14,
        textColor=colors.HexColor('#0066CC'),
        spaceAfter=8,
        spaceBefore=14
    )

    elements = []

    # Student Task Header
    elements.append(Paragraph(f"AOTEAROA RICH MATHS TASK • {phase.upper()} • {theme.upper()}", style_header))
    elements.append(Paragraph(title, style_title))
    elements.append(Spacer(1, 4))

    # Scenario
    elements.append(Paragraph("<b>Context & Scenario:</b>", style_section_heading))
    elements.append(Paragraph(scenario, style_body))
    elements.append(Spacer(1, 8))

    # Questions
    elements.append(Paragraph("<b>Task Questions:</b>", style_section_heading))
    for q_idx, q_text in enumerate(questions):
        elements.append(Paragraph(f"<b>Question {q_idx + 1}:</b> {q_text}", style_body))

    if extension:
        elements.append(Paragraph(f"<b>Extension Challenge:</b> {extension}", style_extension))

    elements.append(Spacer(1, 14))

    # Teacher Notes & Solutions
    if answers:
        elements.append(Paragraph("Teacher Notes & Solutions", style_teacher_hdr))
        for a_idx, a_text in enumerate(answers):
            label = f"Q{a_idx + 1} Solution:" if a_idx < len(questions) else "Extension Solution:"
            elements.append(Paragraph(f"<b>{label}</b> {a_text}", style_body))

    doc.build(elements)
    pdf_io.seek(0)
    return pdf_io
