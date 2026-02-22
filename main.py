"""
TRADEVERSE Instagram Bot — Dynamic Randomization Engine v3
===========================================================
Reference aesthetic: Warm amber LED-lit trading room, ultra-wide curved monitor,
glossy desk reflections, dark wood walls, leather chair, cinematic moody atmosphere.

Every run is 100% unique:
  • AI creative brief generated fresh each run (seed + time entropy)
  • Background: 12 scene types × 6 lighting moods × 4 camera angles = 288+ combos
  • Content: 8 post formats, all pure trading wisdom — no coin-specific content
  • Layout: 5 text positions × 6 accent styles × dynamic font sizing
  • Only TRADEVERSE brand stays fixed (gold, bottom center)
"""

import os, base64, datetime, hashlib, json, random, requests, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import google.generativeai as genai

# ─────────────────────── CONSTANTS ───────────────────────
OUTPUT_DIR     = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H           = 1080, 1080
BRAND          = "TRADEVERSE"
BRAND_SUB      = "PROFESSIONAL TRADING"
GOLD           = (212, 175, 55)
GOLD_DARK      = (160, 128, 35)
GOLD_LIGHT     = (240, 210, 100)
WHITE          = (255, 255, 255)
CREAM          = (235, 228, 210)
BLACK          = (0, 0, 0)
AMBER          = (255, 180, 60)

# ─────────────────────── GEMINI ───────────────────────
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
_model = genai.GenerativeModel("gemini-2.5-flash")

def ai(prompt, fallback=""):
    try:
        r = _model.generate_content(prompt)
        return (r.text or "").strip()
    except Exception as e:
        print(f"  ⚠ Gemini: {e}")
        return fallback

# ═══════════════════════════════════════════════════
# 1. AI CREATIVE BRIEF — the brain of every post
# ═══════════════════════════════════════════════════

def make_brief(seed: int) -> dict:
    """
    Gemini invents every creative decision for this post.
    Seed + time ensures true uniqueness across runs.
    """
    now = datetime.datetime.utcnow()
    prompt = f"""You are creative director of TRADEVERSE — a premium trading lifestyle Instagram page.
Design a unique Instagram post. Be wildly creative and specific.

Run seed: {seed} | UTC: {now.strftime("%H:%M %A %d %b")}

Return ONLY valid JSON, no markdown:

{{
  "scene_type": "one of: amber_led_trading_room, rooftop_city_desk, glass_tower_floor, brutalist_concrete_setup, library_wood_paneling, japanese_minimal_studio, neon_underground_lab, mountain_cabin_setup, yacht_deck_trading, airport_lounge_screen, rainy_penthouse_desk, dark_forest_glass_cabin",
  "lighting": "one of: warm_amber_led, cool_blue_dawn, golden_hour_sun, neon_glow_night, stark_white_studio, stormy_grey",
  "camera": "one of: behind_elevated_wide, behind_low_dramatic, side_profile_45, tight_over_shoulder, aerial_topdown_desk",
  "mood": "one of: cinematic_dark, warm_intimate, cold_clinical, dramatic_storm, serene_focused",
  "post_format": "one of: power_quote, trading_rule, mindset_principle, market_truth, discipline_lesson, pattern_insight, psychology_fact, risk_wisdom",
  "content_energy": "one of: calm_wise, bold_aggressive, philosophical_deep, urgent_sharp, poetic_reflective",
  "headline_form": "one of: single_statement, two_part_contrast, rhetorical_question, numbered_rule, metaphor",
  "layout_style": "one of: centered_dramatic, bottom_heavy, top_anchored, split_horizontal, diagonal_flow",
  "accent": "one of: gold_lines, diamond_dots, bracket_frame, minimal_rule, corner_marks, no_accent",
  "specific_theme": "be very specific — e.g. 'the psychology of cutting losses before they grow', 'why most traders fail at the open', 'patience as a trading strategy', 'reading price action not news'",
  "value_hook": "specific insight or lesson that will make a trader stop scrolling, e.g. '90% of trading success is what you do NOT trade'"
}}"""

    raw = ai(prompt).replace("```json","").replace("```","").strip()
    try:
        b = json.loads(raw)
        needed = ["scene_type","lighting","camera","mood","post_format","content_energy",
                  "headline_form","layout_style","accent","specific_theme","value_hook"]
        for k in needed:
            if k not in b: raise ValueError(f"missing {k}")
        print(f"  ✓ Brief → {b['post_format']} | {b['content_energy']} | {b['scene_type']} | {b['lighting']}")
        return b
    except Exception as e:
        print(f"  ⚠ Brief fallback ({e})")
        # Full random fallback
        return {
            "scene_type": random.choice(["amber_led_trading_room","glass_tower_floor","rooftop_city_desk","neon_underground_lab","library_wood_paneling","japanese_minimal_studio"]),
            "lighting": random.choice(["warm_amber_led","cool_blue_dawn","golden_hour_sun","neon_glow_night","stark_white_studio"]),
            "camera": random.choice(["behind_elevated_wide","behind_low_dramatic","side_profile_45","tight_over_shoulder"]),
            "mood": random.choice(["cinematic_dark","warm_intimate","cold_clinical","dramatic_storm","serene_focused"]),
            "post_format": random.choice(["power_quote","trading_rule","mindset_principle","market_truth","discipline_lesson"]),
            "content_energy": random.choice(["calm_wise","bold_aggressive","philosophical_deep","urgent_sharp","poetic_reflective"]),
            "headline_form": random.choice(["single_statement","two_part_contrast","rhetorical_question","numbered_rule","metaphor"]),
            "layout_style": random.choice(["centered_dramatic","bottom_heavy","top_anchored","split_horizontal"]),
            "accent": random.choice(["gold_lines","diamond_dots","bracket_frame","minimal_rule","corner_marks"]),
            "specific_theme": random.choice(["the psychology of cutting losses early","patience as a trading edge","why discipline beats intelligence in markets","reading charts not headlines"]),
            "value_hook": random.choice(["Most traders lose not from bad analysis but from good analysis executed badly","The market rewards those who wait for confirmation not those who act on prediction"])
        }

