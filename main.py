import os
import random
import textwrap
import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import google.generativeai as genai

# ---------------- CONFIG ----------------
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CANVAS_SIZE = (1080, 1080)
CAPTION_AREA_Y = 720
FONT_SIZE_TITLE = 48
FONT_SIZE_BODY = 36
FONT_SIZE_FOOTER = 32
FONT_PATH = "fonts/Inter-Regular.ttf"  # ✅ Add this font file to your repo

# ---------------- TOPIC POOL ----------------
TOPIC_POOL = [
    "Benefits of fucking",
    "High protein vegetarian bowls",
    "Fermented foods for gut health",
    "Omega-3 rich seeds and nuts",
    "Colorful plant-based breakfast ideas",
    "Foods that boost brain function",
    "Anti-inflammatory spices",
    "Hydrating fruits for summer",
    "Iron-rich vegetarian meals",
    "Healthy fats for skin glow"
]

def get_random_topic():
    return random.choice(TOPIC_POOL)

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("gemini-2.5-flash")

def generate_image_prompt(topic: str) -> str:
    prompt = (
        f"Create a high-resolution Instagram food photography prompt. Topic: {topic}. "
        "Shot with a Sony A7R V + 90mm macro lens, ultra sharp focus, shallow depth of field. "
        "Editorial overhead flat lay, clean white background, soft natural daylight with long shadows. "
        "Include specific ingredients and textures. No text or logos."
    )
    response = model.generate_content(prompt)
    return (response.text or "").strip()

def generate_nutrition_text(topic: str) -> str:
    text_prompt = (
        "Write Instagram nutrition content for a food image. "
        f"Topic: {topic}. "
        "Format: Title centered, then three bullet points with clear spacing. No spelling errors. Keep it informative and engaging."
    )
    response = model.generate_content(text_prompt)
    return (response.text or "").strip()

# ---------------- STABILITY AI IMAGE GENERATION ----------------
STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"
STABILITY_HEADERS = {
    "Authorization": f"Bearer {os.environ['STABILITY_API_KEY']}",
    "Accept": "application/json"
}

def generate_image(prompt: str, path: str):
    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
        "model": (None, "stable-diffusion-xl-1024-v1-0")
    }

    r = requests.post(STABILITY_URL, headers=STABILITY_HEADERS, files=files, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"Stability AI failed: {r.status_code} {r.text}")

    data = r.json()
    image_base64 = data.get("image") or (data.get("images", [{}])[0].get("base64"))
    if not image_base64:
        raise RuntimeError(f"No image returned: {data}")

    image_bytes = base64.b64decode(image_base64)
    with open(path, "wb") as f:
        f.write(image_bytes)

# ---------------- FORMATTING ----------------
def format_and_overlay(image_path: str, text: str, out_path: str):
    img = Image.open(image_path).convert("RGB").resize(CANVAS_SIZE)
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype(FONT_PATH, FONT_SIZE_TITLE)
    font_body = ImageFont.truetype(FONT_PATH, FONT_SIZE_BODY)
    font_footer = ImageFont.truetype(FONT_PATH, FONT_SIZE_FOOTER)

    lines = text.split("\n")
    title = lines[0].strip()
    bullets = [line.strip("•* ") for line in lines[1:] if line.strip()]

    spacing = 12
    total_height = font_title.getsize(title)[1] + len(bullets) * (font_body.getsize("Test")[1] + spacing) + 60
    start_y = (CANVAS_SIZE[1] - total_height) // 2

    # Title
    draw.text((CANVAS_SIZE[0] // 2, start_y), title, fill="black", anchor="mm", font=font_title)
    y = start_y + font_title.getsize(title)[1] + 30

    # Bullets
    for bullet in bullets:
        draw.text((CANVAS_SIZE[0] // 2, y), f"• {bullet}", fill="black", anchor="mm", font=font_body)
        y += font_body.getsize(bullet)[1] + spacing

    # Footer
    footer_text = "---- alaghverse ----"
    draw.text((CANVAS_SIZE[0] // 2, CANVAS_SIZE[1] - 60), footer_text, fill="black", anchor="mm", font=font_footer)

    img.save(out_path)

# ---------------- PIPELINE ----------------
def run():
    topic = get_random_topic()
    print(f"\n=== Processing: {topic} ===")

    try:
        prompt = generate_image_prompt(topic)
        print("Gemini prompt:\n", prompt)

        caption = generate_nutrition_text(topic)
        print("Gemini caption:\n", caption)

        raw = os.path.join(OUTPUT_DIR, "raw.png")
        final = os.path.join(OUTPUT_DIR, "post.png")

        generate_image(prompt, raw)
        format_and_overlay(raw, caption, final)

        print("Created:", final)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
