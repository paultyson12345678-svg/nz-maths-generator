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


# --- FONT REGISTRATION ---
_font_registered = False
_registered_font_name = 'Helvetica'
_registered_bold_font_name = 'Helvetica-Bold'

def get_macron_font():
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


# --- POWERPOINT GENERATOR ---
def generate_powerpoint_slide(title, scenario, questions, extension, phase, theme, answers=None, teacher_notes=None, misconceptions=None):
    """
    Generates a PowerPoint presentation (.pptx) with the math task.
    """
    if not PPTX_AVAILABLE:
        return None

    prs = Presentation()
    
    # Use widescreen (16:9) aspect ratio
    prs.slide_width = Inches(14.333)
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

    # Scenario Box
    scen_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(2.0))
    tf_scen = scen_box.text_frame
    tf_scen.word_wrap = True
    p_scen = tf_scen.paragraphs[0]
    p_scen.text = f"Scenario: {scenario}"
    p_scen.font.size = Pt(20)
    p_scen.font.bold = True
    p_scen.font.color.rgb = RGBColor(31, 41, 55)

    # Question 1 Box
    q1_box = slide1.shapes.add_textbox(Inches(0.8), Inches(3.6), Inches(11.7), Inches(3.2))
    tf_q1 = q1_box.text_frame
    tf_q1.word_wrap = True
    if questions:
        p_q1 = tf_q1.paragraphs[0]
        p_q1.text = f"1. {questions[0]}"
        p_q1.font.size = Pt(18)
        p_q1.font.color.rgb = RGBColor(30, 41, 59)

    # --- SLIDE 2: Question 2+ & Extension Challenge ---
    slide2 = prs.slides.add_slide(blank_layout)

    title_box2 = slide2.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.7))
    tf2 = title_box2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = f"{title} (Continued)"
    p2.font.size = Pt(20)
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
        p_q.font.size = Pt(18)
        p_q.space_after = Pt(60) 

    if extension:
        p_ext = tf_q2.paragraphs[0] if first_item else tf_q2.add_paragraph()
        p_ext.text = f"Extension Challenge:\n{extension}"
        p_ext.font.size = Pt(18)
        p_ext.font.bold = True
        p_ext.font.color.rgb = RGBColor(180, 83, 9)
        p_ext.space_before = Pt(40) # Doubled gap before the extension challenge

    # --- SLIDE 3: MISCONCEPTIONS, SOLUTIONS & TEACHER NOTES ---
    if answers or misconceptions or teacher_notes:
        slide_layout_answers = prs.slide_layouts[1]  # Title and Content layout
        slide_answers = prs.slides.add_slide(slide_layout_answers)
        
        # Style Title to match Slide 1 & 2
        title_shape_answers = slide_answers.shapes.title
        title_shape_answers.text = f"Solutions & Notes: {title}"
        title_p = title_shape_answers.text_frame.paragraphs[0]
        title_p.font.size = Pt(24)
        title_p.font.bold = True
        title_p.font.color.rgb = RGBColor(30, 58, 138)
        
        body_shape_answers = slide_answers.placeholders[1]
        tf_answers = body_shape_answers.text_frame
        tf_answers.word_wrap = True
        tf_answers.clear() 
        
        # 1. Misconceptions first
        if misconceptions:
            p_mc_title = tf_answers.add_paragraph()
            p_mc_title.text = "Common Misconceptions:"
            p_mc_title.font.bold = True
            p_mc_title.font.size = Pt(16)
            
            p_mc = tf_answers.add_paragraph()
            p_mc.text = str(misconceptions)
            p_mc.font.size = Pt(14)
            p_mc.space_after = Pt(16)
            
        # 2. Solutions & Teacher Notes next
        if answers:
            if isinstance(answers, list):
                for i, ans in enumerate(answers):
                    p = tf_answers.add_paragraph()
                    
                    # If this is the final answer, label it as Extension & attach teacher notes
                    if i == len(answers) - 1:
                        combo_text = f"Extension Solution & Teacher guidance:\n{ans}"
                        if teacher_notes:
                            combo_text += f"\n{teacher_notes}"
                        p.text = combo_text
                    else:
                        p.text = f"Question {i+1}: {ans}"
                        
                    p.space_after = Pt(12)
                    p.font.size = Pt(14)
            else:
                p = tf_answers.add_paragraph()
                combo_text = f"Solutions:\n{answers}"
                if teacher_notes:
                    combo_text += f"\n\nTeacher guidance:\n{teacher_notes}"
                p.text = combo_text
                p.space_after = Pt(12)
                p.font.size = Pt(14)

    ppt_buffer = io.BytesIO()
    prs.save(ppt_buffer)
    ppt_buffer.seek(0)
    return ppt_buffer.getvalue()


