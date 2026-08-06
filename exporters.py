# exporters.py
import io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from PIL import Image, ImageDraw

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- THEME COLOR & GRAPHIC MAPPING ---
THEME_STYLES = {
    "Sports": {
        "header_bg": RGBColor(16, 124, 65),     # Field Green
        "card_bg": RGBColor(240, 252, 243),     # Soft Mint
        "accent": RGBColor(0, 80, 30),
        "banner_color": (16, 124, 65)
    },
    "Matariki": {
        "header_bg": RGBColor(25, 25, 112),    # Midnight Blue
        "card_bg": RGBColor(240, 242, 255),    # Soft Starlight Blue
        "accent": RGBColor(180, 140, 20),
        "banner_color": (25, 25, 112)
    },
    "Ocean": {
        "header_bg": RGBColor(0, 119, 182),     # Ocean Blue
        "card_bg": RGBColor(235, 248, 255),     # Aqua Tint
        "accent": RGBColor(0, 90, 150),
        "banner_color": (0, 119, 182)
    },
    "Default": {
        "header_bg": RGBColor(0, 51, 102),      # NZ Navy Blue
        "card_bg": RGBColor(240, 245, 250),     # Cool Blue-Gray
        "accent": RGBColor(0, 51, 102),
        "banner_color": (0, 51, 102)
    }
}

def get_theme_style(theme_str):
    t_lower = theme_str.lower()
    if any(k in t_lower for k in ["sport", "rugby", "netball", "gala"]):
        return THEME_STYLES["Sports"]
    elif any(k in t_lower for k in ["hāngī", "hangi", "matariki", "marae"]):
        return THEME_STYLES["Matariki"]
    elif any(k in t_lower for k in ["waka", "beach", "marine", "sea"]):
        return THEME_STYLES["Ocean"]
    return THEME_STYLES["Default"]

