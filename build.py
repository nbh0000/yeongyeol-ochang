# -*- coding: utf-8 -*-
"""
연결한의원 청주오창 홈페이지 정적 빌드 스크립트

  python build.py             → site/ 폴더에 HTML 생성
  python tools/build_images.py → assets/ 원본을 site/images/ 로 최적화 (사진 바뀔 때만)

콘텐츠 수정은 src/*.py, 레이아웃 수정은 templates/*.html, 스타일은 site/css/style.css
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from jinja2 import Environment, FileSystemLoader, select_autoescape

from site_info import SITE, NAV, DIRECTORS, FEATURED, TICKER_ROW1, TICKER_ROW2, STATS, CORE, WHO, WHY, HOME_FAQ
from services import SERVICES
from conditions import CONDITIONS, CONDITION_CATEGORIES
from columns import COLUMNS, PRINCIPLES, PATIENT_QUESTIONS, FAQ_GROUPS

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")

env = Environment(
    loader=FileSystemLoader(os.path.join(ROOT, "templates")),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)

COND = {c["slug"]: c for c in CONDITIONS}
SVC = {s["slug"]: s for s in SERVICES}

# 해시태그 → 링크
TICKER_LINKS = {
    "오십견": "conditions/frozen-shoulder.html", "목디스크": "conditions/cervical-disc.html",
    "허리디스크": "conditions/lumbar-disc.html", "테니스엘보": "conditions/tennis-elbow.html",
    "손목터널증후군": "conditions/carpal-tunnel.html", "족저근막염": "conditions/plantar-fasciitis.html",
    "좌골신경통": "conditions/sciatica.html", "척추관협착증": "conditions/spinal-stenosis.html",
    "녹용2배공진단": "services/gongjindan.html", "한방다이어트": "services/diet.html",
    "교통사고후유증": "conditions/traffic-accident.html", "갱년기": "conditions/menopause.html",
    "불면증": "conditions/insomnia.html", "만성두통": "conditions/chronic-headache.html",
    "알레르기비염": "conditions/allergic-rhinitis.html", "역류성식도염": "conditions/reflux.html",
}


def search_index():
    idx = []
    for s in SERVICES:
        idx.append({"title": s["name"], "url": f"services/{s['slug']}.html", "type": "진료 안내", "keywords": s["short"] + " " + " ".join(s["who"])})
    for c in CONDITIONS:
        idx.append({"title": c["name"], "url": f"conditions/{c['slug']}.html", "type": "질환 정보", "keywords": c["category"] + " " + c["lead"] + " " + " ".join(c["scenes"])})
    for c in COLUMNS:
        idx.append({"title": c["title"], "url": f"column/{c['slug']}.html", "type": "건강 칼럼", "keywords": c["category"] + " " + c["summary"]})
    idx += [
        {"title": "오시는 길 · 주차 안내", "url": "location.html", "type": "안내", "keywords": "주차 위치 주소 지도 길찾기 주성리 617 부영 부민빌딩 오창 2산단로 진료시간 야간 주말 공휴일"},
        {"title": "진료시간 · 예약 방법", "url": "faq.html", "type": "안내", "keywords": "진료시간 예약 네이버 카카오 전화 야간 주말 공휴일 365일"},
        {"title": "원장 소개", "url": "about.html", "type": "안내", "keywords": "원장 김현교 신재형 이상현 이력 진료요일 진료시간표 한의사"},
        {"title": "진료철학", "url": "philosophy.html", "type": "안내", "keywords": "진료 원칙 철학 치료 강도 반응 보정 설명"},
        {"title": "자주 묻는 질문", "url": "faq.html", "type": "안내", "keywords": "FAQ 질문 보험 실비 비용 한약 침 주차"},
    ]
    return idx


def jsonld(page_path, extra=None):
    data = {
        "@context": "https://schema.org",
        "@type": "MedicalClinic",
        "name": SITE["name"],
        "url": SITE["url"] + "/" + page_path,
        "telephone": "+82-" + SITE["phone"][1:],
        "image": SITE["url"] + "/images/hero/consult-monitor.webp",
        "logo": SITE["url"] + "/images/logo/symbol-green-512.png",
        "address": {"@type": "PostalAddress", "streetAddress": "오창읍 2산단로 132, 301·302호", "addressLocality": "청주시 청원구", "addressRegion": "충청북도", "postalCode": "28116", "addressCountry": "KR"},
        "geo": {"@type": "GeoCoordinates", "latitude": SITE["coords"]["lat"], "longitude": SITE["coords"]["lng"]},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "09:30", "closes": "20:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday", "Sunday", "PublicHolidays"], "opens": "09:30", "closes": "15:00"},
        ],
        "medicalSpecialty": "한의학",
        "sameAs": [SITE["naver_place_full"], SITE["kakao"], SITE["blog"]],
    }
    if extra:
        data = [data, extra]
    return json.dumps(data, ensure_ascii=False, indent=1)


def render(template, out_path, **ctx):
    depth = out_path.count("/")
    root = "../" * depth
    page_path = out_path
    base_ctx = dict(
        site=SITE, nav=NAV, services=SERVICES, conditions=CONDITIONS, columns=COLUMNS, directors=DIRECTORS,
        root=root, page_path=page_path, jsonld=ctx.pop("jsonld", None) or jsonld(page_path),
    )
    base_ctx.update(ctx)
    html = env.get_template(template).render(**base_ctx)
    full = os.path.join(OUT, out_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


def main():
    os.makedirs(OUT, exist_ok=True)
    pages = []

    # 홈
    pages.append(render("index.html", "index.html",
                        featured=FEATURED, ticker1=TICKER_ROW1, ticker2=TICKER_ROW2, ticker_links=TICKER_LINKS,
                        stats=STATS, core=CORE, who=WHO, why=WHY, home_faq=HOME_FAQ,
                        search_index=json.dumps(search_index(), ensure_ascii=False)))

    # 진료 안내
    pages.append(render("services_index.html", "services/index.html"))
    for s in SERVICES:
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in s["faq"]]}
        pages.append(render("service.html", f"services/{s['slug']}.html", s=s,
                            related_conditions=[COND[x] for x in s.get("related", []) if x in COND],
                            jsonld=jsonld(f"services/{s['slug']}.html", faq_ld)))

    # 질환 정보
    pages.append(render("conditions_index.html", "conditions/index.html", categories=CONDITION_CATEGORIES))
    for c in CONDITIONS:
        pages.append(render("condition.html", f"conditions/{c['slug']}.html", c=c,
                            related_services=[SVC[x] for x in c.get("services", []) if x in SVC]))

    # 칼럼
    pages.append(render("column_index.html", "column/index.html"))
    for c in COLUMNS:
        pages.append(render("column.html", f"column/{c['slug']}.html", c=c,
                            related_conditions=[COND[x] for x in c.get("related", []) if x in COND]))

    # 단일 페이지
    pages.append(render("about.html", "about.html", days=["월", "화", "수", "목", "금", "토", "일"]))
    pages.append(render("philosophy.html", "philosophy.html", principles=PRINCIPLES, patient_questions=PATIENT_QUESTIONS))
    lat, lng = SITE["coords"]["lat"], SITE["coords"]["lng"]
    bbox = f"{lng - 0.006:.6f}%2C{lat - 0.0035:.6f}%2C{lng + 0.006:.6f}%2C{lat + 0.0035:.6f}"
    pages.append(render("location.html", "location.html", bbox=bbox))
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for g in FAQ_GROUPS for q, a in g["items"]] +
                            [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in HOME_FAQ]}
    pages.append(render("faq.html", "faq.html", faq_groups=FAQ_GROUPS, home_faq=HOME_FAQ, jsonld=jsonld("faq.html", faq_ld)))
    pages.append(render("privacy.html", "privacy-policy.html"))

    # sitemap / robots
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for p in pages:
            loc = SITE["url"] + "/" + ("" if p == "index.html" else p)
            f.write(f"  <url><loc>{loc}</loc><changefreq>weekly</changefreq></url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")

    print(f"built {len(pages)} pages → {OUT}")


if __name__ == "__main__":
    main()
