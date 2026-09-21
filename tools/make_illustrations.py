# -*- coding: utf-8 -*-
"""
질환·진료별 일러스트 이미지 생성 (원내 포스터 스타일: 아이보리 배경 + 녹색 라인 아이콘 + 골드 포인트)
SVG → 헤드리스 Chrome 렌더 → webp.   실행: python tools/make_illustrations.py
"""
import os
import subprocess
import tempfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "images", "illust")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

JADE, GOLD, INK = "#3e6b5c", "#b08d4f", "#242321"

# 아이콘: viewBox 0 0 200 200, stroke 기반. {dot} 은 골드 포인트
ICONS = {
    # ── 근골격 ──────────────────────────────────────────────────────────────
    "lumbar-disc": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <rect x="76" y="34" width="48" height="22" rx="8"/><rect x="76" y="70" width="48" height="22" rx="8"/>
        <rect x="76" y="106" width="48" height="22" rx="8"/><rect x="76" y="142" width="48" height="22" rx="8"/>
        <ellipse cx="100" cy="63" rx="20" ry="5"/><ellipse cx="100" cy="135" rx="20" ry="5"/>
        <path d="M80 99 a20 5 0 0 1 40 0 M80 99 a20 5 0 0 0 26 4 M120 99 c8 4 16 12 12 20"/>
        <path d="M136 60 q26 40 0 90" stroke-dasharray="3 7"/>
      </g><circle cx="132" cy="112" r="7" fill="{g}"/>""",
    "cervical-disc": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M128 36 a40 40 0 1 0 -56 56 l-6 30 h48 l6 -30 a40 40 0 0 0 8 -56z"/>
        <path d="M92 122 v44 M108 122 v44"/><rect x="88" y="128" width="24" height="10" rx="4"/><rect x="88" y="146" width="24" height="10" rx="4"/>
        <path d="M60 168 h80"/>
      </g><circle cx="120" cy="140" r="7" fill="{g}"/>""",
    "frozen-shoulder": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="70" cy="46" r="16"/><path d="M50 78 q20 -12 46 0 v90 h-50 v-70"/>
        <path d="M96 84 l52 -40 l14 22"/><path d="M96 84 l26 60"/>
        <path d="M110 64 a58 58 0 0 1 52 -14" stroke-dasharray="3 7"/>
      </g><circle cx="96" cy="84" r="7" fill="{g}"/>""",
    "spinal-stenosis": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <rect x="62" y="30" width="34" height="24" rx="7"/><rect x="62" y="70" width="34" height="24" rx="7"/>
        <rect x="62" y="110" width="34" height="24" rx="7"/><rect x="62" y="150" width="34" height="24" rx="7"/>
        <path d="M112 30 v30 q8 20 0 40 q-8 20 0 40 v34 M138 30 v30 q-8 20 0 40 q8 20 0 40 v34"/>
      </g><circle cx="125" cy="100" r="7" fill="{g}"/>""",
    "tennis-elbow": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M34 76 h68 a26 26 0 0 1 26 26 v56 a13 13 0 0 1 -26 0 v-43 h-68 a13 13 0 0 1 0 -26z"/>
        <path d="M120 170 a14 14 0 1 0 0 1"/>
        <path d="M134 78 l12 -12 M142 96 l16 -4 M126 66 l4 -16" stroke="{g}"/>
      </g><circle cx="122" cy="98" r="7" fill="{g}"/>""",
    "carpal-tunnel": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M70 170 v-50 a10 10 0 0 1 20 0 v20 v-70 a10 10 0 0 1 20 0 v66 v-80 a10 10 0 0 1 20 0 v80 v-64 a10 10 0 0 1 20 0 v70 c0 30 -20 44 -40 44 h-14 c-14 0 -26 -8 -30 -20 l-22 -34 a9 9 0 0 1 16 -10 z"/>
        <path d="M70 176 h80"/>
      </g><circle cx="110" cy="170" r="7" fill="{g}"/>""",
    "plantar-fasciitis": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M60 40 c-14 40 -16 70 -8 96 c4 12 2 22 -8 30 h96 c20 0 36 -10 36 -22 c0 -10 -14 -12 -34 -14 c-30 -4 -46 -18 -52 -50 c-4 -20 -6 -36 -30 -40z"/>
        <path d="M68 150 q40 -30 90 -10" stroke-dasharray="3 7"/>
      </g><circle cx="66" cy="148" r="7" fill="{g}"/>""",
    "sciatica": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M58 40 h84 v34 q-42 26 -84 0z"/>
        <path d="M66 82 v86 h26 v-64 M108 104 v64 h26 v-86"/>
        <path d="M126 84 q6 30 0 56 q-3 14 2 26" stroke="{g}" stroke-width="4" stroke-dasharray="4 6"/>
      </g><circle cx="126" cy="80" r="7" fill="{g}"/>""",
    "traffic-accident": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M46 126 v-20 l20 -34 h60 l28 34 v20 z"/><path d="M70 74 l-6 26 h58 l-8 -26"/>
        <circle cx="70" cy="132" r="12"/><circle cx="134" cy="132" r="12"/>
        <path d="M20 84 h14 M14 100 h20 M20 116 h14"/>
      </g><circle cx="156" cy="112" r="7" fill="{g}"/>""",
    # ── 내과·체질 ────────────────────────────────────────────────────────────
    "chronic-headache": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M116 30 a44 44 0 1 0 -52 66 l-4 34 h50 l6 -30 a44 44 0 0 0 0 -70z"/>
        <path d="M148 46 l-16 26 h16 l-14 30" stroke="{g}" stroke-width="5"/>
      </g><circle cx="98" cy="70" r="7" fill="{g}"/>""",
    "reflux": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M96 30 v66 c0 22 -30 22 -34 44 c-4 24 24 40 50 30 c30 -12 40 -40 30 -60 c-8 -14 -24 -18 -26 -38 v-42"/>
        <path d="M106 90 v-46 M96 56 l10 -12 l10 12" stroke="{g}"/>
      </g><circle cx="80" cy="150" r="7" fill="{g}"/>""",
    "indigestion": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M96 30 v66 c0 22 -30 22 -34 44 c-4 24 24 40 50 30 c30 -12 40 -40 30 -60 c-8 -14 -24 -18 -26 -38 v-42"/>
        <circle cx="90" cy="130" r="5"/><circle cx="110" cy="146" r="4"/><circle cx="118" cy="122" r="3"/>
      </g><circle cx="80" cy="150" r="7" fill="{g}"/>""",
    "menopause": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M116 30 a44 44 0 1 0 -52 66 l-4 34 h50 l6 -30 a44 44 0 0 0 0 -70z"/>
        <path d="M134 60 q10 -6 20 0 q10 6 20 0 M134 78 q10 -6 20 0 q10 6 20 0 M134 96 q10 -6 20 0 q10 6 20 0" stroke="{g}"/>
      </g><circle cx="108" cy="92" r="7" fill="{g}"/>""",
    "insomnia": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M118 40 a50 50 0 1 0 44 74 a40 40 0 0 1 -44 -74z"/>
        <path d="M52 44 l10 0 l-10 12 l10 0 M40 80 l14 0 l-14 16 l14 0" stroke="{g}"/>
      </g><circle cx="150" cy="150" r="7" fill="{g}"/>""",
    "allergic-rhinitis": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M96 34 c-6 40 -30 64 -30 88 c0 14 12 22 24 20 c8 -2 12 -8 20 -8 c8 0 12 6 22 4 c12 -4 12 -20 0 -32"/>
        <path d="M84 148 c-6 8 -18 10 -24 4 M118 148 c6 8 18 10 24 4"/>
        <path d="M150 70 l16 -8 M152 88 l18 0 M150 106 l16 8" stroke="{g}"/>
      </g><circle cx="102" cy="126" r="7" fill="{g}"/>""",
    # ── 진료 안내 ────────────────────────────────────────────────────────────
    "constitution": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="100" cy="100" r="60"/>
        <path d="M100 40 a30 30 0 0 1 0 60 a30 30 0 0 0 0 60"/>
        <path d="M60 100 q40 -70 80 0" stroke-dasharray="3 7"/>
      </g><circle cx="100" cy="70" r="7" fill="{g}"/><circle cx="100" cy="130" r="7" fill="{j}"/>""",
    "postpartum": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="82" cy="44" r="17"/><path d="M50 98 q32 -22 64 0 v72 h-64z"/>
        <path d="M114 100 q-22 22 -4 46"/><circle cx="126" cy="110" r="12"/><path d="M110 132 q16 -10 32 0 v38 h-32z"/>
      </g><circle cx="70" cy="122" r="7" fill="{g}"/>""",
    "diet": """
      <g stroke="{j}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M100 36 c-30 0 -50 22 -50 48 c0 30 20 56 50 80 c30 -24 50 -50 50 -80 c0 -26 -20 -48 -50 -48z"/>
        <path d="M76 84 h48 M100 84 v-10 M82 84 v-6 M118 84 v-6 M91 84 v-4 M109 84 v-4"/>
      </g><circle cx="100" cy="96" r="7" fill="{g}"/>""",
}

TITLES = {
    "lumbar-disc": "허리디스크", "cervical-disc": "목디스크", "frozen-shoulder": "오십견 · 어깨통증",
    "spinal-stenosis": "척추관협착증", "tennis-elbow": "테니스엘보", "carpal-tunnel": "손목터널증후군",
    "plantar-fasciitis": "족저근막염", "sciatica": "좌골신경통", "traffic-accident": "교통사고 후유증",
    "chronic-headache": "만성두통", "reflux": "역류성식도염", "indigestion": "소화불량", "menopause": "갱년기 증후군",
    "insomnia": "불면증 · 만성피로", "allergic-rhinitis": "알레르기비염",
    "constitution": "체질개선 클리닉", "postpartum": "산후보약", "diet": "한방 다이어트",
}

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@700&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
html,body{{margin:0}} body{{width:1200px;height:900px;background:#f1ede6;position:relative;overflow:hidden;font-family:"Pretendard Variable",sans-serif}}
.bg{{position:absolute;inset:0;background:
  radial-gradient(circle at 78% 22%, rgba(176,141,79,.10), transparent 32%),
  radial-gradient(circle at 20% 80%, rgba(62,107,92,.08), transparent 36%)}}
.ring{{position:absolute;left:50%;top:44%;width:520px;height:520px;transform:translate(-50%,-50%);border-radius:50%;background:#e9efea;box-shadow:inset 0 0 0 1px rgba(62,107,92,.12)}}
.ring2{{position:absolute;left:50%;top:44%;width:620px;height:620px;transform:translate(-50%,-50%);border-radius:50%;border:1px solid rgba(62,107,92,.14)}}
svg{{position:absolute;left:50%;top:44%;width:360px;height:360px;transform:translate(-50%,-50%)}}
.title{{position:absolute;left:0;right:0;top:722px;text-align:center;font-family:"Gowun Batang",serif;font-weight:700;font-size:44px;color:#26473a;letter-spacing:-.01em}}
.rule{{position:absolute;left:50%;top:790px;width:56px;height:2px;background:#b08d4f;transform:translateX(-50%)}}
.brand{{position:absolute;left:0;right:0;top:812px;text-align:center;font-size:17px;letter-spacing:.28em;color:#6b6862}}
.corner{{position:absolute;right:44px;top:40px;font-size:15px;letter-spacing:.22em;color:#b08d4f}}
</style></head><body>
<div class="bg"></div><div class="ring2"></div><div class="ring"></div>
<svg viewBox="0 0 200 200">{icon}</svg>
<div class="title">{title}</div><div class="rule"></div>
<div class="brand">연결한의원 청주오창</div><div class="corner">{corner}</div>
</body></html>"""


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for key, icon in ICONS.items():
        corner = "CLINIC" if key in ("constitution", "postpartum", "diet") else "HEALTH GUIDE"
        html = HTML.format(icon=icon.format(j=JADE, g=GOLD), title=TITLES[key], corner=corner)
        hp = os.path.join(tmp, key + ".html")
        with open(hp, "w", encoding="utf-8") as f:
            f.write(html)
        png = os.path.join(tmp, key + ".png")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,900",
                        "--virtual-time-budget=6000", f"--screenshot={png}", "file:///" + hp.replace("\\", "/")],
                       capture_output=True)
        im = Image.open(png).convert("RGB")
        dst = os.path.join(OUT, key + ".webp")
        im.save(dst, "WEBP", quality=84, method=6)
        print(key, im.size, os.path.getsize(dst) // 1024, "KB")


if __name__ == "__main__":
    main()
