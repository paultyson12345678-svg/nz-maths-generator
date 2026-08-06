import io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image, ImageDraw, ImageFont


def generate_powerpoint_slide(title, scenario, questions, extension, phase, theme, answers):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)

    # 1. Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.8))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title
    p_title.font.size = Pt(32)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(15, 23, 42)

    # 2. Main Task / Content Box
    task_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(7.5), Inches(5.3))
    tf_task = task_box.text_frame
    tf_task.word_wrap = True

    p_scen = tf_task.paragraphs[0]
    p_scen.text = f"Context: {scenario}"
    p_scen.font.size = Pt(18)
    p_scen.font.color.rgb = RGBColor(51, 65, 85)

    for idx, q in enumerate(questions, start=1):
        p_q = tf_task.add_paragraph()
        p_q.text = f"\nQuestion {idx}: {q}"
        p_q.font.size = Pt(18)
        p_q.font.bold = True
        p_q.font.color.rgb = RGBColor(30, 41, 59)

    if extension:
        p_ext = tf_task.add_paragraph()
        p_ext.text = f"\nExtension Challenge: {extension}"
        p_ext.font.size = Pt(18)
        p_ext.font.italic = True
        p_ext.font.color.rgb = RGBColor(180, 83, 9)

    # 3. Teacher Notes / Solutions Sidebar Box
    notes_box = slide.shapes.add_textbox(Inches(8.7), Inches(1.5), Inches(3.8), Inches(5.3))
    tf_notes = notes_box.text_frame
    tf_notes.word_wrap = True

    p_ntitle = tf_notes.paragraphs[0]
    p_ntitle.text = "Teacher Notes & Guidance"
    p_ntitle.font.size = Pt(20)
    p_ntitle.font.bold = True
    p_ntitle.font.color.rgb = RGBColor(30, 58, 138)

    if len(answers) >= 1:
        p_a1 = tf_notes.add_paragraph()
        p_a1.text = f"\nQ1 Solution:\n{answers[0]}"
        p_a1.font.size = Pt(14)

    if len(answers) >= 2:
        p_a2 = tf_notes.add_paragraph()
        p_a2.text = f"\nQ2 Solution:\n{answers[1]}"
        p_a2.font.size = Pt(14)

    if len(answers) >= 3 and answers[2]:
        p_aext = tf_notes.add_paragraph()
        p_aext.text = f"\nExtension Solution:\n{answers[2]}"
        p_aext.font.size = Pt(14)

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    return output


def generate_task_pdf(title, scenario, questions, extension, phase, theme, answers):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor='#0F172A', spaceAfter=12)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=11, leading=16, textColor='#334155', spaceAfter=10)
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontSize=12, leading=16, textColor='#1E293B', spaceAfter=8)
    ext_style = ParagraphStyle('ExtStyle', parent=styles['Normal'], fontSize=11, leading=16, textColor='#B45309', spaceAfter=12)

    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"<b>Context & Scenario:</b> {scenario}", body_style))
    story.append(Spacer(1, 10))

    for idx, q in enumerate(questions, start=1):
        story.append(Paragraph(f"<b>Question {idx}:</b> {q}", bold_style))
        story.append(Spacer(1, 8))

    if extension:
        story.append(Paragraph(f"<b>Extension Challenge:</b> {extension}", ext_style))
        story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Teacher Guidance & Solutions:</b>", bold_style))
    for idx, ans in enumerate(answers, start=1):
        if idx <= len(questions):
            story.append(Paragraph(f"<b>Q{idx} Guidance:</b> {ans}", body_style))
        elif idx == 3 and ans:
            story.append(Paragraph(f"<b>Extension Guidance:</b> {ans}", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_task_card_image(title, scenario, questions, extension):
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Border
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(15, 23, 42), width=4)

    font_large = ImageFont.load_default()

    y = 40
    draw.text((40, y), title, fill=(15, 23, 42), font=font_large)
    y += 40

    # Draw scenario lines
    draw.text((40, y), f"Scenario: {scenario[:120]}...", fill=(51, 65, 85), font=font_large)
    y += 60

    for idx, q in enumerate(questions, start=1):
        draw.text((40, y), f"Q{idx}: {q[:100]}...", fill=(30, 41, 59), font=font_large)
        y += 50

    if extension:
        draw.text((40, y), f"Extension: {extension[:100]}...", fill=(180, 83, 9), font=font_large)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
