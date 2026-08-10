import io
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Optional pptx import for slide export
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False


# Register Font for Macrons in PDF
_font_registered = False
_registered_font_name = 'Helvetica'
_registered_bold_font_name = 'Helvetica-Bold'

def register_macron_font():
    global _font_registered, _registered_font_name, _registered_bold_font_name
    if _font_registered:
        return _registered_font_name, _registered_bold_font_name

    local_font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')

    font_paths = [
        local_font_path,
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf',
        '/Library/Fonts/DejaVuSans.ttf'
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('DejaVuSans', path))
                _registered_font_name = 'DejaVuSans'
                _registered_bold_font_name = 'DejaVuSans'
                _font_registered = True
                break
            except Exception:
                pass

    return _registered_font_name, _registered_bold_font_name


def generate_powerpoint_slide(title, scenario, questions, extension, phase, theme, answers=None, teacher_notes=None, misconceptions=None):
    """
    Generates a 3-slide PowerPoint presentation (.pptx):
      - Slide 1: Title, scenario (18pt), Question 1 (20pt).
      - Slide 2: Question 2+ (20pt) and Extension Challenge (20pt) with generous spacing.
      - Slide 3: Title, Teacher Notes & Misconceptions, and Answer Key & Solutions.
    """
    if not PPTX_AVAILABLE:
        raise ImportError("python-pptx is required for PowerPoint export.")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # --- SLIDE 1: Scenario & Question 1 ---
    slide1 = prs.slides.add_slide(blank_layout)

    # Title Box
    title_box1 = slide1.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.7))
    tf1 = title_box1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(30, 58, 138)

    # Scenario Box (18pt font)
    scen_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(2.0))
    tf_scen = scen_box.text_frame
    tf_scen.word_wrap = True
    p_scen = tf_scen.paragraphs[0]
    p_scen.text = f"Scenario: {scenario}"
    p_scen.font.size = Pt(18)
    p_scen.font.color.rgb = RGBColor(31, 41, 55)

    # Question 1 Box (20pt font)
    q1_box = slide1.shapes.add_textbox(Inches(0.8), Inches(3.6), Inches(11.7), Inches(3.2))
    tf_q1 = q1_box.text_frame
    tf_q1.word_wrap = True
    if questions:
        p_q1 = tf_q1.paragraphs[0]
        p_q1.text = f"1. {questions[0]}"
        p_q1.font.size = Pt(20)
        p_q1.font.color.rgb = RGBColor(30, 41, 59)

    # --- SLIDE 2: Question 2+ & Extension Challenge ---
    slide2 = prs.slides.add_slide(blank_layout)

    title_box2 = slide2.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.7))
    tf2 = title_box2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = f"{title} (Continued)"
    p2.font.size = Pt(24)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(30, 58, 138)

    q2_box = slide2.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.5))
    tf_q2 = q2_box.text_frame
    tf_q2.word_wrap = True

    remaining_qs = questions[1:] if len(questions) > 1 else []
    first_item = True

    for idx, q in enumerate(remaining_qs, 2):
        p_q = tf_q2.paragraphs[0] if first_item else tf_q2.add_paragraph()
        first_item = False
        p_q.text = f"{idx}. {q}"
        p_q.font.size = Pt(20)
        p_q.space_after = Pt(40)  # Generous gap after Question 2

    if extension:
        p_ext = tf_q2.paragraphs[0] if first_item else tf_q2.add_paragraph()
        p_ext.text = f"Extension Challenge:\n{extension}"
        p_ext.font.size = Pt(20)
        p_ext.font.bold = True
        p_ext.font.color.rgb = RGBColor(180, 83, 9)
        p_ext.space_before = Pt(30)  # Generous gap above Extension Challenge

    # --- SLIDE 3: Teacher Solutions & Guidance ---
    slide_3 = prs.slides.add_slide(blank_slide_layout)

    title_box_3 = slide_3.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.0))
    tf_title_3 = title_box_3.text_frame
    tf_title_3.word_wrap = True
    p_title_3 = tf_title_3.paragraphs[0]
    p_title_3.text = f"Solutions & Teacher Guidance: {title}"
    p_title_3.font.size = Pt(24)
    p_title_3.font.bold = True
    p_title_3.font.color.rgb = RGBColor(27, 54, 93)

    ans_box = slide_3.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))
    tf_ans = ans_box.text_frame
    tf_ans.word_wrap = True

    for idx, ans_text in enumerate(answers, 1):
        p_ans = tf_ans.add_paragraph() if idx > 1 else tf_ans.paragraphs[0]
        if idx <= len(questions):
            label = f"Question {idx} Solution:"
        else:
            label = "Extension Challenge Guidance & Sample Solutions (Open-Ended):"
            
        p_ans.text = f"• {label}\n  {ans_text}"
        p_ans.font.size = Pt(13)
        p_ans.space_after = Pt(10)

    # Teacher Notes & Misconceptions Box (under title)
    if teacher_notes or misconceptions:
        notes_box = slide3.shapes.add_textbox(Inches(0.8), Inches(current_top), Inches(11.7), Inches(1.8))
        tf_notes = notes_box.text_frame
        tf_notes.word_wrap = True
        p_notes_first = True

        if teacher_notes:
            p_tn = tf_notes.paragraphs[0] if p_notes_first else tf_notes.add_paragraph()
            p_notes_first = False
            p_tn.text = f"Teacher Notes: {teacher_notes}"
            p_tn.font.size = Pt(14)
            p_tn.font.italic = True
            p_tn.font.color.rgb = RGBColor(75, 85, 99)
            p_tn.space_after = Pt(10)

        if misconceptions:
            p_mc = tf_notes.paragraphs[0] if p_notes_first else tf_notes.add_paragraph()
            p_mc.text = f"Common Misconceptions: {misconceptions}"
            p_mc.font.size = Pt(14)
            p_mc.font.italic = True
            p_mc.font.color.rgb = RGBColor(185, 28, 28)
            p_mc.space_after = Pt(15)

        current_top += 1.8

    # Solutions Box
    if answers:
        ans_box = slide3.shapes.add_textbox(Inches(0.8), Inches(current_top), Inches(11.7), Inches(7.0 - current_top))
        tf_ans = ans_box.text_frame
        tf_ans.word_wrap = True

        p_hdr = tf_ans.paragraphs[0]
        p_hdr.text = "Answer Key & Solutions:"
        p_hdr.font.size = Pt(18)
        p_hdr.font.bold = True
        p_hdr.font.color.rgb = RGBColor(30, 58, 138)
        p_hdr.space_after = Pt(10)

        if isinstance(answers, list):
            for idx, ans in enumerate(answers, 1):
                p_a = tf_ans.add_paragraph()
                p_a.text = f"Q{idx} Solution: {ans}"
                p_a.font.size = Pt(16)
                p_a.space_after = Pt(14)
        else:
            p_a = tf_ans.add_paragraph()
            p_a.text = str(answers)
            p_a.font.size = Pt(16)
            p_a.space_after = Pt(14)

    buffer = io.BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def generate_pdf_worksheet(title, scenario, questions, extension, phase, theme, answers=None, teacher_notes=None, misconceptions=None):
    """
    Generates a 2-page PDF Worksheet using ReportLab:
      - Page 1: Student Worksheet (Title, Scenario, Questions, Extension Challenge).
      - Page 2: Teacher Guide (Title, Teacher Notes & Misconceptions, Answer Key & Solutions).
    """
    font_name, bold_font_name = register_macron_font()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName=bold_font_name,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName=bold_font_name,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=10
    )

    note_style = ParagraphStyle(
        'TeacherNote',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8
    )

    misconception_style = ParagraphStyle(
        'MisconceptionText',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#991B1B'),
        spaceAfter=12
    )

    story = []

    # --- PAGE 1: Student Worksheet ---
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"<b>Scenario:</b> {scenario}", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Questions:</b>", section_heading))
    for idx, q in enumerate(questions, 1):
        story.append(Paragraph(f"<b>{idx}.</b> {q}", body_style))
        story.append(Spacer(1, 8))

    if extension:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Extension Challenge:</b>", section_heading))
        story.append(Paragraph(extension, body_style))

    # --- PAGE 2: Teacher Guide & Solutions ---
    story.append(PageBreak())

    story.append(Paragraph(f"{title} — Teacher Notes & Solutions", title_style))

    # Teacher Notes & Misconceptions directly under Page 2 Title
    if teacher_notes:
        story.append(Paragraph(f"<b>Teacher Notes:</b> {teacher_notes}", note_style))

    if misconceptions:
        story.append(Paragraph(f"<b>Common Misconceptions:</b> {misconceptions}", misconception_style))

    if teacher_notes or misconceptions:
        story.append(Spacer(1, 10))

    if answers:
        story.append(Paragraph("<b>Answer Key & Solutions:</b>", section_heading))
        if isinstance(answers, list):
            for idx, ans in enumerate(answers, 1):
                story.append(Paragraph(f"<b>Q{idx}:</b> {ans}", body_style))
        else:
            story.append(Paragraph(str(answers), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