# ═══════════════════════════════════════════════════
# 2. BACKGROUND IMAGE PROMPT — cinematic trading rooms
# ═══════════════════════════════════════════════════

SCENES = {
    "amber_led_trading_room":    "professional trading desk setup, warm amber orange LED strip lighting along ceiling edge, ultra-wide curved monitor plus two vertical side monitors displaying trading charts, glossy dark wood desk with reflections of screens, leather executive chair, dark wood panel walls, warm moody glow, cables hidden, premium setup",
    "rooftop_city_desk":         "minimal trading desk on luxury penthouse rooftop terrace, glass railing, city skyline panorama, sunset or night city lights, open air premium setup, cable-managed screens showing charts",
    "glass_tower_floor":         "trading workstation inside glass skyscraper floor, full floor-to-ceiling windows behind, city 200 floors below, clean white marble desk, ultrawide monitors, reflections in glass",
    "brutalist_concrete_setup":  "industrial brutalist concrete space, raw concrete walls and ceiling, single dramatic spotlight, professional trading monitors on raw steel desk, very moody dark cinematic",
    "library_wood_paneling":     "home trading office inside dark walnut wood-paneled library, leather chairs, bookshelves visible, warm reading lamp, ultrawide monitor glowing amber among book spines",
    "japanese_minimal_studio":   "Japanese minimalist trading studio, shoji paper screens, tatami-inspired low desk, clean uncluttered monitors, soft diffused daylight, zen garden visible through window",
    "neon_underground_lab":      "underground trading bunker, dark concrete, electric blue and purple neon strips, multiple monitors stacked, dramatic industrial aesthetic, cables and hardware visible",
    "mountain_cabin_setup":      "luxury mountain cabin trading setup, floor-to-ceiling windows with snow-capped peaks, pine wood interior, warm fireplace glow, clean desk with monitors facing the mountains",
    "yacht_deck_trading":        "luxury superyacht deck trading setup, open ocean horizon, salt air feel, teak deck, monitors in custom marine console, blue water stretching behind",
    "airport_lounge_screen":     "premium airport private lounge, large curved screen on desk, city runway visible through floor-length glass, hushed luxury, leather seat, muted lighting",
    "rainy_penthouse_desk":      "penthouse trading desk, heavy rain on panoramic windows, city lights blurred through water drops, dramatic moody atmosphere, single desk lamp, glowing screens",
    "dark_forest_glass_cabin":   "glass-wall cabin deep in forest, trees pressing against glass, monitors glowing inside, dark green forest ambient, early morning mist, ultra cinematic",
}

