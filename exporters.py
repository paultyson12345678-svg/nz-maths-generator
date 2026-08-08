import io
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
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
    font_path = "DejaVuSans.ttf"  # Local file in repository root

    if 'DejaVuSans' in pdfmetrics.getRegisteredFontNames():
        return font_name, font_name

    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
            return font_name, font_name
        except Exception as e:
            print(f"Error registering local font: {e}")

    return 'Helvetica', 'Helvetica-Bold'


def generate_powerpoint_slide(title, scenario, questions, extension, phase, theme, answers):
    """
    Generates a 16:9 widescreen PowerPoint presentation (.pptx) containing 3 slides:
    Slide 1: Title, Scenario (larger text), and Question 1
    Slide 2: Question 2 and Extension Challenge
    Slide 3: Teacher Answers & Solutions
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # --- SLIDE 1: SCENARIO & QUESTION 1 ---
    slide1 = prs.slides.add_slide(blank_slide_layout)

    # Header Box
    header_box = slide1.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.9))
    tf_header = header_box.text_frame
    tf_header.word_wrap = True
    
    p_phase = tf_header.paragraphs[0]
    p_phase.text = f"AOTEAROA RICH MATHS TASK • {phase.upper()} • {theme.upper()}"
    p_phase.font.size = Pt(12)
    p_phase.font.bold = True
    p_phase.font.color.rgb = RGBColor(0, 102, 204)

    p_title = tf_header.add_paragraph()
    p_title.text = title
    p_title.font.size = Pt(26)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(30, 30, 30)

    # Scenario Box (Larger Text)
    scenario_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.733), Inches(2.2))
    tf_scenario = scenario_box.text_frame
    tf_scenario.word_wrap = True
    
    p_scen_hdr = tf_scenario.paragraphs[0]
    p_scen_hdr.text = "Context & Scenario:"
    p_scen_hdr.font.size = Pt(16)
    p_scen_hdr.font.bold = True
    p_scen_hdr.font.color.rgb = RGBColor(70, 70, 70)

    p_scen_txt = tf_scenario.add_paragraph()
    p_scen_txt.text = scenario
    p_scen_txt.font.size = Pt(16)  # Increased font size
    p_scen_txt.font.color.rgb = RGBColor(40, 40, 40)

    # Question 1 Box
    q1_box = slide1.shapes.add_textbox(Inches(0.8), Inches(4.0), Inches(11.733), Inches(2.8))
    tf_q1 = q1_box.text_frame
    tf_q1.word_wrap = True

    p_q1_hdr = tf_q1.paragraphs[0]
    p_q1_hdr.text = "Question 1:"
    p_q1_hdr.font.size = Pt(18)
    p_q1_hdr.font.bold = True
    p_q1_hdr.font.color.rgb = RGBColor(0, 102, 204)

    p_q1_txt = tf_q1.add_paragraph()
    q1_text = questions[0] if len(questions) > 0 else ""
    p_q1_txt.text = q1_text
    p_q1_txt.font.size = Pt(16)
    p_q1_txt.font.color.rgb = RGBColor(20, 20, 20)

    # --- SLIDE 2: QUESTION 2 & EXTENSION ---
    slide2 = prs.slides.add_slide(blank_slide_layout)

    header_box2 = slide2.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.8))
    tf_header2 = header_box2.text_frame
    tf_header2.word_wrap = True

    p_title2 = tf_header2.paragraphs[0]
    p_title2.text = f"{title} (Continued)"
    p_title2.font.size = Pt(24)
    p_title2.font.bold = True
    p_title2.font.color.rgb = RGBColor(30, 30, 30)

    # Question 2 Box
    q2_box = slide2.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.733), Inches(2.5))
    tf_q2 = q2_box.text_frame
    tf_q2.word_wrap = True

    p_q2_hdr = tf_q2.paragraphs[0]
    p_q2_hdr.text = "Question 2:"
    p_q2_hdr.font.size = Pt(18)
    p_q2_hdr.font.bold = True
    p_q2_hdr.font.color.rgb = RGBColor(0, 102, 204)

    p_q2_txt = tf_q2.add_paragraph()
    q2_text = questions[1] if len(questions) > 1 else ""
    p_q2_txt.text = q2_text
    p_q2_txt.font.size = Pt(16)
    p_q2_txt.font.color.rgb = RGBColor(20, 20, 20)

    # Extension Challenge Box
    if extension:
        ext_box = slide2.shapes.add_textbox(Inches(0.8), Inches(4.2), Inches(11.733), Inches(2.5))
        tf_ext = ext_box.text_frame
        tf_ext.word_wrap = True

        p_ext_hdr = tf_ext.paragraphs[0]
        p_ext_hdr.text = "Extension Challenge:"
        p_ext_hdr.font.size = Pt(18)
        p_ext_hdr.font.bold = True
        p_ext_hdr.font.color.rgb = RGBColor(180, 50, 50)

        p_ext_txt = tf_ext.add_paragraph()
        p_ext_txt.text = extension
        p_ext_txt.font.size = Pt(16)
        p_ext_txt.font.color.rgb = RGBColor(30, 30, 30)

    # --- SLIDE 3: TEACHER SOLUTIONS ---
    slide3 = prs.slides.add_slide(blank_slide_layout)

    header_box3 = slide3.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.0))
    tf_header3 = header_box3.text_frame
    tf_header3.word_wrap = True

    p_title3 = tf_header3.paragraphs[0]
    p_title3.text = f"Teacher Solutions: {title}"
    p_title3.font.size = Pt(26)
    p_title3.font.bold = True
    p_title3.font.color.rgb = RGBColor(0, 102, 204)

    ans_box = slide3.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
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
    Generates a 2-page PDF worksheet:
    Page 1: Student Task with generous workout spaces & answer lines.
    Page 2: Teacher Notes & Solutions.
    """
    font_name, font_bold_name = get_macron_font()

    pdf_io = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_io,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    style_header = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName=font_bold_name,
        fontSize=9.5,
        textColor=colors.HexColor('#0066CC'),
        spaceAfter=2
    )

    style_title = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=font_bold_name,
        fontSize=18,
        textColor=colors.HexColor('#1E1E1E'),
        spaceAfter=8
    )

    style_section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName=font_bold_name,
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4
    )

    style_body = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor('#222222'),
        spaceAfter=4
    )

    style_lines = ParagraphStyle(
        'LinesStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=18,
        textColor=colors.HexColor('#A0A0A0')
    )

    style_extension = ParagraphStyle(
        'ExtensionStyle',
        parent=styles['Normal'],
        fontName=font_bold_name,
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor('#B43232'),
        spaceAfter=4
    )

    style_teacher_hdr = ParagraphStyle(
        'TeacherHeader',
        parent=styles['Heading2'],
        fontName=font_bold_name,
        fontSize=16,
        textColor=colors.HexColor('#0066CC'),
        spaceAfter=10
    )

    elements = []

    # --- PAGE 1: STUDENT TASK CARD ---
    elements.append(Paragraph(f"AOTEAROA RICH MATHS TASK • {phase.upper()} • {theme.upper()}", style_header))
    elements.append(Paragraph(title, style_title))

    # Scenario
    elements.append(Paragraph("<b>Context & Scenario:</b>", style_section_heading))
    elements.append(Paragraph(scenario, style_body))
    elements.append(Spacer(1, 8))

    # Questions with Working Spaces
    elements.append(Paragraph("<b>Task Questions:</b>", style_section_heading))
    
    dotted_line = ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . ."

    for q_idx, q_text in enumerate(questions):
        elements.append(Paragraph(f"<b>Question {q_idx + 1}:</b> {q_text}", style_body))
        # Add workout room and answer lines
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"<i>Working / Answer:</i><br/>{dotted_line}<br/>{dotted_line}", style_lines))
        elements.append(Spacer(1, 10))

    if extension:
        elements.append(Paragraph(f"<b>Extension Challenge:</b> {extension}", style_extension))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"<i>Working / Answer:</i><br/>{dotted_line}<br/>{dotted_line}", style_lines))

    # --- PAGE 2: TEACHER NOTES & SOLUTIONS ---
    elements.append(PageBreak())  # Guarantees answers are strictly on Page 2

    if answers:
        elements.append(Paragraph("Teacher Notes & Solutions", style_teacher_hdr))
        elements.append(Spacer(1, 6))
        for a_idx, a_text in enumerate(answers):
            label = f"Q{a_idx + 1} Solution:" if a_idx < len(questions) else "Extension Solution:"
            elements.append(Paragraph(f"<b>{label}</b>", style_section_heading))
            elements.append(Paragraph(a_text, style_body))
            elements.append(Spacer(1, 8))

    doc.build(elements)
    pdf_io.seek(0)
    return pdf_io
