import io
import textwrap
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from PIL import Image, ImageDraw, ImageFont


# ==========================================
# 1. POWERPOINT EXPORT (3 SLIDES)
# ==========================================
def generate_powerpoint_slide(title, scenario, questions, extension, phase, theme, answers=None):
    prs = Presentation()
    
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    q1 = questions[0] if len(questions) > 0 else ""
    q2 = questions[1] if len(questions) > 1 else ""
    
    ans1 = answers[0] if answers and len(answers) > 0 else ""
    ans2 = answers[1] if answers and len(answers) > 1 else ""
    ans_ext = answers[2] if answers and len(answers) > 2 else ""

    # Color Palette
    TEAL = RGBColor(0, 102, 102)
    DARK_GRAY = RGBColor(40, 40, 40)
    LIGHT_GRAY = RGBColor(240, 242, 245)
    BLUE_ACCENT = RGBColor(0, 51, 102)

    def add_header(slide, subtitle_text):
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(0.8))
        tf = title_box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = TEAL

        p2 = tf.add_paragraph()
        p2.text = f"{phase} | Context: {theme} | {subtitle_text}"
        p2.font.size = Pt(14)
        p2.font.color.rgb = RGBColor(100, 100, 100)

    # --- SLIDE 1: Scenario & Question 1 ---
    slide1 = prs.slides.add_slide(blank_layout)
    add_header(slide1, "Part 1: The Scenario & Question 1")

    # Scenario Box
    scen_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.733), Inches(2.2))
    tf_scen = scen_box.text_frame
    tf_scen.word_wrap = True
    p = tf_scen.paragraphs[0]
    p.text = "Context & Scenario:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = BLUE_ACCENT
    
    p_body = tf_scen.add_paragraph()
    p_body.text = scenario
    p_body.font.size = Pt(18)
    p_body.font.color.rgb = DARK_GRAY

    # Question 1 Box
    q1_box = slide1.shapes.add_textbox(Inches(0.8), Inches(4.0), Inches(11.733), Inches(2.8))
    tf_q1 = q1_box.text_frame
    tf_q1.word_wrap = True
    p = tf_q1.paragraphs[0]
    p.text = "Question 1:"
    p.font.bold = True
    p.font.size = Pt(20)
    p.font.color.rgb = TEAL
    
    p_q1 = tf_q1.add_paragraph()
    p_q1.text = q1
    p_q1.font.size = Pt(20)
    p_q1.font.color.rgb = DARK_GRAY

    # --- SLIDE 2: Question 2 & Extension ---
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Part 2: Question 2 & Extension Challenge")

    # Question 2 Box
    q2_box = slide2.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.733), Inches(2.5))
    tf_q2 = q2_box.text_frame
    tf_q2.word_wrap = True
    p = tf_q2.paragraphs[0]
    p.text = "Question 2:"
    p.font.bold = True
    p.font.size = Pt(20)
    p.font.color.rgb = TEAL
    
    p_q2 = tf_q2.add_paragraph()
    p_q2.text = q2
    p_q2.font.size = Pt(20)
    p_q2.font.color.rgb = DARK_GRAY

    # Extension Challenge Box
    ext_box = slide2.shapes.add_textbox(Inches(0.8), Inches(4.3), Inches(11.733), Inches(2.5))
    tf_ext = ext_box.text_frame
    tf_ext.word_wrap = True
    p = tf_ext.paragraphs[0]
    p.text = "Extension Challenge:"
    p.font.bold = True
    p.font.size = Pt(20)
    p.font.color.rgb = RGBColor(180, 80, 0)
    
    p_ext = tf_ext.add_paragraph()
    p_ext.text = extension
    p_ext.font.size = Pt(20)
    p_ext.font.color.rgb = DARK_GRAY

    # --- SLIDE 3: Teacher Answers & Notes ---
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Teacher Solutions & Answer Guide")

    ans_box = slide3.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))
    tf_ans = ans_box.text_frame
    tf_ans.word_wrap = True

    # Q1 Answer
    p = tf_ans.paragraphs[0]
    p.text = "Question 1 Solution:"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = TEAL
    p_body = tf_ans.add_paragraph()
    p_body.text = ans1 + "\n"
    p_body.font.size = Pt(15)
    p_body.font.color.rgb = DARK_GRAY

    # Q2 Answer
    p = tf_ans.add_paragraph()
    p.text = "Question 2 Solution:"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = TEAL
    p_body = tf_ans.add_paragraph()
    p_body.text = ans2 + "\n"
    p_body.font.size = Pt(15)
    p_body.font.color.rgb = DARK_GRAY

    # Extension Answer
    p = tf_ans.add_paragraph()
    p.text = "Extension Solution:"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = RGBColor(180, 80, 0)
    p_body = tf_ans.add_paragraph()
    p_body.text = ans_ext
    p_body.font.size = Pt(15)
    p_body.font.color.rgb = DARK_GRAY

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    return output.getvalue()