# --- PDF GENERATOR ---
def generate_task_pdf(title, scenario, questions, extension, phase, theme, answers=None, teacher_notes=None, misconceptions=None):
    """
    Generates a printable A4 PDF student worksheet with a solutions & notes page.
    """
    buffer = io.BytesIO()
    font_normal, font_bold = get_macron_font()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=24,
        bottomMargin=24
    )

    story = []
    styles = getSampleStyleSheet()

    total_text_length = len(title) + len(scenario) + sum(len(q) for q in questions) + (len(extension) if extension else 0)
    
    if total_text_length > 600:
        title_size, title_lead = 15, 19
        body_size, body_lead = 9, 12
        q_size, q_lead = 9.5, 13
        scen_padding = 5
        space_after_box = 10
    else:
        title_size, title_lead = 17, 21
        body_size, body_lead = 9.5, 13
        q_size, q_lead = 10, 14
        scen_padding = 7
        space_after_box = 12

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=title_size,
        leading=title_lead,
        textColor=colors.HexColor('#1B365D'),
        spaceAfter=2
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#4A5568')
    )

    scenario_style = ParagraphStyle(
        'ScenarioText',
        parent=styles['Normal'],
        fontName=font_normal,
        fontSize=body_size,
        leading=body_lead,
        textColor=colors.HexColor('#2D3748')
    )

    question_style = ParagraphStyle(
        'QuestionText',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=q_size,
        leading=q_lead,
        textColor=colors.HexColor('#1A202C')
    )

    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"<b>Phase:</b> {phase} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Context:</b> {theme}", meta_style))
    story.append(Spacer(1, 4))

    scenario_p = Paragraph(f"<b>Scenario:</b><br/>{scenario}", scenario_style)
    scenario_table = Table([[scenario_p]], colWidths=[523])
    scenario_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F7FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E0')),
        ('PADDING', (0, 0), (-1, -1), scen_padding),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(scenario_table)
    story.append(Spacer(1, 10))

    num_questions = len(questions)
    total_units = num_questions + (2 if extension else 0)
    
    estimated_text_lines = sum(max(1, len(q) // 80) for q in questions) + (max(1, len(extension) // 80) if extension else 0)
    text_height = estimated_text_lines * q_lead
    
    gaps_space = (num_questions + (1 if extension else 0)) * (space_after_box + 4)
    available_box_space = 460 - text_height - gaps_space
    
    unit_height = max(35, min(75, available_box_space / max(1, total_units)))
    standard_box_height = unit_height
    extension_box_height = unit_height * 2 

    def create_working_box(box_height):
        t = Table([['']], colWidths=[523], rowHeights=[box_height])
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#A0AEC0')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))
        return t

    for idx, q_text in enumerate(questions, 1):
        story.append(Paragraph(f"<b>Question {idx}:</b> {q_text}", question_style))
        story.append(Spacer(1, 3))
        story.append(create_working_box(box_height=standard_box_height))
        story.append(Spacer(1, space_after_box))

    if extension:
        story.append(Paragraph(f"<b>Extension Challenge:</b> {extension}", question_style))
        story.append(Spacer(1, 3))
        story.append(create_working_box(box_height=extension_box_height))
        story.append(Spacer(1, space_after_box))

    # --- PAGE 2: SOLUTIONS, TEACHER NOTES & MISCONCEPTIONS ---
    if answers or teacher_notes or misconceptions:
        story.append(PageBreak()) 
        
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading1'],
            fontName=font_bold,
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1B365D'),
            spaceAfter=15
        )
        
        body_style = ParagraphStyle(
            'SectionBody',
            parent=styles['Normal'],
            fontName=font_normal,
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#2D3748'),
            spaceAfter=12
        )
        
        story.append(Paragraph("Solutions & Notes", section_title_style))

        if misconceptions:
            story.append(Paragraph("<b>Common Misconceptions:</b>", body_style))
            story.append(Paragraph(str(misconceptions), body_style))
            story.append(Spacer(1, 10))
            
        if answers:
            if isinstance(answers, list):
                for i, ans in enumerate(answers):
                    if i == len(answers) - 1:
                        combo_text = f"<b>Extension Solution & Teacher guidance:</b><br/>{ans}"
                        if teacher_notes:
                            combo_text += f"<br/><i>Notes:</i> {teacher_notes}"
                        story.append(Paragraph(combo_text, body_style))
                    else:
                        story.append(Paragraph(f"<b>Question {i+1}:</b> {ans}", body_style))
            else:
                ans_text = f"<b>Solutions:</b><br/>{answers}"
                if teacher_notes:
                    ans_text += f"<br/><br/><b>Teacher guidance:</b><br/>{teacher_notes}"
                story.append(Paragraph(ans_text, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
