import io
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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
    Generates a 3-slide widescreen PowerPoint presentation with larger typography:
    - Slide 1: Title, Meta, Scenario (just 'Scenario:'), and Question 1 only.
    - Slide 2: Question 2 & Extension Challenge with extra vertical spacing.
    - Slide 3: Detailed Solutions & Open-Ended Teacher Guidance.
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_slide_layout = prs.slide_layouts[6]

    # --- SLIDE 1: Title, Scenario, & Question 1 ---
    slide_1 = prs.slides.add_slide(blank_slide_layout)

    # Title Box
    title_box = slide_1.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title
    p_title.font.size = Pt(28)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(27, 54, 93)  # Dark navy blue

    # Meta Info
    p_meta = tf_title.add_paragraph()
    p_meta.text = f"Phase: {phase}  |  Context: {theme}"
    p_meta.font.size = Pt(14)
    p_meta.font.italic = True
    p_meta.font.color.rgb = RGBColor(100, 100, 100)

    # Scenario Box
    scenario_box = slide_1.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(2.2))
    tf_scenario = scenario_box.text_frame
    tf_scenario.word_wrap = True
    p_scen_header = tf_scenario.paragraphs[0]
    p_scen_header.text = "Scenario:"
    p_scen_header.font.bold = True
    p_scen_header.font.size = Pt(22)
    p_scen_header.font.color.rgb = RGBColor(45, 55, 72)

    p_scen_body = tf_scenario.add_paragraph()
    p_scen_body.text = scenario
    p_scen_body.font.size = Pt(22)
    p_scen_body.space_before = Pt(6)

    # Question 1 Box
    q1_box = slide_1.shapes.add_textbox(Inches(0.8), Inches(4.2), Inches(11.733), Inches(2.8))
    tf_q1 = q1_box.text_frame
    tf_q1.word_wrap = True

    if len(questions) > 0:
        p_q1 = tf_q1.paragraphs[0]
        p_q1.text = f"Question 1: {questions[0]}"
        p_q1.font.size = Pt(20)
        p_q1.font.bold = True

    # --- SLIDE 2: Question 2 & Extension Challenge ---
    slide_2 = prs.slides.add_slide(blank_slide_layout)

    # Header Box for Slide 2
    head_box_2 = slide_2.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(0.8))
    tf_head2 = head_box_2.text_frame
    tf_head2.word_wrap = True
    p_head2 = tf_head2.paragraphs[0]
    p_head2.text = f"{title} (Continued)"
    p_head2.font.size = Pt(26)
    p_head2.font.bold = True
    p_head2.font.color.rgb = RGBColor(27, 54, 93)

    # Tasks Box (Questions 2+ and Extension)
    q2_box = slide_2.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.5))
    tf_q2 = q2_box.text_frame
    tf_q2.word_wrap = True

    first_q2_item = True
    if len(questions) > 1:
        for idx, q_text in enumerate(questions[1:], start=2):
            p = tf_q2.paragraphs[0] if first_q2_item else tf_q2.add_paragraph()
            first_q2_item = False
            p.text = f"Question {idx}: {q_text}"
            p.font.size = Pt(20)
            p.font.bold = True
            p.space_after = Pt(16)

    if extension:
        p_ext = tf_q2.paragraphs[0] if first_q2_item else tf_q2.add_paragraph()
        p_ext.text = f"Extension Challenge: {extension}"
        p_ext.font.size = Pt(20)
        p_ext.font.bold = True
        p_ext.font.color.rgb = RGBColor(180, 83, 9)  # Warm accent color
        if not first_q2_item:
            p_ext.space_before = Pt(36)

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

    buffer = io.BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def generate_task_pdf(title, scenario, questions, extension, phase, theme, answers):
    """
    Generates a 1-page printable A4 PDF student worksheet.
    Dynamically calculates vertical height so that the Extension Challenge box receives 
    double the height of standard question working boxes while guaranteeing all content 
    remains strictly within a single page layout.
    """
    buffer = io.BytesIO()

    # Register/fetch macron font
    font_normal, font_bold = get_macron_font()

    # Page dimensions & setup (A4: 595.27 x 841.89 pt)
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

    # Estimate text volume to dynamically tune typography and padding
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

    # Header & Scenario Box
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

    # Calculate Dynamic Box Heights (1 unit per question box, 2 units for extension)
    num_questions = len(questions)
    total_units = num_questions + (2 if extension else 0)
    
    estimated_text_lines = sum(max(1, len(q) // 80) for q in questions) + (max(1, len(extension) // 80) if extension else 0)
    text_height = estimated_text_lines * q_lead
    
    gaps_space = (num_questions + (1 if extension else 0)) * (space_after_box + 4)
    available_box_space = 460 - text_height - gaps_space
    
    unit_height = max(35, min(75, available_box_space / max(1, total_units)))
    
    standard_box_height = unit_height
    extension_box_height = unit_height * 2  # Double height allocation

    def create_working_box(box_height):
        t = Table([['']], colWidths=[523], rowHeights=[box_height])
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#A0AEC0')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))
        return t

    # Build Questions & Working Boxes
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

    # Build PDF document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
