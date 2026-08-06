# --- ILLUSTRATED THEME GRAPHICS GENERATOR ---
def create_thematic_banner_image(theme_str):
    # Banner canvas size: 1200 x 200 px
    img = Image.new('RGB', (1200, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    t_lower = theme_str.lower()

    # 🏉 1. RUGBY / SPORTS THEME
    if any(k in t_lower for k in ["sport", "rugby", "netball", "gala"]):
        # Field background (Green gradient effect with field stripes)
        d.rectangle([0, 0, 1200, 200], fill=(34, 139, 34)) # Forest green
        for x in range(0, 1200, 100):
            if (x // 100) % 2 == 0:
                d.rectangle([x, 0, x + 50, 200], fill=(46, 160, 46)) # Field stripes

        # White Field Lines
        d.line([(50, 180), (1150, 180)], fill=(255, 255, 255), width=4) # Try line
        d.line([(50, 20), (1150, 20)], fill=(255, 255, 255), width=2)

        # Draw Rugby Goal Posts (Left Side)
        d.line([(150, 40), (150, 180)], fill=(255, 255, 255), width=5) # Left post
        d.line([(210, 40), (210, 180)], fill=(255, 255, 255), width=5) # Right post
        d.line([(150, 110), (210, 110)], fill=(255, 255, 255), width=4) # Crossbar

        # Draw Rugby Goal Posts (Right Side)
        d.line([(990, 40), (990, 180)], fill=(255, 255, 255), width=5)
        d.line([(1050, 40), (1050, 180)], fill=(255, 255, 255), width=5)
        d.line([(990, 110), (1050, 110)], fill=(255, 255, 255), width=4)

        # Cute Rugby Ball in Center
        d.ellipse([570, 80, 630, 120], fill=(180, 100, 40), outline=(255, 255, 255), width=2)
        d.line([(580, 100), (620, 100)], fill=(255, 255, 255), width=2) # Ball laces

    # ✨ 2. MATARIKI / HĀNGĪ THEME
    elif any(k in t_lower for k in ["hāngī", "hangi", "matariki", "marae"]):
        # Night Sky Gradient Background
        d.rectangle([0, 0, 1200, 200], fill=(15, 23, 42)) # Deep midnight blue

        # Mountain Silhouettes at bottom
        d.polygon([(0, 200), (200, 100), (450, 200)], fill=(30, 41, 59))
        d.polygon([(350, 200), (600, 80), (850, 200)], fill=(20, 30, 45))
        d.polygon([(750, 200), (1000, 110), (1200, 200)], fill=(30, 41, 59))

        # Matariki Seven Stars (Twinkling Yellow Stars)
        star_positions = [(100, 40), (220, 30), (350, 60), (600, 40), (720, 30), (880, 50), (1050, 35)]
        for sx, sy in star_positions:
            d.ellipse([sx-6, sy-6, sx+6, sy+6], fill=(255, 230, 100))
            d.line([(sx-12, sy), (sx+12, sy)], fill=(255, 255, 200), width=2)
            d.line([(sx, sy-12), (sx, sy+12)], fill=(255, 255, 200), width=2)

    # 🌊 3. OCEAN / BEACH / WAKA THEME
    elif any(k in t_lower for k in ["waka", "beach", "marine", "sea", "ocean"]):
        # Ocean Sky & Sea
        d.rectangle([0, 0, 1200, 90], fill=(186, 230, 253))  # Soft sky blue
        d.rectangle([0, 90, 1200, 200], fill=(14, 116, 144)) # Deep ocean blue

        # Waves
        for x in range(0, 1200, 80):
            d.arc([x, 80, x+80, 120], start=0, end=180, fill=(255, 255, 255), width=3)

        # Sun in corner
        d.ellipse([1050, 15, 1130, 95], fill=(253, 224, 71))

    # 🌿 4. DEFAULT NZ BUSH / NATURE THEME
    else:
        d.rectangle([0, 0, 1200, 200], fill=(15, 118, 110)) # Teal green
        # Decorative Fern Leaves / Hill curves
        d.chord([100, 50, 500, 300], start=180, end=360, fill=(20, 184, 166))
        d.chord([700, 20, 1100, 300], start=180, end=360, fill=(13, 148, 136))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
