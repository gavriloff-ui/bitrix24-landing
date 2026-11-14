#!/usr/bin/env python3
"""Собирает JSON-LD разметку из фактического содержимого index.html.

Запуск:  python3 scripts/build-jsonld.py
Результат: блок <script type="application/ld+json"> в <head> файла index.html.
"""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

SITE = "https://sophia.su/"
TELEPHONE = "+7-8162-55-60-65"
EMAIL = "hello@sophia.su"

MARKER_START = '  <script type="application/ld+json">'
MARKER_END = '  </script>'


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_faq(source: str) -> list[dict]:
    pattern = re.compile(
        r"<summary[^>]*>(.*?)<span class=\"faq-plus.*?</summary>\s*<p[^>]*>(.*?)</p>",
        re.DOTALL,
    )
    items = []
    for question_html, answer_html in pattern.findall(source):
        question = strip_tags(question_html)
        answer = strip_tags(answer_html)
        if question and answer:
            items.append(
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
            )
    return items


def extract_prices(source: str) -> list[dict]:
    pattern = re.compile(
        r"<h3 class=\"text-lg font-bold\">([^<]+)</h3>\s*"
        r"<p class=\"mt-1 text-sm text-(?:ink/50|white/50)\">([^<]+)</p>\s*"
        r"<p class=\"mt-6 text-4xl font-extrabold\">([^<]+)</p>\s*"
        r"<p class=\"mt-1 text-sm text-(?:ink/50|white/50)\">([^<]+)</p>"
    )
    offers = []
    for name, audience, price, term in pattern.findall(source):
        digits = re.sub(r"[^\d]", "", price)
        if not digits:
            continue
        offer = {
            "@type": "Offer",
            "name": f"Внедрение Bitrix24 — пакет «{name}»",
            "description": f"{audience} · {term}",
            "price": digits,
            "priceCurrency": "RUB",
        }
        if price.strip().startswith("от"):
            offer["priceSpecification"] = {
                "@type": "PriceSpecification",
                "minPrice": digits,
                "priceCurrency": "RUB",
            }
        offers.append(offer)
    return offers


def build(source: str) -> dict:
    organization = {
        "@type": ["Organization", "ProfessionalService"],
        "@id": f"{SITE}#organization",
        "name": "Агентство «София»",
        "url": SITE,
        "logo": f"{SITE}brand/logo-tile-512.png",
        "image": f"{SITE}brand/logo-tile-512.png",
        "description": (
            "Внедрение Bitrix24 и 1С под ключ: CRM, задачи, аналитика, "
            "автоматизация, учёт и интеграции. Фиксированная смета и сроки в договоре."
        ),
        "telephone": TELEPHONE,
        "email": EMAIL,
        "priceRange": "от 90 000 ₽",
        "areaServed": {"@type": "Country", "name": "Россия"},
        "availableLanguage": "ru",
    }

    offers = extract_prices(source)
    if offers:
        organization["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": "Пакеты внедрения Bitrix24",
            "itemListElement": offers,
        }

    graph = [
        organization,
        {
            "@type": "WebSite",
            "@id": f"{SITE}#website",
            "url": SITE,
            "name": "София — внедрение Bitrix24 и 1С",
            "inLanguage": "ru-RU",
            "publisher": {"@id": f"{SITE}#organization"},
        },
        {
            "@type": "Service",
            "@id": f"{SITE}#service-1c",
            "name": "1С Франчайзинг: внедрение и сопровождение",
            "serviceType": "Внедрение 1С, доработка и сопровождение",
            "provider": {"@id": f"{SITE}#organization"},
            "areaServed": {"@type": "Country", "name": "Россия"},
            "description": (
                "Официальный франчайзи 1С: 1С:Бухгалтерия, 1С:ЗУП, 1С:УТ / ERP, "
                "интеграция 1С с Bitrix24, банком, ЭДО и маркетплейсами."
            ),
        },
        {
            "@type": "Service",
            "@id": f"{SITE}#service-bitrix24",
            "name": "Внедрение Bitrix24 под ключ",
            "serviceType": "Внедрение CRM, задач, аналитики и интеграций",
            "provider": {"@id": f"{SITE}#organization"},
            "areaServed": {"@type": "Country", "name": "Россия"},
            "description": (
                "Настройка CRM и воронок, задачи и проекты, автоматизация, "
                "дашборды и отчёты, обучение команды и поддержка после запуска."
            ),
        },
    ]

    faq = extract_faq(source)
    if faq:
        graph.append(
            {
                "@type": "FAQPage",
                "@id": f"{SITE}#faq",
                "mainEntity": faq,
            }
        )

    return {"@context": "https://schema.org", "@graph": graph}


def main() -> None:
    source = INDEX.read_text(encoding="utf-8")
    data = build(source)
    payload = json.dumps(data, ensure_ascii=False, indent=2)

    block = MARKER_START + "\n" + payload + "\n" + MARKER_END

    if MARKER_START in source:
        source = re.sub(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
            lambda _: block,
            source,
            flags=re.DOTALL,
        )
    else:
        source = source.replace("</head>", block + "\n</head>", 1)

    INDEX.write_text(source, encoding="utf-8")
    questions = len(data["@graph"][-1].get("mainEntity", [])) if data["@graph"][-1]["@type"] == "FAQPage" else 0
    offers = len(data["@graph"][0].get("hasOfferCatalog", {}).get("itemListElement", []))
    print(f"JSON-LD обновлён: {questions} вопросов FAQ, {offers} пакета в каталоге")


if __name__ == "__main__":
    main()
