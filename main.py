import os
import requests
import base64
import io
from PIL import Image, ImageDraw
import google.generativeai as genai

# ---------------- CONFIG ----------------
TOPICS = [
    "Benefits of soaked almonds",
    "High protein vegetarian foods",
    "Foods that improve gut health"
]

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

def generate_image_prompt(topic):
    prompt = (
        "Create a minimal flat lay Instagram food photography prompt. "
        f"Topic: {topic}. "
        "Clean white background, soft natural lighting, "
        "professional food photography, no text in image."
    )
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_nutrition_text(topic):
    text_prompt = (
        "Write short Instagram nutrition content. "
        f"Topic: {topic}. "
        "Format: Title, then three bullet points."
    )
    response = model.generate_content(text_prompt)
    return response.text.strip()

# ---------------- STABILITY AI IMAGE GENERATION ----------------
STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"
STABILITY_HEADERS = {
    "Authorization": f"Bearer {os.environ['STABILITY_API_KEY']}",
    "Accept": "application/json"
}

def generate_image(prompt, path):
    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
        "model": (None, "stable-diffusion-xl-1024-v1-0")
    }

    r = requests.post(STABILITY_URL, headers=STABILITY_HEADERS, files=files, timeout=120)

    if r.status_code != 200:
        raise RuntimeError(f"Stability AI failed: {r.status_code} {r.text}")

    data = r.json()
    if "images" not in data or not data["images"]:
        raise RuntimeError(f"No image returned: {data}")

    image_base64 = data["images"][0]["base64"]
    image_bytes = base64.b64decode(image_base64)

    with open(path, "wb") as f:
        f.write(image_bytes)

def format_and_overlay(image_path, text, out_path):
    img = Image.open(image_path).convert("RGB").resize((1080, 1080))
    draw = ImageDraw.Draw(img)

    draw.multiline_text(
        (40, 720),
        text,
        fill="black",
        spacing=12
    )

    img.save(out_path)

# ---------------- PIPELINE ----------------
def run():
    for idx, topic in enumerate(TOPICS):
        print(f"Processing: {topic}")

        try:
            prompt = generate_image_prompt(topic)
            print("Gemini prompt:", prompt)

            text = generate_nutrition_text(topic)
            print("Gemini text:", text)

            raw = f"{OUTPUT_DIR}/raw_{idx}.png"
            final = f"{OUTPUT_DIR}/post_{idx}.png"

            generate_image(prompt, raw)
            format_and_overlay(raw, text, final)

            print("Created:", final)

        except Exception as e:
            print(f"Error processing '{topic}': {e}")

if __name__ == "__main__":
    run()
