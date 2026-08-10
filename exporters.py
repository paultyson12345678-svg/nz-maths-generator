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


# --- PDF GENERATOR ---
def generate_task_pdf(title, scenario, questions, extension, phase, theme, answers):
    """
    Generates a 1-page printable A4 PDF student worksheet.
    Dynamically adjusts working box heights and font sizes while making the 
    Extension Challenge working box double the height of standard question boxes,
    ensuring all content remains cleanly formatted on a single page.
    """
    buffer = io.BytesIO()

    # Register/fetch macron font
    font_normal, font_bold = get_macron_font()

    # 1. Page dimensions & setup (A4: 595.27 x 841.89 pt)
    # Margins: Top/Bottom 24pt, Left/Right 36pt -> Printable height ~793pt
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

    # 2. Estimate text volume to dynamically tune font sizes
    total_text_length = len(title) + len(scenario) + sum(len(q) for q in questions) + (len(extension) if extension else 0)
    
    # Adjust typography and spacing for breathing room
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

    # 3. Add Header & Scenario Box
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

    # 4. Calculate Dynamic Box Heights (Double height for Extension Box)
    # Unit allocation: each regular question = 1 unit, extension box = 2 units
    num_questions = len(questions)
    total_units = num_questions + (2 if extension else 0)
    
    # Estimate vertical space taken by question/extension headers
    estimated_text_lines = sum(max(1, len(q) // 80) for q in questions) + (max(1, len(extension) // 80) if extension else 0)
    text_height = estimated_text_lines * q_lead
    
    # Available vertical space calculation
    gaps_space = (num_questions + (1 if extension else 0)) * (space_after_box + 4)
    available_box_space = 460 - text_height - gaps_space
    
    # Calculate height per 1 unit
    unit_height = max(35, min(75, available_box_space / max(1, total_units)))
    
    standard_box_height = unit_height
    extension_box_height = unit_height * 2  # Double the size for extension answer box

    def create_working_box(box_height):
        t = Table([['']], colWidths=[523], rowHeights=[box_height])
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#A0AEC0')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))
        return t

    # 5. Build Questions & Working Boxes
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