# ==========================================
# 2. PDF WORKSHEET EXPORT (SEPARATE ANSWER PAGE)
# ==========================================
def generate_task_pdf(title, scenario, questions, extension, phase, theme, answers=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#006666'), spaceAfter=4)
    meta_style = ParagraphStyle('MetaStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#555555'), spaceAfter=12)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#003366'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=11, leading=14, textColor=colors.black, spaceAfter=8)

    q1 = questions[0] if len(questions) > 0 else ""
    q2 = questions[1] if len(questions) > 1 else ""
    
    ans1 = answers[0] if answers and len(answers) > 0 else ""
    ans2 = answers[1] if answers and len(answers) > 1 else ""
    ans_ext = answers[2] if answers and len(answers) > 2 else ""

    elements = []

    # Student Worksheet Header
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"<b>Phase:</b> {phase} | <b>Context:</b> {theme} &nbsp;&nbsp;&nbsp;&nbsp; <b>Name:</b> ___________________________", meta_style))
    
    # Scenario
    elements.append(Paragraph("<b>Context & Scenario:</b>", heading_style))
    elements.append(Paragraph(scenario, body_style))
    elements.append(Spacer(1, 8))

    # Q1 + Working Space Box
    elements.append(Paragraph("<b>Question 1:</b> " + q1, body_style))
    box_q1 = Table([["Working / Answer:"]], colWidths=[540], rowHeights=[90])
    box_q1.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#888888')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('FONTSIZE', (0,0), (-1,-1), 9)
    ]))
    elements.append(box_q1)
    elements.append(Spacer(1, 12))

    # Q2 + Working Space Box
    elements.append(Paragraph("<b>Question 2:</b> " + q2, body_style))
    box_q2 = Table([["Working / Answer:"]], colWidths=[540], rowHeights=[90])
    box_q2.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#888888')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('FONTSIZE', (0,0), (-1,-1), 9)
    ]))
    elements.append(box_q2)
    elements.append(Spacer(1, 12))

    # Extension + Working Space Box
    elements.append(Paragraph("<b>Extension Challenge:</b> " + extension, body_style))
    box_ext = Table([["Working / Answer:"]], colWidths=[540], rowHeights=[100])
    box_ext.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#B8860B')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#888888')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('FONTSIZE', (0,0), (-1,-1), 9)
    ]))
    elements.append(box_ext)

    # --- SEPARATE PAGE FOR TEACHER ANSWERS ---
    elements.append(PageBreak())

    elements.append(Paragraph(f"{title} - Teacher Answer Key", title_style))
    elements.append(Paragraph(f"<b>Phase:</b> {phase} | <b>Context:</b> {theme}", meta_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Question 1 Solution:</b>", heading_style))
    elements.append(Paragraph(ans1, body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Question 2 Solution:</b>", heading_style))
    elements.append(Paragraph(ans2, body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Extension Solution:</b>", heading_style))
    elements.append(Paragraph(ans_ext, body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# ==========================================
# 3. TASK CARD IMAGE EXPORT (NO TEXT CUTOFF)
# ==========================================
def generate_task_card_image(title, scenario, questions, extension):
    # Generous dimensions to prevent text truncation
    width, height = 1200, 1500
    img = Image.new('RGB', (width, height), color='#F8F9FA')
    draw = ImageDraw.Draw(img)

    # Header Card Banner
    draw.rectangle([(0, 0), (width, 140)], fill='#006666')

    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_header = ImageFont.truetype("arial.ttf", 26)
        font_body = ImageFont.truetype("arial.ttf", 22)
    except IOError:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # Draw Title
    draw.text((40, 45), title, fill='white', font=font_title)

    y = 180
    q1 = questions[0] if len(questions) > 0 else ""
    q2 = questions[1] if len(questions) > 1 else ""

    sections = [
        ("Context & Scenario", scenario, '#003366'),
        ("Question 1", q1, '#006666'),
        ("Question 2", q2, '#006666'),
        ("Extension Challenge", extension, '#B8860B')
    ]

    for header, content, color in sections:
        # Header text
        draw.text((50, y), header + ":", fill=color, font=font_header)
        y += 40

        # Wrap body text cleanly at ~68 chars/line
        wrapped = textwrap.wrap(content, width=68)
        for line in wrapped:
            draw.text((50, y), line, fill='#222222', font=font_body)
            y += 32
        
        y += 35  # Section spacing

    # Decorative Border
    draw.rectangle([(15, 15), (width - 15, height - 15)], outline='#006666', width=4)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
