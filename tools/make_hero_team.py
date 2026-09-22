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

W, H = 2400, 1150          # 히어로 캔버스
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



def head_width(rgba):
    """머리 폭(픽셀) 추정 — 인물 크기를 얼굴 기준으로 맞추기 위한 값"""
    a = rgba.split()[3]
    w, h = a.size
    px = a.load()
    widths = []
    for y in range(int(h * 0.10), int(h * 0.24)):
        xs = [x for x in range(0, w, 2) if px[x, y] > 128]
        if xs:
            widths.append(xs[-1] - xs[0])
    widths.sort()
    return widths[len(widths) // 2] if widths else w


def normalize(rgba, target_white=236, target_lum=None):
    """흰 가운을 기준으로 화이트밸런스를 맞추고 전체 밝기를 통일"""
    r, g, b, a = rgba.split()
    rp, gp, bp, ap = r.load(), g.load(), b.load(), a.load()
    w, h = rgba.size
    sums = [0.0, 0.0, 0.0]
    cnt = 0
    lum_sum, lum_cnt = 0.0, 0
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            if ap[x, y] < 200:
                continue
            rr, gg, bb = rp[x, y], gp[x, y], bp[x, y]
            lum = 0.299 * rr + 0.587 * gg + 0.114 * bb
            lum_sum += lum
            lum_cnt += 1
            if lum > 190:                      # 흰 가운 영역
                sums[0] += rr; sums[1] += gg; sums[2] += bb; cnt += 1
    if not cnt or not lum_cnt:
        return rgba, 0
    mean = [v / cnt for v in sums]
    lum_mean = lum_sum / lum_cnt
    gains = [target_white / m if m > 1 else 1.0 for m in mean]
    if target_lum:
        k = target_lum / lum_mean
        gains = [gn * k for gn in gains]
    gains = [max(0.75, min(1.3, gn)) for gn in gains]
    ch = [c.point(lambda v, gn=gn: min(255, round(v * gn))) for c, gn in zip((r, g, b), gains)]
    return Image.merge("RGBA", (ch[0], ch[1], ch[2], a)), lum_mean


def ground_shadow(w, h):
    s = Image.new("L", (w, h), 0)
    ImageDraw.Draw(s).ellipse([0, 0, w, h], fill=80)
    return s.filter(ImageFilter.GaussianBlur(h * 0.45))


def fit_height(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


def shadow(size, blur=28, alpha=60):
    s = Image.new("L", size, 0)
    ImageDraw.Draw(s).ellipse([0, 0, size[0], size[1]], fill=alpha)
    return s.filter(ImageFilter.GaussianBlur(blur))


def main():
    os.makedirs(OUT, exist_ok=True)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # ── 인물 보정: 화이트밸런스·밝기를 통일하고 얼굴 크기를 맞춘다 ─────────────
    raw = {k: cutout(k) for k in ("shin", "kim", "lee")}
    lums = {k: normalize(v)[1] for k, v in raw.items()}
    target_lum = sum(lums.values()) / len(lums)
    norm = {k: normalize(v, target_lum=target_lum)[0] for k, v in raw.items()}

    heads = {k: head_width(v) for k, v in norm.items()}
    target_head = sum(heads.values()) / len(heads)
    # 대표원장만 아주 살짝 크게(앞쪽에 선 느낌)
    boost = {"shin": 1.0, "kim": 1.06, "lee": 1.0}
    sized = {}
    for k, im in norm.items():
        f = (target_head / heads[k]) * boost[k]
        sized[k] = im.resize((max(1, round(im.width * f)), max(1, round(im.height * f))), Image.LANCZOS)

    # 얼굴 높이를 맞추기 위해 머리 꼭대기를 기준선에 정렬 (가운데만 조금 위로)
    scale = (H * 0.80) / max(im.height for im in sized.values())
    people = []
    for k in ("shin", "kim", "lee"):
        im = sized[k]
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        people.append((k, im))

    gap = -round(W * 0.015)
    total = sum(im.width for _, im in people) + gap * (len(people) - 1)
    avail = round(W * 0.45)
    if total > avail:
        k2 = avail / total
        people = [(k, im.resize((round(im.width * k2), round(im.height * k2)), Image.LANCZOS)) for k, im in people]
        gap = round(gap * k2)
        total = sum(im.width for _, im in people) + gap * (len(people) - 1)

    head_top = round(H * 0.10)
    offset = {"shin": round(H * 0.022), "kim": 0, "lee": round(H * 0.022)}
    x = round(W * 0.975) - total
    placed, spots = [], []
    for key, im in people:
        spots.append((key, im, x, head_top + offset[key]))
        placed.append((x, x + im.width))
        x += im.width + gap
    for key, im, px_, py in spots:
        canvas.paste(im, (px_, py), im)

    # 인물만 타이트하게 잘라 한 장으로 (히어로 우측 칼럼에 그대로 배치)
    cut = min(py + im.height for _, im, _, py in spots)
    left = max(0, min(a for a, _ in placed) - round(W * 0.015))
    right = min(W, max(b for _, b in placed) + round(W * 0.015))
    team = canvas.crop((left, round(H * 0.045), right, cut))
    team = team.resize((1600, round(team.height * 1600 / team.width)), Image.LANCZOS)
    path = os.path.join(OUT, "directors-team.webp")
    team.save(path, "WEBP", quality=90, method=6, lossless=False, exact=False)
    print("directors-team", team.size, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    main()
