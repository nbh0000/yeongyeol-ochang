# -*- coding: utf-8 -*-
"""
세 원장(신재형·김현교·이상현) 프로필 사진을 누끼 따서 한 장의 히어로 이미지로 합성
  python tools/make_hero_team.py      → docs/images/hero/directors-team.webp
"""
import os

from PIL import Image, ImageDraw, ImageFilter
from rembg import remove, new_session

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
CUT = os.path.join(A, "cutouts")
OUT = os.path.join(ROOT, "docs", "images", "hero")

SRC = {
    "shin": ("06_원장프로필_진료시간표", "KakaoTalk_20260820_200907542.jpg"),
    "kim": ("04_원장사진", "vitastudio 54448_(2).jpg"),
    "lee": ("06_원장프로필_진료시간표", "KakaoTalk_20260508_174930797_02.jpg"),
}

W, H = 2000, 1150          # 히어로 캔버스
BG_TOP, BG_BOT = (243, 240, 234), (228, 223, 213)


def cutout(key):
    """배경 제거 후 인물 바운딩 박스로 크롭한 RGBA 반환 (결과 캐시)"""
    cached = os.path.join(CUT, key + ".png")
    if os.path.exists(cached):
        return Image.open(cached).convert("RGBA")
    d, f = SRC[key]
    im = Image.open(os.path.join(A, d, f)).convert("RGB")
    if im.width > 1600:
        im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    out = remove(im, session=new_session("isnet-general-use"))
    out = out.convert("RGBA")
    # 알파 가장자리를 살짝 부드럽게
    r, g, b, a = out.split()
    a = a.filter(ImageFilter.GaussianBlur(0.6)).point(lambda v: 0 if v < 12 else v)
    out = Image.merge("RGBA", (r, g, b, a))
    out = keep_largest(out)
    out = out.crop(out.getbbox())
    os.makedirs(CUT, exist_ok=True)
    out.save(cached)
    return out


def keep_largest(rgba):
    """알파 채널에서 가장 큰 연결 덩어리(인물)만 남기고 나머지 얼룩 제거"""
    a = rgba.split()[3]
    w, h = a.size
    px = a.load()
    seen = [[False] * w for _ in range(h)]
    best, best_size = None, 0
    for sy in range(0, h, 3):
        for sx in range(0, w, 3):
            if seen[sy][sx] or px[sx, sy] < 40:
                continue
            stack, comp = [(sx, sy)], []
            seen[sy][sx] = True
            while stack:
                x, y = stack.pop()
                comp.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and px[nx, ny] >= 40:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            if len(comp) > best_size:
                best, best_size = comp, len(comp)
    if not best:
        return rgba
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    for x, y in best:
        mp[x, y] = 255
    mask = mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1))
    r, g, b, al = rgba.split()
    al = Image.composite(al, Image.new("L", (w, h), 0), mask.point(lambda v: 255 if v > 60 else 0))
    return Image.merge("RGBA", (r, g, b, al))


def fit_height(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


def shadow(size, blur=28, alpha=60):
    s = Image.new("L", size, 0)
    ImageDraw.Draw(s).ellipse([0, 0, size[0], size[1]], fill=alpha)
    return s.filter(ImageFilter.GaussianBlur(blur))


def main():
    os.makedirs(OUT, exist_ok=True)
    canvas = Image.new("RGB", (W, H), BG_TOP)

    # 배경: 세로 그라데이션 + 부드러운 원형 하이라이트
    grad = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1)
        grad.putpixel((0, y), tuple(round(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))
    canvas = grad.resize((W, H))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * 0.30, -H * 0.5, W * 1.05, H * 1.1], fill=70)
    canvas = Image.composite(Image.new("RGB", (W, H), (255, 253, 249)), canvas, glow.filter(ImageFilter.GaussianBlur(160)))

    # 인물 배치: 좌측은 카피 공간, 우측에 세 원장 (가운데 대표원장이 가장 크게)
    # 왼쪽부터 신재형 · 김현교(대표, 가장 크게) · 이상현 순으로 겹치지 않게 배치
    order = [("shin", 0.93), ("kim", 1.02), ("lee", 0.93)]
    people = [(k, fit_height(cutout(k), round(H * hr))) for k, hr in order]
    gap = -round(W * 0.018)          # 살짝 겹쳐 한 팀처럼 보이게
    total = sum(im.width for _, im in people) + gap * (len(people) - 1)
    # 우측 62% 영역 안에 들어오도록 축소
    avail = round(W * 0.53)
    if total > avail:
        k = avail / total
        people = [(key, im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)) for key, im in people]
        gap = round(gap * k)
        total = sum(im.width for _, im in people) + gap * (len(people) - 1)
    x = round(W * 0.985) - total
    placed = []
    for key, im in people:
        canvas.paste(im, (x, H - im.height), im)
        placed.append((x, x + im.width))
        x += im.width + gap

    path = os.path.join(OUT, "directors-team.webp")
    canvas.save(path, "WEBP", quality=88, method=6)
    print("directors-team", canvas.size, os.path.getsize(path) // 1024, "KB")

    # 모바일용: 인물만 타이트하게 담은 별도 이미지 (여백 없이)
    mh = max(im.height for _, im in people)
    mw = total
    pad_x, pad_top = round(mw * 0.03), round(mh * 0.05)
    mob = Image.new("RGB", (mw + pad_x * 2, mh + pad_top), BG_TOP)
    g2 = Image.new("RGB", (1, mob.height))
    for y in range(mob.height):
        t = y / max(1, mob.height - 1)
        g2.putpixel((0, y), tuple(round(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))
    mob = g2.resize(mob.size)
    mx = pad_x
    for key, im in people:
        mob.paste(im, (mx, mob.height - im.height), im)
        mx += im.width + gap
    mob = mob.resize((1200, round(mob.height * 1200 / mob.width)), Image.LANCZOS)
    mp = os.path.join(OUT, "directors-team-mobile.webp")
    mob.save(mp, "WEBP", quality=88, method=6)
    print("directors-team-mobile", mob.size, os.path.getsize(mp) // 1024, "KB")


if __name__ == "__main__":
    main()