def create_thematic_banner_image(theme_style):
    # Generates a kid-friendly geometric pattern banner image
    img = Image.new('RGB', (1200, 200), color=theme_style["banner_color"])
    d = ImageDraw.Draw(img)
    
    # Add playful decorative circles/polygons to theme header
    for x in range(30, 1200, 90):
        d.ellipse([x, -20, x + 60, 40], fill=(255, 255, 255, 40))
        d.ellipse([x + 30, 140, x + 80, 210], fill=(255, 255, 255, 30))
        
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# --- POWERPOINT (.pptx) GENERATOR ---
def generate_powerpoint_slide(title, scenario, questions, extension, phase, theme, answers=None):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide_layout = prs.slide_layouts[6] # Blank
    
    style = get_theme_style(theme)

    q1_text = questions[0] if len(questions) > 0 else ""
    q2_text = questions[1] if len(questions) > 1 else ""

    # ==========================================
    # SLIDE 1: TEACHER LAUNCH (Scenario + Q1)
    # ==========================================
    s1 = prs.slides.add_slide(slide_layout)
    
    # Graphic Banner
    banner_img = create_thematic_banner_image(style)
    s1.shapes.add_picture(banner_img, Inches(0), Inches(0), Inches(13.333), Inches(1.3))

    t1 = s1.shapes.add_textbox(Inches(0.6), Inches(0.25), Inches(12.133), Inches(0.8))
    tf1 = t1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = f"🇳🇿 {title}"
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)

    # Scenario Graphic Card
    sc_card = s1.shapes.add_shape(1, Inches(0.6), Inches(1.6), Inches(12.133), Inches(2.1))
    sc_card.fill.solid()
    sc_card.fill.fore_color.rgb = style["card_bg"]
    sc_card.line.color.rgb = style["header_bg"]
    sc_card.line.width = Pt(2)
    
    stf = sc_card.text_frame
    stf.word_wrap = True
    sp = stf.paragraphs[0]
    sp.text = f"📖 {scenario}"
    sp.font.size = Pt(19)
    sp.font.italic = True
    sp.font.color.rgb = RGBColor(30, 30, 30)

    # Q1 Discussion Box
    q1_card = s1.shapes.add_shape(1, Inches(0.6), Inches(3.9), Inches(12.133), Inches(3.0))
    q1_card.fill.solid()
    q1_card.fill.fore_color.rgb = RGBColor(255, 250, 230) # Warm Gold Accent
    q1_card.line.color.rgb = RGBColor(230, 180, 50)
    q1_card.line.width = Pt(2)

    q1_tf = q1_card.text_frame
    q1_tf.word_wrap = True
    
    q1_p_head = q1_tf.paragraphs[0]
    q1_p_head.text = "🎯 Main Question for Discussion:"
    q1_p_head.font.bold = True
    q1_p_head.font.size = Pt(22)
    q1_p_head.font.color.rgb = RGBColor(160, 90, 0)
    q1_p_head.space_after = Pt(8)

    q1_p_body = q1_tf.add_paragraph()
    q1_p_body.text = q1_text
    q1_p_body.font.size = Pt(22)
    q1_p_body.font.bold = True
    q1_p_body.font.color.rgb = RGBColor(20, 20, 20)

    # ==========================================
    # SLIDE 2: INDEPENDENT / FOLLOW-UP (Q2 + Ext)
    # ==========================================
    s2 = prs.slides.add_slide(slide_layout)
    
    banner_img2 = create_thematic_banner_image(style)
    s2.shapes.add_picture(banner_img2, Inches(0), Inches(0), Inches(13.333), Inches(1.3))

    t2 = s2.shapes.add_textbox(Inches(0.6), Inches(0.25), Inches(12.133), Inches(0.8))
    tf2 = t2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = f"✏️ Follow-Up Tasks: {title}"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(255, 255, 255)

    if q2_text:
        q2_card = s2.shapes.add_shape(1, Inches(0.6), Inches(1.6), Inches(12.133), Inches(2.5))
        q2_card.fill.solid()
        q2_card.fill.fore_color.rgb = style["card_bg"]
        q2_card.line.color.rgb = style["header_bg"]
        
        q2_tf = q2_card.text_frame
        q2_tf.word_wrap = True
        
        q2_head = q2_tf.paragraphs[0]
        q2_head.text = "2. Next Question:"
        q2_head.font.bold = True
        q2_head.font.size = Pt(22)
        q2_head.font.color.rgb = style["header_bg"]
        q2_head.space_after = Pt(8)

        q2_body = q2_tf.add_paragraph()
        q2_body.text = q2_text
        q2_body.font.size = Pt(21)
        q2_body.font.color.rgb = RGBColor(30, 30, 30)

    # Extension Challenge Card
    ext_card = s2.shapes.add_shape(1, Inches(0.6), Inches(4.3), Inches(12.133), Inches(2.6))
    ext_card.fill.solid()
    ext_card.fill.fore_color.rgb = RGBColor(235, 250, 240)
    ext_card.line.color.rgb = RGBColor(140, 210, 160)
    
    ext_tf = ext_card.text_frame
    ext_tf.word_wrap = True
    
    ext_head = ext_tf.paragraphs[0]
    ext_head.text = "🌟 Extension Challenge:"
    ext_head.font.bold = True
    ext_head.font.size = Pt(22)
    ext_head.font.color.rgb = RGBColor(0, 110, 50)
    ext_head.space_after = Pt(8)

    ext_body = ext_tf.add_paragraph()
    ext_body.text = extension
    ext_body.font.size = Pt(21)
    ext_body.font.color.rgb = RGBColor(20, 20, 20)

    # ==========================================
    # SLIDE 3: TEACHER ANSWER KEY & GUIDANCE
    # ==========================================
    if answers:
        s3 = prs.slides.add_slide(slide_layout)
        
        h3 = s3.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(1.3))
        h3.fill.solid()
        h3.fill.fore_color.rgb = RGBColor(180, 50, 50)
        h3.line.fill.background()

        t3 = s3.shapes.add_textbox(Inches(0.6), Inches(0.25), Inches(12.133), Inches(0.8))
        tf3 = t3.text_frame
        tf3.word_wrap = True
        p3 = tf3.paragraphs[0]
        p3.text = f"📝 Teacher Answer Key & Guidance"
        p3.font.size = Pt(28)
        p3.font.bold = True
        p3.font.color.rgb = RGBColor(255, 255, 255)

        a_card = s3.shapes.add_shape(1, Inches(0.6), Inches(1.6), Inches(12.133), Inches(5.3))
        a_card.fill.solid()
        a_card.fill.fore_color.rgb = RGBColor(253, 245, 245)
        a_card.line.color.rgb = RGBColor(230, 180, 180)
        
        atf = a_card.text_frame
        atf.word_wrap = True
        
        for idx, ans in enumerate(answers, 1):
            ap_head = atf.add_paragraph() if idx > 1 else atf.paragraphs[0]
            ap_head.text = f"Question {idx} Solution & Teaching Tip:"
            ap_head.font.bold = True
            ap_head.font.size = Pt(18)
            ap_head.font.color.rgb = RGBColor(160, 30, 30)

            ap_body = atf.add_paragraph()
            ap_body.text = ans
            ap_body.font.size = Pt(18)
            ap_body.font.color.rgb = RGBColor(30, 30, 30)
            ap_body.space_after = Pt(12)

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
    
    # Student Header Block
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
    
    # Title & Scenario
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"<b>Phase:</b> {phase} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Context:</b> {theme}", styles['Normal']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(scenario, scenario_style))
    elements.append(Spacer(1, 10))
    
    # Questions & Working Boxes
    for idx, q in enumerate(questions, 1):
        elements.append(Paragraph(f"{idx}. {q}", question_style))
        
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
        
    # Extension Box
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
    
    # Teacher Answer Page
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
    d.rectangle([0, 0, 1000, 80], fill=(0, 51, 102))
    d.text((30, 25), f"Task Card: {title}", fill=(255, 255, 255))
    d.rectangle([30, 100, 970, 220], fill=(240, 244, 248), outline=(200, 210, 220))
    d.text((45, 120), scenario[:140] + "..." if len(scenario) > 140 else scenario, fill=(30, 30, 30))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
