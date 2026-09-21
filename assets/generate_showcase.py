import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_entropy_spoke_visual():
    W, H = 1600, 900
    cx, cy = W // 2, H // 2 + 30
    
    # 1. Base Image with Dark Void
    img = Image.new("RGBA", (W, H), (10, 5, 18, 255))
    
    # Create background nebula glow layer
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    
    # Nebula 1: Center Cyan/Teal glow
    for r in range(450, 0, -10):
        alpha = int(45 * (1 - r / 450))
        glow_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(95, 251, 241, alpha))
        
    # Nebula 2: Off-center Purple glow
    pcx, pcy = cx - 250, cy - 120
    for r in range(500, 0, -15):
        alpha = int(55 * (1 - r / 500))
        glow_draw.ellipse([pcx - r, pcy - r, pcx + r, pcy + r], fill=(157, 92, 255, alpha))
        
    # Nebula 3: Lower Magenta glow
    mcx, mcy = cx + 280, cy + 180
    for r in range(400, 0, -15):
        alpha = int(40 * (1 - r / 400))
        glow_draw.ellipse([mcx - r, mcy - r, mcx + r, mcy + r], fill=(192, 132, 252, alpha))
        
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)
    
    # Fonts
    def get_font(size, bold=False):
        font_names = [
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/CascadiaCode.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]
        for f in font_names:
            if os.path.exists(f):
                try:
                    return ImageFont.truetype(f, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    f_title = get_font(28, bold=True)
    f_sub = get_font(15)
    f_badge = get_font(13, bold=True)
    f_huge = get_font(38, bold=True)
    f_metric = get_font(18, bold=True)
    f_label = get_font(14)
    f_tiny = get_font(12)
    f_token = get_font(16, bold=True)
    f_mono = get_font(13)

    # 2. Concentric Radar Grid Rings
    radii = [90, 160, 230, 310, 390]
    for r in radii:
        # Ring glow
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(157, 92, 255, 60), width=1)
        # Tick marks along outer ring
        if r == 310:
            for deg in range(0, 360, 15):
                rad = math.radians(deg)
                x1 = cx + (r - 6) * math.cos(rad)
                y1 = cy + (r - 6) * math.sin(rad)
                x2 = cx + (r + 6) * math.cos(rad)
                y2 = cy + (r + 6) * math.sin(rad)
                tick_color = (95, 251, 241, 160) if deg % 45 == 0 else (169, 150, 214, 80)
                draw.line([(x1, y1), (x2, y2)], fill=tick_color, width=1)

    # 3. Outer Crosshairs / Degree Indicators
    draw.line([(cx - 430, cy), (cx - 400, cy)], fill=(95, 251, 241, 140), width=1)
    draw.line([(cx + 400, cy), (cx + 430, cy)], fill=(95, 251, 241, 140), width=1)
    draw.line([(cx, cy - 430), (cx, cy - 400)], fill=(95, 251, 241, 140), width=1)
    draw.line([(cx, cy + 400), (cx, cy + 430)], fill=(95, 251, 241, 140), width=1)

    # 4. Spoke Candidates (Simulated Live Token Event)
    # Target Token 1: [CHK-20260920-00042] (Chosen token, low entropy grounded)
    candidates = [
        {"token": "[CHK-20260920-00042]", "prob": 0.942, "angle": -math.pi / 2, "color": (95, 251, 241), "chosen": True, "len": 320},
        {"token": "architecture_audit", "prob": 0.038, "angle": -math.pi / 2 + 1.25, "color": (192, 132, 252), "chosen": False, "len": 150},
        {"token": "hardware_guardrails", "prob": 0.012, "angle": -math.pi / 2 + 2.51, "color": (169, 150, 214), "chosen": False, "len": 110},
        {"token": "canonical_chunk", "prob": 0.005, "angle": -math.pi / 2 + 3.77, "color": (140, 120, 190), "chosen": False, "len": 80},
        {"token": "vulkan_stream", "prob": 0.003, "angle": -math.pi / 2 + 5.02, "color": (110, 90, 160), "chosen": False, "len": 70},
    ]

    # Draw Spokes
    for c in candidates:
        ang = c["angle"]
        slen = c["len"]
        color = c["color"]
        is_chosen = c["chosen"]
        
        sx = cx + slen * math.cos(ang)
        sy = cy + slen * math.sin(ang)
        
        # Spoke ray line with glow
        if is_chosen:
            # Multi-layer glow for chosen spoke
            for gw in [7, 5, 3]:
                alpha = 60 if gw > 3 else 180
                draw.line([(cx, cy), (sx, sy)], fill=color + (alpha,), width=gw)
            draw.line([(cx, cy), (sx, sy)], fill=(255, 255, 255, 255), width=2)
        else:
            draw.line([(cx, cy), (sx, sy)], fill=color + (140,), width=2)
            
        # Endpoint Pod
        pod_r = 9 if is_chosen else 5
        # Pod halo
        draw.ellipse([sx - pod_r - 4, sy - pod_r - 4, sx + pod_r + 4, sy + pod_r + 4], fill=color + (70,))
        draw.ellipse([sx - pod_r, sy - pod_r, sx + pod_r, sy + pod_r], fill=color + (255,))
        if is_chosen:
            draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 255, 255, 255))
            
        # Spoke Tag & Label Box
        offset_d = 28 if is_chosen else 18
        tx = sx + offset_d * math.cos(ang)
        ty = sy + offset_d * math.sin(ang)
        
        label_text = f"{c['token']}  ({c['prob']*100:.1f}%)"
        
        # Calculate text bounding box
        bbox = draw.textbbox((0, 0), label_text, font=f_token if is_chosen else f_label)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        # Align tag based on angle
        if math.cos(ang) > 0.3:
            box_x0 = tx
            box_x1 = tx + tw + 18
        elif math.cos(ang) < -0.3:
            box_x0 = tx - tw - 18
            box_x1 = tx
        else:
            box_x0 = tx - tw // 2 - 10
            box_x1 = tx + tw // 2 + 10
            
        if math.sin(ang) > 0.3:
            box_y0 = ty
            box_y1 = ty + th + 12
        else:
            box_y0 = ty - th - 12
            box_y1 = ty
            
        # Tag background pod
        bg_col = (20, 10, 36, 230) if not is_chosen else (15, 30, 45, 245)
        border_col = color + ((220 if is_chosen else 130),)
        draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=5, fill=bg_col, outline=border_col, width=1)
        
        # Text inside tag
        text_x = box_x0 + 9
        text_y = box_y0 + 5
        text_col = (255, 255, 255) if is_chosen else (216, 198, 255)
        draw.text((text_x, text_y), label_text, font=f_token if is_chosen else f_label, fill=text_col)

    # 5. Central Hub (Entropy Core)
    core_r = 78
    # Outer core pulsing glow
    for cr in range(core_r + 20, core_r, -2):
        alpha = int(90 * (1 - (cr - core_r) / 20))
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], outline=(95, 251, 241, alpha), width=2)
        
    # Core body
    draw.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r], fill=(12, 6, 24, 250), outline=(95, 251, 241, 255), width=2)
    
    # Inner telemetry text
    draw.text((cx, cy - 38), "SHANNON ENTROPY", font=f_tiny, fill=(169, 150, 214), anchor="mm")
    draw.text((cx, cy - 14), "0.342 BITS", font=f_metric, fill=(95, 251, 241), anchor="mm")
    
    # Divider line
    draw.line([(cx - 45, cy), (cx + 45, cy)], fill=(95, 251, 241, 100), width=1)
    
    draw.text((cx, cy + 14), "GROUNDED CERTAINTY", font=f_tiny, fill=(95, 251, 241), anchor="mm")
    draw.text((cx, cy + 34), "GATE: < 0.60 PASS", font=f_mono, fill=(192, 132, 252), anchor="mm")

    # 6. Orbiting Bioluminescent Particles
    particles = [
        (160, 0.45, (95, 251, 241)), (160, 1.82, (192, 132, 252)), (160, 3.4, (95, 251, 241)), (160, 5.1, (169, 150, 214)),
        (230, 0.9, (192, 132, 252)), (230, 2.7, (95, 251, 241)), (230, 4.2, (192, 132, 252)),
        (310, 1.3, (95, 251, 241)), (310, 3.9, (192, 132, 252)), (310, 5.8, (95, 251, 241))
    ]
    for pr, pang, pcol in particles:
        px = cx + pr * math.cos(pang)
        py = cy + pr * math.sin(pang)
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=pcol + (60,))
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255, 220))

    # 7. Header HUD Bar
    hud_y = 35
    draw.line([(50, hud_y + 65), (W - 50, hud_y + 65)], fill=(157, 92, 255, 70), width=1)
    draw.text((50, hud_y), "CRITICAL RAG FRAMEWORK  //  LIVE ENTROPY SPOKE ENGINE", font=f_title, fill=(237, 230, 255))
    draw.text((50, hud_y + 36), "Deterministic Corpus Grounding • Top-5 Epistemic Drift Analysis • Vulkan RT Local Hardware Execution", font=f_sub, fill=(169, 150, 214))

    # Header Status Badges (Right side)
    badges = [
        ("CONTAINER ENCLAVE", (95, 251, 241)),
        ("VULKAN 100% OFF-CHIP", (192, 132, 252)),
        ("NEMOTRON-4B", (95, 251, 241)),
        ("SYSTEM ONLINE", (95, 251, 241))
    ]
    bx = W - 50
    for btext, bcol in reversed(badges):
        bbox = draw.textbbox((0, 0), btext, font=f_badge)
        bw = bbox[2] - bbox[0] + 18
        bh = 26
        bx0 = bx - bw
        bx1 = bx
        by0 = hud_y + 12
        by1 = by0 + bh
        draw.rounded_rectangle([bx0, by0, bx1, by1], radius=4, fill=(25, 12, 45, 200), outline=bcol + (180,), width=1)
        draw.text((bx0 + 9, by0 + 5), btext, font=f_badge, fill=bcol)
        bx = bx0 - 12

    # 8. Bottom Telemetry Panels (Alien Cut-Corner Glass Panels)
    bot_y = H - 110
    panel_h = 75
    
    # 3 Bottom Cards
    cards = [
        {
            "x0": 50, "x1": 510,
            "title": "EPISTEMIC GATE TELEMETRY",
            "stat": "PASS (H = 0.342 < 0.60 bits)",
            "sub": "Hallucination Risk: 0.00% • Top-1 Confidence: 94.20%",
            "accent": (95, 251, 241)
        },
        {
            "x0": 545, "x1": 1055,
            "title": "CANONICAL CITATION GROUNDING",
            "stat": "[CHK-20260920-00042] VERIFIED",
            "sub": "DOC-architecture-audit-v1 • 100% Corpus Alignment",
            "accent": (192, 132, 252)
        },
        {
            "x0": 1090, "x1": W - 50,
            "title": "DISTRIBUTED CLUSTER HARDWARE",
            "stat": "PORT 8080 VULKAN // PORT 8090 HARNESS",
            "sub": "Latency: 14.8 ms/tok • Memory: 4.8 GB VRAM Bound",
            "accent": (95, 251, 241)
        }
    ]
    
    for c in cards:
        x0, x1 = c["x0"], c["x1"]
        y0, y1 = bot_y, bot_y + panel_h
        # Draw cut corner panel
        cut = 12
        pts = [
            (x0 + cut, y0), (x1, y0), (x1, y1 - cut),
            (x1 - cut, y1), (x0, y1), (x0, y0 + cut)
        ]
        draw.polygon(pts, fill=(22, 12, 40, 220), outline=(157, 92, 255, 90))
        # Accent left pip
        draw.line([(x0, y0 + cut), (x0, y1)], fill=c["accent"] + (255,), width=3)
        
        draw.text((x0 + 16, y0 + 10), c["title"], font=f_tiny, fill=(169, 150, 214))
        draw.text((x0 + 16, y0 + 26), c["stat"], font=f_token, fill=c["accent"])
        draw.text((x0 + 16, y0 + 49), c["sub"], font=f_mono, fill=(216, 198, 255))

    # Outer Frame Border
    draw.rectangle([10, 10, W - 10, H - 10], outline=(157, 92, 255, 45), width=1)
    # Corner Accents
    c_len = 25
    for cx_c, cy_c, dx, dy in [(10, 10, 1, 1), (W - 10, 10, -1, 1), (10, H - 10, 1, -1), (W - 10, H - 10, -1, -1)]:
        draw.line([(cx_c, cy_c), (cx_c + dx * c_len, cy_c)], fill=(95, 251, 241, 220), width=2)
        draw.line([(cx_c, cy_c), (cx_c, cy_c + dy * c_len)], fill=(95, 251, 241, 220), width=2)

    # Save Output
    out_png = "./assets/entropy_spoke_graph.png"
    img.save(out_png, "PNG", quality=100)
    print(f"Generated showcase snapshot: {out_png}")

if __name__ == "__main__":
    create_entropy_spoke_visual()
