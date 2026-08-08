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
    Generates a widescreen PowerPoint presentation containing the task scenario,
    questions, extension, and full answer key with guidance notes.
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_slide_layout = prs.slide_layouts[6]

    # --- SLIDE 1: Student Task Slide ---
    slide_1 = prs.slides.add_slide(blank_slide_layout)

    # Title Box
    title_box = slide_1.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.0))
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
    scenario_box = slide_1.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(1.5))
    tf_scenario = scenario_box.text_frame
    tf_scenario.word_wrap = True
    p_scen_header = tf_scenario.paragraphs[0]
    p_scen_header.text = "Context & Scenario:"
    p_scen_header.font.bold = True
    p_scen_header.font.size = Pt(16)
    p_scen_header.font.color.rgb = RGBColor(45, 55, 72)

    p_scen_body = tf_scenario.add_paragraph()
    p_scen_body.text = scenario
    p_scen_body.font.size = Pt(15)

    # Questions Box
    q_box = slide_1.shapes.add_textbox(Inches(0.8), Inches(3.3), Inches(11.733), Inches(3.6))
    tf_q = q_box.text_frame
    tf_q.word_wrap = True

    p_q_header = tf_q.paragraphs[0]
    p_q_header.text = "Tasks & Questions:"
    p_q_header.font.bold = True
    p_q_header.font.size = Pt(16)
    p_q_header.font.color.rgb = RGBColor(45, 55, 72)

    for idx, q_text in enumerate(questions, 1):
        p = tf_q.add_paragraph()
        p.text = f"Question {idx}: {q_text}"
        p.font.size = Pt(15)
        p.space_after = Pt(10)

    if extension:
        p_ext = tf_q.add_paragraph()
        p_ext.text = f"<b>Extension Challenge: {extension}"
        p_ext.font.size = Pt(15)
        p_ext.font.bold = True
        p_ext.font.color.rgb = RGBColor(180, 83, 9)

    # --- SLIDE 2: Teacher Answers & Guidance Slide ---
    slide_2 = prs.slides.add_slide(blank_slide_layout)

    title_box_2 = slide_2.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.0))
    tf_title_2 = title_box_2.text_frame
    tf_title_2.word_wrap = True
    p_title_2 = tf_title_2.paragraphs[0]
    p_title_2.text = f"Solutions & Teacher Guidance: {title}"
    p_title_2.font.size = Pt(24)
    p_title_2.font.bold = True
    p_title_2.font.color.rgb = RGBColor(27, 54, 93)

    ans_box = slide_2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.3))
    tf_ans = ans_box.text_frame
    tf_ans.word_wrap = True

    for idx, ans_text in enumerate(answers, 1):
        p_ans = tf_ans.add_paragraph() if idx > 1 else tf_ans.paragraphs[0]
        label = f"Question {idx} Answer:" if idx <= len(questions) else "Extension Answer:"
        p_ans.text = f"• {label} {ans_text}"
        p_ans.font.size = Pt(14)
        p_ans.space_after = Pt(12)

    buffer = io.BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def generate_task_pdf(title, scenario, questions, extension, phase, theme, answers):
    """
    Generates a printable A4 PDF student worksheet with clean, spacious rectangular 
    working boxes that scale cleanly across the full page.
    """
    buffer = io.BytesIO()

    # Register/fetch macron font
    font_normal, font_bold = get_macron_font()

    # 1. Setup Document with standard 0.5 inch (36pt) margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # 2. Define Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1B365D'),
        spaceAfter=4
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#4A5568')
    )

    scenario_style = ParagraphStyle(
        'ScenarioText',
        parent=styles['Normal'],
        fontName=font_normal,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2D3748')
    )

    question_style = ParagraphStyle(
        'QuestionText',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1A202C')
    )

    # Header & Title Block
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"<b>Phase:</b> {phase} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Context:</b> {theme}", meta_style))
    story.append(Spacer(1, 10))

    # Context / Scenario Callout Box (A4 width - 72pt margins = 523pt wide)
    scenario_p = Paragraph(f"<b>Context & Scenario:</b><br/>{scenario}", scenario_style)
    scenario_table = Table([[scenario_p]], colWidths=[523])
    scenario_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F7FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E0')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(scenario_table)
    story.append(Spacer(1, 15))

    # Helper function to generate clean, solid working boxes
    def create_working_box(box_height=140):
        t = Table([['']], colWidths=[523], rowHeights=[box_height])
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#A0AEC0')), # Clean solid border
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))
        return t

    # 3. Main Questions + Spaced Working Boxes
    for idx, q_text in enumerate(questions, 1):
        story.append(Paragraph(f"<b>Question {idx}:</b> {q_text}", question_style))
        story.append(Spacer(1, 6))
        story.append(create_working_box(box_height=145))
        story.append(Spacer(1, 15))

    # 4. Extension Challenge + Working Box
    if extension:
        story.append(Paragraph(f"<b>⭐ Extension Challenge:</b> {extension}", question_style))
        story.append(Spacer(1, 6))
        story.append(create_working_box(box_height=145))

    # Build PDF document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