LIGHTING_DESC = {
    "warm_amber_led":    "warm amber orange LED accent lighting, golden glow, deep shadows, cozy yet powerful atmosphere",
    "cool_blue_dawn":    "cold blue pre-dawn light, icy white monitor glow, before-sunrise stillness",
    "golden_hour_sun":   "golden hour side lighting, long shadows, warm honey sunlight streaming in",
    "neon_glow_night":   "neon accent lights, electric color reflections, dark night atmosphere",
    "stark_white_studio":"bright white diffused studio lighting, clean clinical, high key exposure",
    "stormy_grey":       "overcast stormy light, grey dramatic sky, high contrast moody atmosphere",
}

CAMERA_DESC = {
    "behind_elevated_wide":  "wide angle shot from behind and above the person, full scene visible, environmental storytelling",
    "behind_low_dramatic":   "low angle from behind, person silhouette powerful, screens tower above, cinematic",
    "side_profile_45":       "45-degree side angle, person in profile, desk and monitors visible, editorial",
    "tight_over_shoulder":   "tight over-shoulder shot, screens fill frame, intimate focused feel",
    "aerial_topdown_desk":   "aerial top-down view of desk and screens, flat lay cinematic, no person visible",
}

MOOD_GRADE = {
    "cinematic_dark":  "cinematic color grade, deep blacks, teal shadows, rich contrast, film look",
    "warm_intimate":   "warm amber color grade, honey tones, soft vignette, intimate",
    "cold_clinical":   "cold clinical grade, desaturated blues, sharp clean, analytical",
    "dramatic_storm":  "dramatic high-contrast grade, near-monochrome, stormy tension",
    "serene_focused":  "soft natural grade, balanced exposure, peaceful focus",
}

def make_image_prompt(brief: dict) -> str:
    scene   = SCENES.get(brief["scene_type"], SCENES["amber_led_trading_room"])
    light   = LIGHTING_DESC.get(brief["lighting"], "dramatic moody lighting")
    camera  = CAMERA_DESC.get(brief["camera"], "behind elevated wide angle")
    grade   = MOOD_GRADE.get(brief["mood"], "cinematic color grade")

    raw = (
        f"Professional trader at desk, {camera}, {scene}, "
        f"{light}, {grade}, "
        f"charts and trading data on monitors, no text overlays, no logos, "
        f"photorealistic DSLR photography, 8K ultra sharp, "
        f"no watermarks, pure background composition"
    )

    refined = ai(
        f"Compress into one Stability AI image prompt under 380 chars. "
        f"Keep: camera position, trading desk scene, lighting mood, photorealistic. "
        f"Output ONLY the prompt:\n{raw}",
        fallback=raw
    ).strip().strip('"').strip("'")

    return refined[:380] if len(refined) > 40 else raw[:380]

# ═══════════════════════════════════════════════════
# 3. POST CONTENT — pure trading wisdom, always unique
# ═══════════════════════════════════════════════════

