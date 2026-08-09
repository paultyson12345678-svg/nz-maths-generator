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
        '/Library/Fonts/DejaVuSans.ttf',
        'C:\\Windows\\Fonts\\DejaVuSans.ttf',
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('DejaVuSans', path))
                _registered_font_name = 'DejaVuSans'
                
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
      - Page 2: Full answer key and solutions with a generous gap between answers.
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
        spaceAfter=10
    )

    answer_style = ParagraphStyle(
        'AnswerText',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#0F172A')
    )

    title = format_text_with_macrons(title)
    scenario = format_text_with_macrons(scenario)
    questions = [format_text_with_macrons(q) for q in questions]
    extension = format_text_with_macrons(extension) if extension else ""

    # --- PAGE 1: WORKSHEET ---
    story.append(Paragraph(f"<b>{title}</b>", title_style))
    story.append(Paragraph(f"<b>Phase:</b> {phase} &nbsp;|&nbsp; <b>Context:</b> {theme}", meta_style))

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

    # --- PAGE 2: SOLUTIONS ---
    if answers:
        story.append(PageBreak())

        story.append(Paragraph(f"<b>{title} — Answer Key & Solutions</b>", title_style))
        story.append(Paragraph(f"<b>Phase:</b> {phase} &nbsp;|&nbsp; <b>Context:</b> {theme}", meta_style))
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>Solutions & Mark Scheme</b>", section_heading))
        story.append(Spacer(1, 8))

        if isinstance(answers, list):
            for idx, ans_text in enumerate(answers, 1):
                formatted_ans = format_text_with_macrons(str(ans_text))
                ans_p = Paragraph(f"<b>Q{idx} Solution:</b> {formatted_ans}", answer_style)
                ans_table = Table([[ans_p]], colWidths=[523])
                ans_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                    ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#CBD5E1')),
                    ('PADDING', (0, 0), (-1, -1), 10),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(ans_table)
                # Generous gap between solution boxes on Page 2
                story.append(Spacer(1, 28))
        else:
            formatted_ans = format_text_with_macrons(str(answers))
            ans_p = Paragraph(formatted_ans, answer_style)
            ans_table = Table([[ans_p]], colWidths=[523])
            ans_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#CBD5E1')),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(ans_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()


def generate_powerpoint_slide(title, scenario, questions, extension, phase, theme, answers=None):
    """
    Generates a 3-slide PowerPoint presentation (.pptx):
      - Slide 1: Title, larger scenario font size (18pt), generous gap, Question 1 (20pt).
      - Slide 2: Question 2+ (20pt) and Extension Challenge (20pt) with generous spacing between them.
      - Slide 3: Answer Key & Solutions.
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

    # Scenario Box (Bigger Font + Generous Height)
    scen_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(2.0))
    tf_scen = scen_box.text_frame
    tf_scen.word_wrap = True
    p_scen = tf_scen.paragraphs[0]
    p_scen.text = f"Scenario: {scenario}"
    p_scen.font.size = Pt(24)
    p_scen.font.color.rgb = RGBColor(31, 41, 55)

    # Question 1 Box (Larger 20pt font + generous gap from scenario)
    q1_box = slide1.shapes.add_textbox(Inches(0.8), Inches(3.6), Inches(11.7), Inches(3.2))
    tf_q1 = q1_box.text_frame
    tf_q1.word_wrap = True
    if questions:
        p_q1 = tf_q1.paragraphs[0]
        p_q1.text = f"1. {questions[0]}"
        p_q1.font.size = Pt(20)  # Larger font size
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
        p_q.font.size = Pt(20)  # Larger font size
        p_q.space_after = Pt(40)  # Significantly larger gap after Question 2

    if extension:
        p_ext = tf_q2.paragraphs[0] if first_item else tf_q2.add_paragraph()
        p_ext.text = f"Extension Challenge:\n{extension}"
        p_ext.font.size = Pt(20)  # Larger font size
        p_ext.font.bold = True
        p_ext.font.color.rgb = RGBColor(180, 83, 9)
        p_ext.space_before = Pt(30)  # Extra spacing above extension challenge

    # --- SLIDE 3: Answer Key & Solutions ---
    if answers:
        slide3 = prs.slides.add_slide(blank_layout)

        sol_title_box = slide3.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.7))
        tf_sol = sol_title_box.text_frame
        tf_sol.word_wrap = True
        p_sol_title = tf_sol.paragraphs[0]
        p_sol_title.text = f"{title} — Answer Key & Solutions"
        p_sol_title.font.size = Pt(24)
        p_sol_title.font.bold = True
        p_sol_title.font.color.rgb = RGBColor(30, 58, 138)

        ans_box = slide3.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.5))
        tf_ans = ans_box.text_frame
        tf_ans.word_wrap = True

        if isinstance(answers, list):
            for idx, ans in enumerate(answers, 1):
                p_a = tf_ans.add_paragraph() if idx > 1 else tf_ans.paragraphs[0]
                p_a.text = f"Q{idx} Solution: {ans}"
                p_a.font.size = Pt(16)
                p_a.space_after = Pt(22)
        else:
            p_a = tf_ans.paragraphs[0]
            p_a.text = str(answers)
            p_a.font.size = Pt(16)
            p_a.space_after = Pt(22)

    buffer = io.BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
