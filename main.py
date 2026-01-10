# Install dependencies
!pip install -q google-generativeai pillow requests

import os, io, time, textwrap, requests, base64, random
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai

# 🔑 Set your keys here
GEMINI_API_KEY = "your_gemini_key_here"
STABILITY_API_KEY = "your_stability_key_here"

# 🔧 Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# 🔧 Stability setup
STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"
STABILITY_HEADERS = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Accept": "application/json"
}

# 🔁 Topic pool
TOPIC_POOL = [
    "Benefits of soaked almonds",
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

# 🧠 Gemini prompt + caption
topic = get_random_topic()
print("🎯 Topic:", topic)

prompt = model.generate_content(
    f"Create a high-resolution Instagram food photography prompt. Topic: {topic}. "
    "Style: 4K camera, ultra focus, editorial composition, natural shadows, clean white background, overhead flat lay. "
    "Include specific ingredients and visual textures. No text or logos in image."
).text.strip()

caption = model.generate_content(
    f"Write Instagram nutrition content for a food image. Topic: {topic}. "
    "Format: Title centered, then three bullet points with clear spacing. No spelling errors. Keep it informative and engaging."
).text.strip()

print("\n📸 Prompt:\n", prompt)
print("\n📝 Caption:\n", caption)

# 🖼️ Generate image from Stability
def generate_image(prompt):
    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
        "model": (None, "stable-diffusion-xl-1024-v1-0")
    }
    r = requests.post(STABILITY_URL, headers=STABILITY_HEADERS, files=files, timeout=120)
    data = r.json()
    image_base64 = data.get("image") or (data.get("images", [{}])[0].get("base64"))
    if not image_base64:
        raise RuntimeError(f"No image returned: {data}")
    return base64.b64decode(image_base64)

image_bytes = generate_image(prompt)

# 🖍️ Format and overlay caption
img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((1080, 1080))
draw = ImageDraw.Draw(img)
font_title = ImageFont.load_default()
font_body = ImageFont.load_default()
font_footer = ImageFont.load_default()

lines = caption.split("\n")
title = lines[0].strip()
bullets = [line.strip("•* ") for line in lines[1:] if line.strip()]

# Title
draw.text((540, 720), title, fill="black", anchor="mm", font=font_title)

# Bullets
y = 780
for bullet in bullets:
    draw.text((540, y), f"• {bullet}", fill="black", anchor="mm", font=font_body)
    y += 50

# Footer
footer_text = "---- alaghverse ----"
draw.text((540, 1020), footer_text, fill="black", anchor="mm", font=font_footer)

# 📤 Show image
img.show()
