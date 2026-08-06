# exporters.py
import io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from PIL import Image, ImageDraw, ImageFont

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- POWERPOINT (.pptx) GENERATOR ---
def generate_powerpoint_slide(title, scenario, questions, extension, phase, theme, answers=None):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Slide 1: Student Task Visual Slide
    slide_layout = prs.slide_layouts[6] # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # Header Banner Background
    header_box = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(1.2)) # Rect
    header_box.fill.solid()
    header_box.fill.fore_color.rgb = RGBColor(0, 51, 102) # NZ Dark Blue
    header_box.line.color.rgb = RGBColor(0, 51, 102)
    
    # Title Text
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12.333), Inches(0.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f"🇳🇿 {title}"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    
    # Scenario Box (Highlighted)
    scenario_bg = slide.shapes.add_shape(1, Inches(0.5), Inches(1.5), Inches(12.333), Inches(1.8))
    scenario_bg.fill.solid()
    scenario_bg.fill.fore_color.rgb = RGBColor(240, 244, 248) # Light Gray-Blue
    scenario_bg.line.color.rgb = RGBColor(200, 210, 220)
    
    stf = scenario_bg.text_frame
    stf.word_wrap = True
    sp = stf.paragraphs[0]
    sp.text = scenario
    sp.font.size = Pt(18)
    sp.font.italic = True
    sp.font.color.rgb = RGBColor(30, 30, 30)
    
    # Questions Box
    q_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.5), Inches(12.333), Inches(2.5))
    qtf = q_box.text_frame
    qtf.word_wrap = True
    
    qp1 = qtf.paragraphs[0]
    qp1.text = "Questions:"
    qp1.font.bold = True
    qp1.font.size = Pt(20)
    qp1.font.color.rgb = RGBColor(0, 51, 102)
    
    for idx, q in enumerate(questions, 1):
        qp = qtf.add_paragraph()
        qp.text = f"{idx}. {q}"
        qp.font.size = Pt(18)
        qp.font.color.rgb = RGBColor(20, 20, 20)
        
    # Extension Box
    ext_bg = slide.shapes.add_shape(1, Inches(0.5), Inches(6.1), Inches(12.333), Inches(1.0))
    ext_bg.fill.solid()
    ext_bg.fill.fore_color.rgb = RGBColor(230, 245, 235) # Light Green
    ext_bg.line.color.rgb = RGBColor(160, 210, 170)
    
    etf = ext_bg.text_frame
    etf.word_wrap = True
    ep = etf.paragraphs[0]
    ep.text = f"🌟 Extension: {extension}"
    ep.font.size = Pt(16)
    ep.font.bold = True
    ep.font.color.rgb = RGBColor(0, 100, 40)
    
    # Slide 2: Teacher Answer Key (If available)
    if answers:
        slide2 = prs.slides.add_slide(slide_layout)
        
        t_header = slide2.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(1.2))
        t_header.fill.solid()
        t_header.fill.fore_color.rgb = RGBColor(180, 40, 40) # Red Accent for Answers
        t_header.line.color.rgb = RGBColor(180, 40, 40)
        
        t_title = slide2.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12.333), Inches(0.8))
        ttp = t_title.text_frame.paragraphs[0]
        ttp.text = f"📝 Teacher Answer Key: {title}"
        ttp.font.size = Pt(28)
        ttp.font.bold = True
        ttp.font.color.rgb = RGBColor(255, 255, 255)
        
        a_box = slide2.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(12.333), Inches(5.5))
        atf = a_box.text_frame
        atf.word_wrap = True
        
        for idx, ans in enumerate(answers, 1):
            ap = atf.add_paragraph()
            ap.text = f"Question {idx} Solution: {ans}"
            ap.font.size = Pt(18)
            ap.font.color.rgb = RGBColor(20, 20, 20)
            ap.space_after = Pt(14)
            
    buffer = io.BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# --- PRINTABLE WORKSHEET PDF GENERATOR ---
def generate_task_pdf(title, scenario, questions, extension, phase, theme, answers=None):
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
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#003366'),
        spaceAfter=6
    )
    
    scenario_style = ParagraphStyle(
        'ScenarioStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1A1A1A'),
        spaceAfter=12
    )
    
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        spaceAfter=6
    )
    
    elements = []
    
    # 1. Student Header Block
    header_data = [
        [Paragraph("<b>Name:</b> ___________________________", styles['Normal']), 
         Paragraph("<b>Date:</b> ______________", styles['Normal'])]
    ]
    header_table = Table(header_data, colWidths=[350, 170])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 5))
    
    # 2. Task Title & Scenario
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"<b>Phase:</b> {phase} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Context:</b> {theme}", styles['Normal']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(scenario, scenario_style))
    elements.append(Spacer(1, 10))
    
    # 3. Questions with Working Boxes
    for idx, q in enumerate(questions, 1):
        elements.append(Paragraph(f"{idx}. {q}", question_style))
        
        # Answer Box Table
        box_data = [[Paragraph("<font color='#888888'>Show your working out here:</font>", styles['Normal'])]]
        box_table = Table(box_data, colWidths=[520], rowHeights=[65])
        box_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(box_table)
        elements.append(Spacer(1, 10))
        
    # 4. Extension Box
    elements.append(Paragraph(f"<b>🌟 Extension Challenge:</b> {extension}", question_style))
    ext_box_data = [[Paragraph("<font color='#888888'>Extension Working & Answer:</font>", styles['Normal'])]]
    ext_box_table = Table(ext_box_data, colWidths=[520], rowHeights=[60])
    ext_box_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#88CC99')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F2FAF4')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(ext_box_table)
    
    # 5. Teacher Answer Key Page (Separate Page)
    if answers:
        elements.append(PageBreak())
        elements.append(Paragraph(f"📝 Teacher Answer Key: {title}", title_style))
        elements.append(Spacer(1, 10))
        
        for idx, ans in enumerate(answers, 1):
            elements.append(Paragraph(f"<b>Question {idx} Answer & Guidance:</b>", question_style))
            elements.append(Paragraph(ans, styles['Normal']))
            elements.append(Spacer(1, 10))
            
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# --- TASK CARD PNG IMAGE GENERATOR ---
def generate_task_card_image(title, scenario, questions, extension):
    img = Image.new('RGB', (1000, 700), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Decorative Header Bar
    d.rectangle([0, 0, 1000, 80], fill=(0, 51, 102))
    d.text((30, 25), f"Task Card: {title}", fill=(255, 255, 255))
    
    # Scenario Box
    d.rectangle([30, 100, 970, 220], fill=(240, 244, 248), outline=(200, 210, 220))
    d.text((45, 120), scenario[:140] + "..." if len(scenario) > 140 else scenario, fill=(30, 30, 30))
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
