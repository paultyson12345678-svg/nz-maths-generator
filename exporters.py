# --- ILLUSTRATED THEME GRAPHICS GENERATOR ---
def create_thematic_banner_image(theme_str):
    # Banner canvas size: 1200 x 200 px
    img = Image.new('RGB', (1200, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    t_lower = theme_str.lower()

    # 🧁 1. BAKE SALE / GALA / FOOD THEME
    if any(k in t_lower for k in ["bake", "cake", "gala", "stall", "food", "fundraiser"]):
        # Soft Pastel Yellow/Pink Background
        d.rectangle([0, 0, 1200, 200], fill=(255, 240, 245)) # Soft Pink

        # Colorful Festive Bunting Triangles across top
        bunting_colors = [(255, 99, 132), (54, 162, 235), (255, 206, 86), (75, 192, 192), (153, 102, 255)]
        d.line([(0, 20), (1200, 20)], fill=(100, 100, 100), width=2)
        for i, x in enumerate(range(0, 1200, 80)):
            color = bunting_colors[i % len(bunting_colors)]
            d.polygon([(x, 20), (x + 80, 20), (x + 40, 70)], fill=color)

        # Draw Cute Cupcake / Cake Icons on Left and Right
        for cx in [120, 1080]:
            # Wrapper
            d.polygon([(cx - 25, 170), (cx + 25, 170), (cx + 20, 130), (cx - 20, 130)], fill=(210, 180, 140))
            # Frosting Top
            d.ellipse([cx - 28, 105, cx + 28, 138], fill=(255, 182, 193))
            # Cherry
            d.ellipse([cx - 6, 95, cx + 6, 107], fill=(220, 20, 60))

    # 🏉 2. RUGBY / SPORTS THEME (Removed 'gala' from here)
    elif any(k in t_lower for k in ["sport", "rugby", "netball", "touch", "athletics"]):
        # Field background (Green gradient effect with field stripes)
        d.rectangle([0, 0, 1200, 200], fill=(34, 139, 34)) # Forest green
        for x in range(0, 1200, 100):
            if (x // 100) % 2 == 0:
                d.rectangle([x, 0, x + 50, 200], fill=(46, 160, 46)) # Field stripes

        # White Field Lines
        d.line([(50, 180), (1150, 180)], fill=(255, 255, 255), width=4)
        d.line([(50, 20), (1150, 20)], fill=(255, 255, 255), width=2)

        # Draw Rugby Goal Posts (Left Side)
        d.line([(150, 30), (150, 180)], fill=(255, 255, 255), width=5)
        d.line([(210, 30), (210, 180)], fill=(255, 255, 255), width=5)
        d.line([(150, 100), (210, 100)], fill=(255, 255, 255), width=4)

        # Draw Rugby Goal Posts (Right Side)
        d.line([(990, 30), (990, 180)], fill=(255, 255, 255), width=5)
        d.line([(1050, 30), (1050, 180)], fill=(255, 255, 255), width=5)
        d.line([(990, 100), (1050, 100)], fill=(255, 255, 255), width=4)

        # Rugby Ball in Center
        d.ellipse([570, 80, 630, 120], fill=(180, 100, 40), outline=(255, 255, 255), width=2)
        d.line([(580, 100), (620, 100)], fill=(255, 255, 255), width=2)

    # ✨ 3. MATARIKI / HĀNGĪ THEME
    elif any(k in t_lower for k in ["hāngī", "hangi", "matariki", "marae"]):
        d.rectangle([0, 0, 1200, 200], fill=(15, 23, 42))

        # Mountain Silhouettes at bottom
        d.polygon([(0, 200), (200, 100), (450, 200)], fill=(30, 41, 59))
        d.polygon([(350, 200), (600, 80), (850, 200)], fill=(20, 30, 45))
        d.polygon([(750, 200), (1000, 110), (1200, 200)], fill=(30, 41, 59))

        # Matariki Seven Stars
        star_positions = [(100, 40), (220, 30), (350, 60), (600, 40), (720, 30), (880, 50), (1050, 35)]
        for sx, sy in star_positions:
            d.ellipse([sx-6, sy-6, sx+6, sy+6], fill=(255, 230, 100))
            d.line([(sx-12, sy), (sx+12, sy)], fill=(255, 255, 200), width=2)
            d.line([(sx, sy-12), (sx, sy+12)], fill=(255, 255, 200), width=2)

    # 🌊 4. OCEAN / BEACH / WAKA THEME
    elif any(k in t_lower for k in ["waka", "beach", "marine", "sea", "ocean"]):
        d.rectangle([0, 0, 1200, 90], fill=(186, 230, 253))
        d.rectangle([0, 90, 1200, 200], fill=(14, 116, 144))

        for x in range(0, 1200, 80):
            d.arc([x, 80, x+80, 120], start=0, end=180, fill=(255, 255, 255), width=3)

        d.ellipse([1050, 15, 1130, 95], fill=(253, 224, 71))

    # 🌿 5. DEFAULT NZ BUSH / NATURE THEME
    else:
        d.rectangle([0, 0, 1200, 200], fill=(15, 118, 110))
        d.chord([100, 50, 500, 300], start=180, end=360, fill=(20, 184, 166))
        d.chord([700, 20, 1100, 300], start=180, end=360, fill=(13, 148, 136))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
