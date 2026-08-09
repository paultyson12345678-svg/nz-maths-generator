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

# Register Font for Macrons
_font_registered = False
_registered_font_name = 'Helvetica'
_registered_bold_font_name = 'Helvetica-Bold'

def register_macron_font():
    global _font_registered, _registered_font_name, _registered_bold_font_name
    if _font_registered:
        return _registered_font_name, _registered_bold_font_name

    # Try local font file in project root first
    local_font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
    
    # Check common system font locations for DejaVu Sans
    font_paths = [
        local_font_path,
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf',
        '/Library/Fonts/DejaVuSans.ttf',
        'C:\\Windows\\Fonts\\DejaVuSans.ttf',
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('DejaVuSans', path))
                _registered_font_name = 'DejaVuSans'
                
                # Check for Bold variant
                bold_path = path.replace('.ttf', '-Bold.ttf')
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_path))
                    _registered_bold_font_name = 'DejaVuSans-Bold'
                else:
                    _registered_bold_font_name = 'DejaVuSans'
                
                _font_registered = True
                return _registered_font_name, _registered_bold_font_name
            except Exception:
                pass

    _font_registered = True
    return _registered_font_name, _registered_bold_font_name


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render page footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor('#6B7280'))
        
        # Draw top separator line on Page 2+
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.5)
            self.line(36, 800, 559, 800)

        # Footer line
        self.setStrokeColor(colors.HexColor('#E2E8F0'))
        self.setLineWidth(0.5)
        self.line(36, 42, 559, 42)
        
        # Footer text
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 28, footer_text)
        self.drawString(36, 28, "NZ Curriculum Mathematics — Generated Worksheet")
        self.restoreState()


def format_text_with_macrons(text):
    """
    Ensures macron characters in text are properly formatted for ReportLab.
    """
    if not text:
        return ""
    # Standardize macron unicode characters
    macron_map = {
        'ā': 'ā', 'Ā': 'Ā',
        'ē': 'ē', 'Ē': 'Ē',
        'ī': 'ī', 'Ī': 'Ī',
        'ō': 'ō', 'Ō': 'Ō',
        'ū': 'ū', 'Ū': 'Ū'
    }
    for k, v in macron_map.items():
        text = text.replace(k, v)
    return text


def generate_task_pdf(title, scenario, questions, extension, phase, theme, answers=None):
    """
    Generates a PDF worksheet:
      - Page 1: Task scenario, student questions, and optional extension challenge.
      - Page 2: Full answer key and solutions (if provided).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=50
    )

    story = []
    styles = getSampleStyleSheet()
    font_name, bold_font_name = register_macron_font()

    # Base Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=bold_font_name,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=4
    )

    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=10
    )

    scenario_style = ParagraphStyle(
        'ScenarioBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1F2937')
    )

    question_style = ParagraphStyle(
        'QuestionText',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1E293B')
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName=bold_font_name,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=8,
        spaceAfter=6
    )

    answer_style = ParagraphStyle(
        'AnswerText',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#0F172A')
    )

    # Clean text inputs
    title = format_text_with_macrons(title)
    scenario = format_text_with_macrons(scenario)
    questions = [format_text_with_macrons(q) for q in questions]
    extension = format_text_with_macrons(extension) if extension else ""

    # ==================== PAGE 1: WORKSHEET ====================
    story.append(Paragraph(f"<b>{title}</b>", title_style))
    story.append(Paragraph(f"<b>Phase:</b> {phase} &nbsp;|&nbsp; <b>Context:</b> {theme}", meta_style))

    # Scenario Box
    scenario_p = Paragraph(f"<b>Scenario:</b> {scenario}", scenario_style)
    scenario_table = Table([[scenario_p]], colWidths=[523])
    scenario_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(scenario_table)
    story.append(Spacer(1, 12))

    # Dynamic box sizing for working space
    num_questions = len(questions)
    space_after_box = 8
    q_lead = 14

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

    # ==================== PAGE 2: SOLUTIONS ====================
    if answers:
        story.append(PageBreak())  # Force solution key to Page 2

        story.append(Paragraph(f"<b>{title} — Answer Key & Solutions</b>", title_style))
        story.append(Paragraph(f"<b>Phase:</b> {phase} &nbsp;|&nbsp; <b>Context:</b> {theme}", meta_style))
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Solutions & Mark Scheme</b>", section_heading))
        story.append(Spacer(1, 4))

        if isinstance(answers, list):
            for idx, ans_text in enumerate(answers, 1):
                formatted_ans = format_text_with_macrons(str(ans_text))
                ans_p = Paragraph(f"<b>Q{idx} Solution:</b> {formatted_ans}", answer_style)
                ans_table = Table([[ans_p]], colWidths=[523])
                ans_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                    ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(ans_table)
                story.append(Spacer(1, 6))
        else:
            formatted_ans = format_text_with_macrons(str(answers))
            ans_p = Paragraph(formatted_ans, answer_style)
            ans_table = Table([[ans_p]], colWidths=[523])
            ans_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#E2E8F0')),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(ans_table)

    # Build PDF Document
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