FORMAT_GUIDE = {
    "power_quote":        "A single unforgettable quote that distills trading wisdom. No explanation needed — the words must hit hard.",
    "trading_rule":       "An ironclad rule that every serious trader follows. State it like law. Subtext explains the cost of breaking it.",
    "mindset_principle":  "A psychological principle that separates elite traders from the rest. Go deep into the mental game.",
    "market_truth":       "A hard truth about how markets actually work. Counterintuitive. Makes you think differently.",
    "discipline_lesson":  "A lesson about discipline that traders learn the hard way. Specific. Painful. True.",
    "pattern_insight":    "An insight about patterns in trading — not technical patterns, but behavioral and psychological ones.",
    "psychology_fact":    "A surprising fact about trader psychology. Data-driven feel. Eye-opening.",
    "risk_wisdom":        "Deep wisdom about risk — how to think about it, respect it, and use it as an edge.",
}

ENERGY_GUIDE = {
    "calm_wise":          "Speak like a seasoned veteran who has seen everything. Unhurried. Certain.",
    "bold_aggressive":    "Direct. No softening. Every word earns its place. Punches hard.",
    "philosophical_deep": "Contemplative. References the human condition. Trading as metaphor for life.",
    "urgent_sharp":       "Urgent warning energy. Like a mentor stopping you before you make a mistake.",
    "poetic_reflective":  "Slightly poetic. Uses imagery. Still about trading but with a literary quality.",
}

FORM_GUIDE = {
    "single_statement":   "One sentence. Complete. Powerful. Stands alone.",
    "two_part_contrast":  "Two halves in contrast: 'X does Y. Z does W.' The contrast creates the tension.",
    "rhetorical_question":"Starts with a question the reader is already asking. Then answers it sharply.",
    "numbered_rule":      "Phrased as a rule number: 'Rule: ...' or 'The first law of...'",
    "metaphor":           "Trading concept through a real-world metaphor. Unexpected but perfect fit.",
}

def make_content(brief: dict) -> dict:
    prompt = f"""You are the voice of TRADEVERSE — a premium trading wisdom page.
Write one Instagram post based on this brief.

Post format: {brief['post_format']} — {FORMAT_GUIDE.get(brief['post_format'], '')}
Content energy: {brief['content_energy']} — {ENERGY_GUIDE.get(brief['content_energy'], '')}
Headline form: {brief['headline_form']} — {FORM_GUIDE.get(brief['headline_form'], '')}
Specific theme: {brief['specific_theme']}
Value hook to deliver: {brief['value_hook']}

STRICT FORMAT — output ONLY these lines, nothing else:
HEADLINE: [the headline — max 8 words, follows the headline_form exactly]
LINE1: [first supporting line — max 13 words, deepens the headline]
LINE2: [second supporting line — max 13 words, lands the insight or flips perspective]
CAPTION: [Instagram caption — 2-4 sentences that feel like a mentor talking, specific and real, ends with 5 powerful hashtags]

RULES:
- Zero clichés: no "journey", "grind", "hustle", "to the moon", "WAGMI"
- No coin names, no specific markets, no price predictions  
- Must feel like it was written by a 20-year trading veteran
- HEADLINE must stop the scroll — it should feel almost too true
- Make LINE1 and LINE2 feel like hard-won wisdom, not motivation poster text
- CAPTION must add information not just repeat the headline"""

    raw = ai(prompt)
    result = {"headline": "", "line1": "", "line2": "", "caption": ""}
    for ln in raw.split("\n"):
        ln = ln.strip()
        if   ln.startswith("HEADLINE:"): result["headline"] = ln[9:].strip().strip('"')
        elif ln.startswith("LINE1:"):    result["line1"]    = ln[6:].strip().strip('"')
        elif ln.startswith("LINE2:"):    result["line2"]    = ln[6:].strip().strip('"')
        elif ln.startswith("CAPTION:"):  result["caption"]  = ln[8:].strip()

    # Fallbacks
    theme = brief.get("specific_theme", "discipline")
    hook  = brief.get("value_hook", "Patience is a position.")
    result["headline"] = result["headline"] or hook[:60]
    result["line1"]    = result["line1"]    or f"Most traders understand {theme} in theory."
    result["line2"]    = result["line2"]    or "The market charges tuition for the rest."
    result["caption"]  = result["caption"]  or f"{hook} The edge is not in the analysis — it is in the execution. #Tradeverse #TradingMindset #TradingPsychology #MarketWisdom #ProfessionalTrading"
    return result

