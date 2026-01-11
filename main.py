import os
import random
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

# ---------------- TOPIC POOL ----------------
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

    r = requests.post(STABILITY_URL, headers=STABILITY_HEADERS, files=files, timeout
