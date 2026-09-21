# -*- coding: utf-8 -*-
"""
질환별 대표 이미지 생성 (Gemini 3.1 Flash Image / Nano Banana 2, 2K)
  set GEMINI_API_KEY=...   (키는 환경변수로만, 코드/깃에 저장 금지)
  python tools/gen_condition_images.py            # 전체 15장
  python tools/gen_condition_images.py reflux     # 특정 슬러그만 재생성
원본 PNG는 assets/ai_raw/ 에, 웹용 webp는 docs/images/ai/ 에 저장
"""
import base64
import json
import os
import sys
import time
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "ai_raw")
OUT = os.path.join(ROOT, "docs", "images", "ai")
MODEL = "gemini-3.1-flash-image"
KEY = os.environ.get("GEMINI_API_KEY")

STYLE = (
    "Editorial lifestyle photograph for a Korean medicine (한의원) clinic website. "
    "Korean adult subject, natural realistic skin, soft diffused daylight, calm and trustworthy mood. "
    "Warm ivory and beige tones with muted sage green accents, shallow depth of field, clean uncluttered background. "
    "The person shows mild discomfort with a gentle, non-dramatic expression. "
    "No text, no letters, no logos, no watermarks, no medical gore, no needles. Photorealistic, 4:3 composition."
)

PROMPTS = {
    "lumbar-disc": "A Korean man in his 40s in a light shirt, rising from an office chair and pressing one hand on his lower back, side view, home office with wooden desk.",
    "cervical-disc": "A Korean woman in her 30s at a desk in front of a monitor, tilting her head and touching the back of her neck with one hand, soft window light.",
    "frozen-shoulder": "A Korean woman in her 50s in a beige cardigan trying to raise one arm, other hand holding her shoulder, standing in a bright living room.",
    "spinal-stenosis": "An elderly Korean man pausing on a walk in a park, one hand on his lower back and the other resting on a wooden bench, autumn light, distant path.",
    "tennis-elbow": "Close-up of a Korean woman's arms in a kitchen: one hand holding a kettle, the other hand gripping the outside of her elbow, warm counter light.",
    "carpal-tunnel": "A Korean woman in her 40s sitting on the edge of a bed in early morning, shaking and rubbing her wrist and hand, soft pale light.",
    "plantar-fasciitis": "Bare feet of a Korean adult stepping onto a wooden floor from a bed in the morning, one hand reaching to touch the heel, low angle, soft sunlight.",
    "sciatica": "A Korean man in his 30s seated on a sofa, shifting his weight and holding the back of his hip and thigh, living room with plants.",
    "traffic-accident": "A Korean woman in her 30s sitting in the driver's seat of a parked car, seatbelt on, gently holding the back of her neck, calm daylight through the windshield, no damage visible.",
    "chronic-headache": "A Korean man in his 30s at a desk pressing both temples with his fingertips, eyes closed, laptop and a cup of tea, soft afternoon light.",
    "reflux": "A Korean woman in her 40s at a dining table after a meal, one hand resting on her upper chest, slight discomfort, ceramic dishes and warm light.",
    "indigestion": "A Korean man in his 40s at a table with a half-finished bowl of rice and soup, one hand on his stomach, looking down thoughtfully, warm kitchen light.",
    "menopause": "A Korean woman in her early 50s by a window fanning herself with a paper fan, flushed cheeks, linen blouse, soft light and a plant.",
    "insomnia": "A Korean woman in her 30s lying awake in bed at night, eyes open looking at the ceiling, soft blue moonlight and a warm bedside lamp, calm.",
    "allergic-rhinitis": "A Korean woman in her 20s holding a tissue to her nose about to sneeze, autumn morning, soft golden light, cozy sweater.",
}


def generate(slug, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = {
        "contents": [{"parts": [{"text": STYLE + "\n\nScene: " + prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "4:3", "imageSize": "2K"},
        },
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.load(r)
            break
        except Exception as e:  # noqa
            err = getattr(e, "read", lambda: b"")().decode(errors="ignore")
            print(f"  retry {attempt+1}: {e} {err[:200]}")
            time.sleep(5)
    else:
        raise RuntimeError("generation failed: " + slug)
    for part in data["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"])
    raise RuntimeError("no image in response: " + json.dumps(data)[:300])


def to_web(slug):
    im = Image.open(os.path.join(RAW, slug + ".png")).convert("RGB")
    im.thumbnail((1600, 1600), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, slug + ".webp")
    im.save(dst, "WEBP", quality=82, method=6)
    print(f"  → {dst} {im.size} {os.path.getsize(dst)//1024}KB")


def main():
    if not KEY:
        sys.exit("GEMINI_API_KEY 환경변수가 없습니다.")
    os.makedirs(RAW, exist_ok=True)
    targets = sys.argv[1:] or list(PROMPTS)
    for slug in targets:
        print(slug)
        png = generate(slug, PROMPTS[slug])
        with open(os.path.join(RAW, slug + ".png"), "wb") as f:
            f.write(png)
        to_web(slug)


if __name__ == "__main__":
    main()