# ═══════════════════════════════════════════════════
# 4. STABILITY AI
# ═══════════════════════════════════════════════════

def gen_image(prompt: str, path: str):
    headers = {"Authorization": f"Bearer {os.environ['STABILITY_API_KEY']}", "Accept": "application/json"}
    files   = {"prompt": (None, prompt), "output_format": (None, "png"), "aspect_ratio": (None, "1:1")}
    r = requests.post("https://api.stability.ai/v2beta/stable-image/generate/core",
                      headers=headers, files=files, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"Stability AI {r.status_code}: {r.text[:300]}")
    data = r.json()
    b64  = data.get("image") or (data.get("images",[{}])[0].get("base64",""))
    if not b64: raise RuntimeError(f"No image: {data}")
    with open(path, "wb") as f: f.write(base64.b64decode(b64))
    print(f"  ✓ BG saved: {path}")

# ═══════════════════════════════════════════════════
# 5. FONTS
# ═══════════════════════════════════════════════════

def font(size: int, bold=False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"        if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"          if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

# ═══════════════════════════════════════════════════
# 6. DRAW UTILITIES
# ═══════════════════════════════════════════════════

def tw(draw, text, f): 
    b = draw.textbbox((0,0), text, font=f); return b[2]-b[0]

def th(draw, text, f): 
    b = draw.textbbox((0,0), text, font=f); return b[3]-b[1]

def draw_c(draw, text, y, f, fill=WHITE, shadow=BLACK, off=3):
    """Draw horizontally centered text with shadow."""
    w = tw(draw, text, f)
    x = (W - w) // 2
    draw.text((x+off, y+off), text, font=f, fill=shadow)
    draw.text((x, y),         text, font=f, fill=fill)
    return th(draw, text, f)

def wrap(text: str, chars: int) -> list:
    return textwrap.wrap(text, width=chars)

def auto_wrap_font(draw, text: str, max_w: int, max_chars_start=18) -> tuple:
    """Auto-size headline: shrink font until it fits."""
    for size in [80, 72, 64, 56, 48]:
        f = font(size, bold=True)
        lines = wrap(text, max_chars_start)
        fits = all(tw(draw, line, f) <= max_w for line in lines)
        if fits: return f, lines, size
    # final fallback
    f = font(44, bold=True)
    return f, wrap(text, 24), 44

# ═══════════════════════════════════════════════════
# 7. ACCENT DRAWING — varies every post
# ═══════════════════════════════════════════════════

def draw_accent_element(draw, style: str, y: int) -> int:
    """Draw the decorative separator. Returns height consumed."""
    cx = W // 2
    g  = GOLD

    if style == "gold_lines":
        draw.line([(cx-180, y+6), (cx-40, y+6)], fill=(*g,230), width=2)
        draw.line([(cx+40,  y+6), (cx+180, y+6)], fill=(*g,230), width=2)
        # center gem
        draw.rectangle([(cx-6, y+2), (cx+6, y+10)], fill=g)
        return 20

    elif style == "diamond_dots":
        for i, dx in enumerate([-60,-30,0,30,60]):
            alpha = 255 if i == 2 else (180 if abs(i-2)==1 else 100)
            sz = 8 if i == 2 else (5 if abs(i-2)==1 else 3)
            draw.polygon([(cx+dx, y), (cx+dx+sz, y+sz), (cx+dx, y+sz*2), (cx+dx-sz, y+sz)], fill=(*g, alpha))
        return 22

    elif style == "bracket_frame":
        # [  content  ]
        bl, br = cx-200, cx+200
        draw.line([(bl, y+3), (bl+30, y+3)],   fill=g, width=2)
        draw.line([(bl, y+3), (bl, y+16)],      fill=g, width=2)
        draw.line([(br-30, y+3), (br, y+3)],   fill=g, width=2)
        draw.line([(br, y+3), (br, y+16)],      fill=g, width=2)
        return 22

    elif style == "minimal_rule":
        draw.line([(cx-220, y+5), (cx+220, y+5)], fill=(*g, 180), width=1)
        return 14

    elif style == "corner_marks":
        # Four corner ticks pointing inward
        for sx, sy, dx, dy in [(-200,-2,1,1),(-200,14,1,-1),(200,-2,-1,1),(200,14,-1,-1)]:
            draw.line([(cx+sx,y+sy+8),(cx+sx+dx*16,y+sy+8)], fill=g, width=2)
            draw.line([(cx+sx,y+sy+8),(cx+sx,y+sy+dy*12)],    fill=g, width=2)
        return 18

    else:  # no_accent
        return 10

# ═══════════════════════════════════════════════════
# 8. DYNAMIC OVERLAY — mood-driven gradients
# ═══════════════════════════════════════════════════

def build_overlay(mood: str, lighting: str) -> Image.Image:
    """Build the gradient overlay that makes text readable while preserving BG atmosphere."""
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)

    # Base gradient strength by mood
    strength = {"cinematic_dark":210,"warm_intimate":180,"cold_clinical":195,"dramatic_storm":225,"serene_focused":170}.get(mood, 195)

    # Top soft vignette
    for i in range(90):
        od.line([(0,i),(W,i)], fill=(0,0,0,int(70*(1-i/90))))

    # Main gradient (bottom-heavy so BG shows in upper portion)
    for i in range(H):
        a = int(strength * ((i/H)**1.5))
        od.line([(0,i),(W,i)], fill=(0,0,0,a))

    # Mood-specific color tint layer
    tints = {
        "warm_intimate":  (40, 20, 0,  20),
        "cold_clinical":  (0,  10, 30, 15),
        "dramatic_storm": (10, 5,  20, 25),
    }
    if mood in tints:
        r2,g2,b2,ta = tints[mood]
        tint = Image.new("RGBA", (W, H), (r2,g2,b2,0))
        td = ImageDraw.Draw(tint)
        for i in range(H):
            a = int(ta * ((i/H)**0.8))
            td.line([(0,i),(W,i)], fill=(r2,g2,b2,a))
        overlay = Image.alpha_composite(overlay, tint)

    return overlay

