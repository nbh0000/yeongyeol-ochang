# -*- coding: utf-8 -*-
"""
assets/ 원본 사진을 웹용(webp)으로 변환해 site/images/ 에 저장합니다.
실행: python tools/build_images.py
"""
import os
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "docs", "images")


def save(src, dst, width=None, crop=None, quality=82, square=False, fmt="webp", height=None):
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    if crop:
        im = im.crop(crop)
    if square:
        w, h = im.size
        s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    if width and im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    if height and im.height > height:
        im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    if fmt == "webp":
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGB")
        path = os.path.join(OUT, dst + ".webp")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.save(path, "WEBP", quality=quality, method=6)
    else:
        path = os.path.join(OUT, dst + "." + fmt)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.save(path)
    print(dst, im.size, os.path.getsize(path) // 1024, "KB")


def main():
    os.makedirs(OUT, exist_ok=True)
    D = lambda *p: os.path.join(A, *p)

    # ── 히어로 / 진료 장면 (김현교 원장 촬영 사진) ─────────────────────────
    doc = "04_원장사진"
    save(D(doc, "DSC09327(수정).jpg"), "hero/consult-monitor", 1920)
    save(D(doc, "DSC09335(수정).jpg"), "hero/consult-monitor-2", 1600)
    save(D(doc, "DSC09352(수정).jpg"), "treat/pulse-consult", 1600)
    save(D(doc, "DSC09371(수정).jpg"), "treat/chuna", 1600)
    save(D(doc, "DSC09387(수정).jpg"), "treat/acupuncture-1", 1600)
    save(D(doc, "DSC09393(수정).jpg"), "treat/acupuncture-2", 1600)
    save(D(doc, "DSC09400(수정).jpg"), "treat/acupuncture-3", 1600)
    save(D(doc, "DSC09417(수정).jpg"), "treat/acupuncture-4", 1600)
    save(D(doc, "DSC09449(수정).jpg"), "treat/director-standing", 1200)

    # ── 원장 프로필 ─────────────────────────────────────────────────────
    # 원장 프로필 포스터에서 인물 영역 크롭 → 세 원장 모두 동일한 배경·구도
    PP = "06_원장프로필_진료시간표"
    save(D(PP, "1787188344087.jpg"), "directors/kim-hyeongyo", 800, crop=(585, 200, 1080, 937), quality=88)
    save(D(PP, "KakaoTalk_20260508_174930797_01.jpg"), "directors/shin-jaehyeong", 800, crop=(585, 200, 1080, 937), quality=88)
    save(D(PP, "KakaoTalk_20260508_174930797_03.jpg"), "directors/lee-sanghyeon", 800, crop=(585, 200, 1080, 937), quality=88)
    save(D(doc, "vitastudio 54448_(2).jpg"), "directors/kim-hyeongyo-studio", 1200)
    save(D(doc, "vitastudio 54314_(2).jpg"), "directors/kim-hyeongyo-casual", 1200)
    save(D(doc, "vitastudio 54346_(2).jpg"), "directors/kim-hyeongyo-point", 1600)
    save(D("06_원장프로필_진료시간표", "KakaoTalk_20260820_200907542.jpg"), "directors/shin-jaehyeong-studio", 1200)
    save(D("06_원장프로필_진료시간표", "vitastudio_54314__2_-removebg-preview.png"), "directors/kim-hyeongyo-cutout", fmt="png")
    # 원장 프로필 포스터 (이력·진료시간표)
    save(D("06_원장프로필_진료시간표", "1787188344087.jpg"), "directors/profile-kim-hyeongyo", 1080)
    save(D("06_원장프로필_진료시간표", "KakaoTalk_20260508_174930797_01.jpg"), "directors/profile-shin-jaehyeong", 1080)
    save(D("06_원장프로필_진료시간표", "KakaoTalk_20260508_174930797_03.jpg"), "directors/profile-lee-sanghyeon", 1080)

    # ── 원내 사진 ────────────────────────────────────────────────────────
    cl = os.path.join("01_원내사진", "compressed")
    names = {
        1: "treatment-room-1", 2: "treatment-room-2", 3: "consult-room-1", 4: "consult-room-2",
        5: "lounge-1", 6: "corridor-1", 7: "hydro-bed", 8: "reception-1", 9: "treatment-room-3",
        10: "corridor-posters", 11: "entrance-hall", 12: "waiting-1", 13: "entrance-sign",
        14: "waiting-2", 15: "waiting-3", 16: "waiting-4",
    }
    for i, n in names.items():
        save(D(cl, f"{i:02d}.png"), f"clinic/{n}", 1600)
    save(D("02_플레이스썸네일", "네이버플레이스_1인치료실.png"), "clinic/private-room-card", 1200)
    save(D("02_플레이스썸네일", "네이버플레이스05.png"), "clinic/hydro-lounge-card", 1200)

    # ── 포스터 ──────────────────────────────────────────────────────────
    po = "03_원내포스터"
    save(D(po, "공진단포스터.png"), "posters/gongjindan", 1200)
    save(D(po, "다이어트포스터.png"), "posters/diet", 1200)
    save(D(po, "성장보약포스터.png"), "posters/growth", 1200)
    save(D(po, "추나포스터.png"), "posters/chuna", 1200)
    save(D(po, "체질개선 클리닉 소개.png"), "posters/constitution", 1200)
    save(D(po, "KakaoTalk_20260820_094941285.jpg"), "posters/chuna-insurance", 900, crop=(0, 130, 1707, 5281))
    save(D("02_플레이스썸네일", "연결.png"), "posters/365", 1080)
    # 포스터 내 사진 영역 크롭 (카드 썸네일용)
    save(D(po, "공진단포스터.png"), "cards/gongjindan", 1200, crop=(1095, 2635, 3415, 4955))
    save(D(po, "성장보약포스터.png"), "cards/growth", 1400, crop=(0, 3200, 5906, 6100))
    save(D(po, "다이어트포스터.png"), "cards/diet", 1200, crop=(3650, 5150, 5480, 7560))

    # ── 오시는 길 / 주차 ─────────────────────────────────────────────────
    save(D("07_오시는길_주차안내", "연결한의원 오시는길.png"), "location/map-poster", 1190)
    save(D("07_오시는길_주차안내", "연결한의원 오시는길.png"), "location/map", 1000, crop=(90, 360, 915, 885))
    save(D("07_오시는길_주차안내", "KakaoTalk_20260820_094956324.jpg"), "location/parking-guide", 1264)
    save(D("07_오시는길_주차안내", "KakaoTalk_20260820_094956324.jpg"), "location/parking-photos", 1100, crop=(100, 1075, 1170, 1640))

    # ── 원장님 제공 배너 (공진단·추나·다이어트) ─────────────────────────────
    for n in ("gongjindan", "chuna", "diet"):
        save(D("08_추가사진", n + ".jpeg"), "banner/" + n, 1424, quality=86)

    # ── 로고 ────────────────────────────────────────────────────────────
    lg = "05_로고"
    save(D(lg, "KakaoTalk_20251121_200753637_01.png"), "logo/logo-green", 800, fmt="png")
    save(D(lg, "KakaoTalk_20251121_200753637_03.png"), "logo/logo-gold", 800, fmt="png")
    # 세로형 로고에서 심볼 부분만 크롭 (0~554px 행이 심볼, 그 아래가 워드마크)
    save(D(lg, "KakaoTalk_20251121_200753637.png"), "logo/symbol-green", 400, fmt="png", crop=(0, 0, 1573, 560))
    save(D(lg, "KakaoTalk_20251121_200753637_02.png"), "logo/symbol-gold", 400, fmt="png", crop=(0, 0, 1573, 560))
    save(D(lg, "KakaoTalk_20251121_200753637.png"), "logo/stacked-green", 600, fmt="png")
    save(D(lg, "KakaoTalk_20251121_200753637_02.png"), "logo/stacked-gold", 600, fmt="png")
    # 파비콘/OG
    save(D(lg, "KakaoTalk_20251121_200753637.png"), "logo/symbol-green-512", 512, fmt="png", crop=(0, 0, 1573, 560))



def hero_composites():
    """세로 스튜디오 사진을 가로 히어로로 확장: 사진 가장자리 색을 좌우로 늘려 배경을 잇는다."""
    D = lambda *p: os.path.join(A, *p)
    # 신재형 원장 (2400x3600, 회색 그라데이션 배경) → 1920x1100 히어로, 인물은 우측
    im = Image.open(D("06_원장프로필_진료시간표", "KakaoTalk_20260820_200907542.jpg")).convert("RGB")
    W, H = 1920, 1100
    ph = int(H * 1.18)
    person = im.resize((round(im.width * ph / im.height), ph), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H))
    # 배경: 인물 사진 왼쪽 가장자리 세로줄을 가로로 늘림
    edge = person.crop((0, 0, 6, ph)).resize((W, ph), Image.BILINEAR)
    canvas.paste(edge.crop((0, 0, W, H)), (0, 0))
    x = W - person.width - 120
    canvas.paste(person.crop((0, 0, person.width, H)), (x, 0))
    # 접합부 부드럽게: 인물 사진 왼쪽 60px에 그라데이션 마스크
    mask = Image.new("L", (person.width, H), 255)
    from PIL import ImageDraw
    d = ImageDraw.Draw(mask)
    for i in range(80):
        d.line([(i, 0), (i, H)], fill=int(255 * i / 80))
    canvas.paste(person.crop((0, 0, person.width, H)), (x, 0), mask)
    path = os.path.join(OUT, "hero", "director-shin.webp")
    canvas.save(path, "WEBP", quality=84, method=6)
    print("hero/director-shin", canvas.size, os.path.getsize(path) // 1024, "KB")

    # 가로형 카드용 크롭 (상반신)
    save(D("06_원장프로필_진료시간표", "KakaoTalk_20260820_200907542.jpg"), "directors/shin-jaehyeong-wide", 1400, crop=(0, 350, 2400, 2350))
    save(D("06_원장프로필_진료시간표", "KakaoTalk_20260508_174930797_03.jpg"), "directors/lee-sanghyeon-wide", 1080, crop=(585, 200, 1080, 720), quality=88)
    save(D("06_원장프로필_진료시간표", "KakaoTalk_20260508_174930797_01.jpg"), "directors/shin-jaehyeong-poster-wide", 1080, crop=(585, 200, 1080, 720), quality=88)


if __name__ == "__main__":
    main()
    hero_composites()