# ═══════════════════════════════════════════════════
# 9. COMPOSE — dynamic layout engine
# ═══════════════════════════════════════════════════

def compose(bg_path: str, content: dict, brief: dict, out_path: str):
    img = Image.open(bg_path).convert("RGBA").resize((W,H), Image.LANCZOS)

    # Apply overlay
    overlay = build_overlay(brief["mood"], brief["lighting"])
    img     = Image.alpha_composite(img, overlay)

    # Gold thin line above brand zone
    al = Image.new("RGBA",(W,H),(0,0,0,0))
    ald = ImageDraw.Draw(al)
    ald.line([(50, H-305),(W-50, H-305)], fill=(*GOLD,120), width=1)
    img = Image.alpha_composite(img, al)

    draw = ImageDraw.Draw(img)

    # ── Determine text block Y based on layout ──
    layout = brief.get("layout_style","centered_dramatic")
    if   layout == "bottom_heavy":      base_y = H - 620
    elif layout == "top_anchored":      base_y = 80
    elif layout == "split_horizontal":  base_y = H//2 - 240
    elif layout == "diagonal_flow":     base_y = H//4
    else:                               base_y = H//2 - 210  # centered_dramatic

    # ── HEADLINE — auto-sized ──
    headline_raw = content["headline"].upper()
    f_hl, hl_lines, hl_size = auto_wrap_font(draw, headline_raw, W-120, max_chars_start=18)

    # Subtle text glow (draw slightly blurred white underneath)
    glow_layer = Image.new("RGBA",(W,H),(0,0,0,0))
    gd = ImageDraw.Draw(glow_layer)
    y = base_y
    for line in hl_lines:
        lw = tw(gd, line, f_hl)
        lx = (W-lw)//2
        gd.text((lx, y), line, font=f_hl, fill=(255,255,255,60))
        y += hl_size + 10
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=8))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)

    # Draw headline
    y = base_y
    for line in hl_lines:
        draw_c(draw, line, y, f_hl, fill=WHITE, shadow=BLACK, off=4)
        y += hl_size + 12

    # ── Accent separator ──
    y += 16
    accent_h = draw_accent_element(draw, brief.get("accent","gold_lines"), y)
    y += accent_h + 14

    # ── LINE 1 ──
    f_sub = font(38)
    line1 = content.get("line1","")
    if line1:
        for sub in wrap(line1, 46):
            draw_c(draw, sub, y, f_sub, fill=CREAM, shadow=BLACK, off=2)
            y += 48

    y += 8

    # ── LINE 2 — slightly dimmer, italic feel via smaller font ──
    f_sub2 = font(34)
    line2 = content.get("line2","")
    if line2:
        for sub in wrap(line2, 50):
            draw_c(draw, sub, y, f_sub2, fill=(*CREAM[:3], 200), shadow=BLACK, off=2)
            y += 44

    # ── BRAND ZONE — always fixed, always gold ──
    # Thin gold line
    brand_y  = H - 200
    f_brand  = font(52, bold=True)
    f_bsub   = font(24)

    draw_c(draw, BRAND,     brand_y,    f_brand, fill=GOLD,      shadow=BLACK, off=3)
    draw_c(draw, BRAND_SUB, brand_y+64, f_bsub,  fill=GOLD_DARK, shadow=BLACK, off=2)

    img.convert("RGB").save(out_path, "PNG", quality=95)
    print(f"  ✓ Composed: {out_path}")

# ═══════════════════════════════════════════════════
# 10. MAIN PIPELINE
# ═══════════════════════════════════════════════════

def make_seed() -> int:
    ts      = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    entropy = str(random.randint(100000,999999))
    return int(hashlib.sha256((ts+entropy).encode()).hexdigest()[:10], 16) % (10**9)

def slot() -> int:
    return int(os.environ.get("POST_SLOT","0")) % 3

def run():
    s    = slot()
    seed = make_seed()
    ts   = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    bg_path    = os.path.join(OUTPUT_DIR, f"bg_{ts}.png")
    post_path  = os.path.join(OUTPUT_DIR, f"post_{ts}_s{s}.png")
    cap_path   = os.path.join(OUTPUT_DIR, f"caption_{ts}_s{s}.txt")
    brief_path = os.path.join(OUTPUT_DIR, f"brief_{ts}_s{s}.json")

    print(f"\n{'═'*54}")
    print(f"  TRADEVERSE  ·  Slot {s}  ·  Seed {seed}")
    print(f"{'═'*54}\n")

    # 1 — Creative brief
    print("  🧠  Generating creative brief...")
    brief = make_brief(seed)
    with open(brief_path,"w") as f: json.dump(brief, f, indent=2)

    # 2 — Image prompt
    print(f"  🎨  Building image prompt ({brief['scene_type']})...")
    img_prompt = make_image_prompt(brief)
    print(f"  → {img_prompt[:90]}...")

    # 3 — Generate background
    print(f"  🖼   Generating background (Stability AI)...")
    gen_image(img_prompt, bg_path)

    # 4 — Generate content
    print(f"  ✍   Writing content ({brief['post_format']} · {brief['content_energy']})...")
    content = make_content(brief)
    print(f"  HL  : {content['headline']}")
    print(f"  L1  : {content['line1']}")
    print(f"  L2  : {content['line2']}")

    # 5 — Compose post
    print(f"  🖼   Composing (layout:{brief['layout_style']} accent:{brief['accent']})...")
    compose(bg_path, content, brief, post_path)

    # 6 — Caption
    with open(cap_path,"w") as f: f.write(content["caption"])
    print(f"  ✓   Caption → {cap_path}")

    print(f"\n  ✅  DONE → {post_path}")
    print(f"{'═'*54}\n")

if __name__ == "__main__":
    run()
