#!/usr/bin/env python3
"""Generate the static Russian SEO article hub and 25 crawlable article pages."""
from __future__ import annotations

import json
import os
import re
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "articles" / "content.json"
TIPS_PATH = ROOT / "articles" / "tips.json"
PUBLISHED = os.environ.get("CONTENT_PUBLISHED", "2026-09-30")
TODAY = os.environ.get("CONTENT_DATE", "2026-10-24")
SITE_BASE = os.environ.get(
    "SITE_BASE_URL", "https://semyazdrav.ru"
).rstrip("/") + "/"
PRODUCT_URL = "https://www.wildberries.ru/catalog/784598331/detail.aspx"


def e(value: str) -> str:
    return escape(str(value), quote=True)


def render_inline(text: str) -> str:
    """Escape text, expanding [[slug|label]] article links and [[product|label]]."""
    parts = re.split(r"\[\[([a-z0-9-]+)\|([^\]]+)\]\]", str(text))
    out = [e(parts[0])]
    for i in range(1, len(parts), 3):
        slug, label = parts[i], parts[i + 1]
        href = "../../index.html#product" if slug == "product" else f"../{slug}/"
        out.append(f'<a href="{href}">{e(label)}</a>')
        out.append(e(parts[i + 2]))
    return "".join(out)


COVER_BY_CATEGORY = {
    "Базовый уход": ("botanical/watering", "Полив комнатного растения из лейки"),
    "Состав и дозировка": ("botanical/droplet-leaf", "Капля воды на зелёном листе крупным планом"),
    "Виды растений": ("plants/leafy", "Монстера и другие декоративно-лиственные растения"),
    "Проблемы растений": ("botanical/yellow-leaf", "Лист комнатного растения с пожелтевшим краем"),
    "Рассада": ("plants/seedlings", "Молодая рассада в горшочках на подоконнике"),
}
COVER_OVERRIDES = {
    # Базовый уход: не одна и та же лейка на все пять статей.
    "udobrenie-dlya-komnatnyh-rasteniy": ("botanical/hero-plants", "Домашний сад из комнатных растений на полке у окна"),
    "kak-chasto-podkarmlivat-komnatnye-rasteniya": ("botanical/watering", "Полив комнатного растения из лейки"),
    "podkormka-rasteniy-posle-peresadki": ("botanical/repotting", "Руки пересаживают комнатное растение с земляным комом в терракотовый горшок"),
    "komnatnye-rasteniya-zimoy-uhod-podkormka": ("botanical/winter-windowsill", "Комнатные растения в горшках на деревянном подоконнике зимой"),
    "uhod-za-komnatnymi-rasteniyami-vesnoy": ("botanical/soil-sprout", "Руки держат тёмную почву с маленьким зелёным ростком"),
    # Состав и дозировка: доза, опрыскивание, капля и почва вместо одного макро-листа.
    "kak-razvodit-zhidkoe-udobrenie": ("botanical/measuring-dose", "Руки наливают отмеренную жидкость из стеклянной ёмкости в лейку"),
    "kornevaya-i-vnekornevaya-podkormka-rasteniy": ("botanical/watering", "Полив комнатного растения из лейки"),
    "mozhno-li-opryskivat-rasteniya-udobreniem": ("botanical/spraying-leaves", "Рука опрыскивает листья комнатного растения из пульверизатора"),
    "chto-takoe-npk-v-udobrenii": ("botanical/droplet-leaf", "Капля воды на зелёном листе крупным планом"),
    "guminovye-i-fulvovye-kisloty-dlya-rasteniy": ("botanical/soil-sprout", "Руки держат тёмную почву с маленьким зелёным ростком"),
    "yantarnaya-kislota-dlya-komnatnyh-rasteniy": ("botanical/measuring-dose", "Руки наливают отмеренную жидкость из стеклянной ёмкости в лейку"),
    "aminokisloty-i-vitaminy-dlya-rasteniy": ("plants/leafy", "Монстера и другие декоративно-лиственные растения"),
    "organicheskoe-ili-mineralnoe-udobrenie": ("botanical/soil-sprout", "Руки держат тёмную почву с маленьким зелёным ростком"),
    # Виды растений: по возможности именно то растение, о котором статья.
    "udobrenie-dlya-orhidei": ("plants/orchid", "Цветущий фаленопсис в горшке на подоконнике"),
    "udobrenie-dlya-fialok": ("plants/violets", "Цветущие фиалки в горшках на светлом подоконнике"),
    "udobrenie-dlya-fikusa": ("plants/ficus", "Фикус Бенджамина в светлом горшке у окна"),
    "podkormka-monstery-i-dekorativno-listvennyh": ("plants/leafy", "Монстера и другие декоративно-лиственные растения"),
    "podkormka-tsvetushchih-rasteniy": ("plants/violets", "Цветущие фиалки в горшках на светлом подоконнике"),
    "udobrenie-dlya-palm": ("plants/palm", "Комнатная пальма в плетёном кашпо у окна"),
    "komnatnyy-limon-podkormka-i-uhod": ("botanical/hero-plants", "Комнатные растения на полке у светлого окна"),
    # Рассада и проблемы.
    "udobrenie-dlya-rassady-v-domashnih-usloviyah": ("plants/seedlings", "Молодая рассада в горшочках на подоконнике"),
    "podkormka-rassady-posle-pikirovki": ("botanical/repotting", "Руки пересаживают комнатное растение с земляным комом в терракотовый горшок"),
    "zhelteyut-listya-komnatnyh-rasteniy": ("botanical/yellow-leaf", "Лист комнатного растения с пожелтевшим краем"),
    "priznaki-nehvatki-pitaniya-u-rasteniy": ("botanical/leaf-inspection", "Рука осматривает лист комнатного растения с бледными участками между жилками"),
    "izbytok-udobreniya-priznaki-i-pomoshch": ("botanical/measuring-dose", "Руки наливают отмеренную жидкость из стеклянной ёмкости в лейку"),
}


def cover_for(article: dict) -> tuple[str, str]:
    return COVER_OVERRIDES.get(article["slug"], COVER_BY_CATEGORY[article["category"]])


def json_script(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def page_header(home_href: str, blog_href: str, product_href: str) -> str:
    return f'''<a class="skip-link" href="#main-content">К содержанию</a>
<div class="topline">Уход за растениями — просто и бережно</div>
<header class="site-header">
  <a class="brand" href="{home_href}" aria-label="Семяздрав — на главную"><span class="brand__mark" aria-hidden="true">✳</span><span>семя<b>здрав</b></span></a>
  <nav aria-label="Основная навигация"><a href="{blog_href}">Все статьи</a><a href="{product_href}">О продукте</a><a href="{PRODUCT_URL}" target="_blank" rel="noopener noreferrer">Wildberries ↗</a></nav>
</header>'''


def faq_schema(article: dict) -> dict:
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in article.get("faq", [])
        ],
    }


def breadcrumb_schema(items: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": index, "name": name, "item": url}
            for index, (name, url) in enumerate(items, 1)
        ],
    }


def render_article(article: dict, all_articles: list[dict], tips: dict[str, str]) -> str:
    slug = article["slug"]
    title = article["title"]
    description = article["description"]
    canonical = f"{SITE_BASE}articles/{quote(slug)}/"
    root_url = SITE_BASE
    blog_url = f"{SITE_BASE}articles/"
    home_href = "../../index.html"
    blog_href = "../"
    product_href = "../../index.html#product"
    published = article.get("published", PUBLISHED)
    updated = article.get("updated", published)
    cover_path, cover_alt = cover_for(article)
    cover_name = cover_path.rsplit("/", 1)[-1]
    cover_og = f"{SITE_BASE}public/images/og/{cover_name}-1200x630.jpg"
    page_title = f"{title} — Семяздрав"
    reading_text = " ".join([
        article["lead"],
        tips[slug],
        *(section["heading"] + " " + " ".join(section.get("paragraphs", [])) for section in article["sections"]),
        *(question + " " + answer for question, answer in article.get("faq", [])),
    ])
    reading_minutes = max(1, (len(re.findall(r"[\wЁё-]+", reading_text)) + 179) // 180)

    toc = []
    sections_html = []
    for index, section in enumerate(article["sections"], 1):
        section_id = f"section-{index}"
        toc.append(f'<a href="#{section_id}">{e(section["heading"])}</a>')
        paragraphs = "\n".join(f"<p>{render_inline(text)}</p>" for text in section.get("paragraphs", []))
        bullets = section.get("bullets", [])
        list_html = ""
        if bullets:
            list_html = "<ul>" + "".join(f"<li>{render_inline(item)}</li>" for item in bullets) + "</ul>"
        sections_html.append(
            f'<section class="article-section" id="{section_id}"><h2>{e(section["heading"])}</h2>{paragraphs}{list_html}</section>'
        )

    faqs = article.get("faq", [])
    faq_html = ""
    if faqs:
        faq_html = '<section class="article-faq"><h2>Частые вопросы</h2>' + "".join(
            f'<details><summary>{e(question)}</summary><p>{render_inline(answer)}</p></details>'
            for question, answer in faqs
        ) + "</section>"

    sources = article.get("sources", [])
    sources_html = ""
    if sources:
        sources_html = '<aside class="sources"><h2>Источники и дополнительное чтение</h2><ul>' + "".join(
            f'<li><a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(name)} ↗</a></li>'
            for name, url in sources
        ) + "</ul></aside>"

    tip_html = f'<aside class="article-tip"><span>ПРАКТИЧЕСКИЙ СОВЕТ</span><p>{render_inline(tips[slug])}</p></aside>'

    # Same-category pages are useful next reads; fill to three with nearby content.
    related = [x for x in all_articles if x["slug"] != slug and x["category"] == article["category"]]
    if len(related) < 3:
        related += [x for x in all_articles if x["slug"] != slug and x not in related]
    related = related[:3]
    related_html = "".join(
        f'<a class="related-card" href="../{e(item["slug"])}/"><span>{e(item["category"])}</span><b>{e(item["title"])}</b><i>Читать →</i></a>'
        for item in related
    )

    crumbs = breadcrumb_schema([
        ("Главная", root_url),
        ("Статьи", blog_url),
        (title, canonical),
    ])
    article_schema = {
        "@type": "Article",
        "headline": title,
        "description": description,
        "inLanguage": "ru-RU",
        "datePublished": published,
        "dateModified": updated,
        "image": cover_og,
        "mainEntityOfPage": canonical,
        "author": {"@type": "Organization", "name": "Семяздрав"},
        "publisher": {"@type": "Organization", "name": "Семяздрав", "logo": {"@type": "ImageObject", "url": f"{SITE_BASE}public/images/icon-512.png"}},
        "articleSection": article["category"],
        "keywords": article["query"],
    }
    graph = [article_schema, crumbs]
    if faqs:
        graph.append(faq_schema(article))

    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f7f6ef">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<link rel="icon" type="image/svg+xml" href="../../favicon.svg">
<meta property="og:site_name" content="Семяздрав">
<meta property="og:type" content="article">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{e(page_title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(cover_og)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:alt" content="{e(cover_alt)} (иллюстрация)">
<meta property="article:published_time" content="{published}">
<meta property="article:modified_time" content="{updated}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(page_title)}">
<meta name="twitter:description" content="{e(description)}">
<meta name="twitter:image" content="{e(cover_og)}">
<meta name="twitter:image:alt" content="{e(cover_alt)} (иллюстрация)">
<title>{e(page_title)}</title>
<link rel="icon" type="image/png" sizes="192x192" href="../../public/images/icon-192.png"><link rel="apple-touch-icon" sizes="180x180" href="../../public/images/apple-touch-icon.png"><link rel="manifest" href="../../manifest.webmanifest">
<link rel="preload" href="../../public/fonts/manrope-cyrillic-400-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="../../public/fonts/fonts.css">
<link rel="stylesheet" href="../assets/articles.css">
<script type="application/ld+json">{json_script({"@context":"https://schema.org","@graph":graph})}</script>
</head>
<body>
{page_header(home_href, blog_href, product_href)}
<main class="article-shell" id="main-content">
  <div class="breadcrumbs"><a href="{home_href}">Главная</a><span aria-hidden="true">/</span><a href="{blog_href}">Статьи</a><span aria-hidden="true">/</span><span>{e(title)}</span></div>
  <div class="article-layout">
    <article class="article">
      <header class="article-header"><p class="eyebrow">{e(article["category"])} <span>·</span> {reading_minutes} мин чтения</p><h1>{e(title)}</h1><p class="article-lead">{e(article["lead"])}</p><p class="article-updated">Материал обновлён {updated[8:10]}.{updated[5:7]}.{updated[:4]} · Справочная информация, не заменяет инструкцию на упаковке.</p></header>
      <figure class="article-cover"><picture><source type="image/webp" srcset="../../public/images/{cover_path}-480.webp 480w, ../../public/images/{cover_path}-800.webp 800w" sizes="(max-width: 720px) 100vw, 760px"><img src="../../public/images/{cover_path}-800.jpg" srcset="../../public/images/{cover_path}-480.jpg 480w, ../../public/images/{cover_path}-800.jpg 800w" sizes="(max-width: 720px) 100vw, 760px" width="800" height="436" alt="{e(cover_alt)}" fetchpriority="high"></picture><figcaption>{e(cover_alt)} — иллюстрация. Фото самого флакона — на <a href="{product_href}">главной странице</a>.</figcaption></figure>
      <nav class="toc" aria-label="Содержание статьи"><b>В статье</b>{''.join(toc)}</nav>
      {''.join(sections_html)}
      {tip_html}
      {faq_html}
      {sources_html}
      <aside class="product-callout"><span class="callout-kicker">УНИВЕРСАЛЬНЫЙ КОНЦЕНТРАТ</span><h2>Питание для домашнего сада</h2><p>Семяздрав — жидкое удобрение для комнатных растений, цветов и рассады. Подберите дозировку по инструкции на флаконе.</p><a href="{PRODUCT_URL}" target="_blank" rel="noopener noreferrer" class="button">Открыть карточку товара на Wildberries <span>↗</span></a><small>Актуальные цена, наличие и сведения о продавце — на площадке.</small></aside>
    </article>
    <aside class="article-aside"><div class="aside-sticky"><p>КРАТКО</p><b>Следуйте этикетке</b><span>Нормы и частота зависят от растения, грунта и конкретного удобрения.</span><a href="{product_href}">О продукте Семяздрав ↗</a></div></aside>
  </div>
  <section class="related"><div class="related-heading"><div><p class="eyebrow">ЧИТАЙТЕ ТАКЖЕ</p><h2>Ещё полезное</h2></div><a href="{blog_href}">Все статьи →</a></div><div class="related-grid">{related_html}</div></section>
</main>
<footer class="footer"><a class="footer-brand" href="{home_href}">семяздрав</a><span>Здоровый рост начинается с заботы.</span><nav class="footer__links" aria-label="Служебная навигация"><a href="../../about-product.html">О продукте</a><a href="../../editorial-policy.html">Редакционная политика</a><a href="../../privacy.html">Конфиденциальность</a><a href="{blog_href}">База знаний</a><a href="{home_href}#top">Наверх ↑</a></nav></footer>
</body>
</html>
'''


def render_index(articles: list[dict]) -> str:
    canonical = f"{SITE_BASE}articles/"
    cards = []
    for article in articles:
        search_text = " ".join((article["title"], article["query"], article["category"], article["description"]))
        _cover_path, _cover_alt = cover_for(article)
        cards.append(f'''<article class="article-card" data-category="{e(article["category"])}" data-search="{e(search_text.lower())}">
<a class="article-card__link" href="{e(article["slug"])}/"><span class="article-card__media"><picture><source type="image/webp" srcset="../public/images/{_cover_path}-480.webp"><img src="../public/images/{_cover_path}-480.jpg" width="480" height="262" alt="" loading="lazy"></picture></span><span class="article-card__category">{e(article["category"])}</span><h2>{e(article["title"])}</h2><p>{e(article["description"])}</p><span class="article-card__read">Читать статью <b>↗</b></span></a>
</article>''')

    categories = []
    for article in articles:
        if article["category"] not in categories:
            categories.append(article["category"])
    filters = '<button class="filter is-active" type="button" data-filter="all" aria-pressed="true">Все темы</button>' + "".join(
        f'<button class="filter" type="button" data-filter="{e(category)}" aria-pressed="false">{e(category)}</button>'
        for category in categories
    )
    collection_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Советы по уходу за растениями — Семяздрав",
        "description": "Практические статьи об удобрениях, комнатных растениях, рассаде и уходе.",
        "url": canonical,
        "inLanguage": "ru-RU",
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(articles),
            "itemListElement": [
                {"@type": "ListItem", "position": i, "url": f"{SITE_BASE}articles/{article['slug']}/", "name": article["title"]}
                for i, article in enumerate(articles, 1)
            ],
        },
    }
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f7f6ef">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="description" content="25 понятных статей об удобрениях, комнатных растениях, рассаде и уходе. Дозировки, сезонные советы и разбор частых проблем.">
<link rel="canonical" href="{e(canonical)}"><link rel="icon" type="image/svg+xml" href="../favicon.svg">
<meta property="og:site_name" content="Семяздрав"><meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:title" content="Советы по уходу за растениями — Семяздрав"><meta property="og:description" content="25 практических статей для домашнего сада, комнатных растений и рассады."><meta property="og:url" content="{e(canonical)}"><meta property="og:image" content="{e(SITE_BASE)}public/images/og/library-hero-1200x630.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:alt" content="Семяздрав — база знаний по уходу за растениями"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Советы по уходу за растениями — Семяздрав"><meta name="twitter:description" content="25 практических статей для домашнего сада, комнатных растений и рассады."><meta name="twitter:image" content="{e(SITE_BASE)}public/images/og/library-hero-1200x630.jpg"><meta name="twitter:image:alt" content="Семяздрав — база знаний по уходу за растениями">
<title>Советы по уходу за растениями: 25 статей — Семяздрав</title>
<link rel="icon" type="image/png" sizes="192x192" href="../public/images/icon-192.png"><link rel="apple-touch-icon" sizes="180x180" href="../public/images/apple-touch-icon.png"><link rel="manifest" href="../manifest.webmanifest">
<link rel="preload" href="../public/fonts/manrope-cyrillic-400-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="../public/fonts/fonts.css">
<link rel="stylesheet" href="assets/articles.css"><script src="assets/articles.js" defer></script>
<script type="application/ld+json">{json_script(collection_schema)}</script>
</head>
<body>
{page_header("../index.html", "./", "../index.html#product")}
<main id="main-content">
<section class="library-hero"><div class="library-hero__inner"><p class="eyebrow">БАЗА ЗНАНИЙ СЕМЯЗДРАВ</p><h1>Растениям —<br><em>понятный уход.</em></h1><p>Практические ответы о подкормках, дозировках и уходе за комнатными растениями и рассадой — без обещаний чудес и советов «на глаз».</p><div class="library-stats"><span><b>{len(articles)}</b> статей</span><span><b>{len(categories)}</b> тематических разделов</span><span>Обновлено {TODAY[8:10]}.{TODAY[5:7]}.{TODAY[:4]}</span></div></div><figure class="library-hero__media"><picture><source type="image/webp" srcset="../public/images/botanical/library-hero-480.webp 480w, ../public/images/botanical/library-hero-800.webp 800w, ../public/images/botanical/library-hero-1200.webp 1200w" sizes="(max-width: 640px) 100vw, 48vw"><img src="../public/images/botanical/library-hero-800.jpg" srcset="../public/images/botanical/library-hero-480.jpg 480w, ../public/images/botanical/library-hero-800.jpg 800w, ../public/images/botanical/library-hero-1200.jpg 1200w" sizes="(max-width: 640px) 100vw, 48vw" width="1200" height="654" alt="" fetchpriority="high"></picture></figure></section>
<section class="library section-wrap"><div class="library-toolbar"><div><p class="eyebrow">ВЫБЕРИТЕ ТЕМУ</p><h2>Полезные статьи</h2></div><label class="search-box"><span class="visually-hidden">Поиск по статьям</span><input id="article-search" type="search" placeholder="Например, орхидеи…"><svg class="search-box__icon" aria-hidden="true" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg></label></div>
<div class="filters" aria-label="Фильтр статей">{filters}</div>
<div class="article-grid" id="article-grid">{''.join(cards)}</div>
<p class="no-results" id="no-results" hidden>По этому запросу статей не найдено. Попробуйте другое слово.</p>
<p class="visually-hidden" id="search-status" aria-live="polite"></p>
</section>
<section class="library-cta"><div><p class="eyebrow">ПОДКОРМКА ДЛЯ ДОМАШНЕГО САДА</p><h2>Семяздрав — один концентрат<br>для разных растений.</h2><p>Состав, применение и актуальная карточка товара — на странице продукта.</p></div><a href="../index.html#product" class="button">Узнать о продукте <span>↗</span></a></section>
</main>
<footer class="footer"><a class="footer-brand" href="../index.html">семяздрав</a><span>Здоровый рост начинается с заботы.</span><nav class="footer__links" aria-label="Служебная навигация"><a href="../about-product.html">О продукте и продавце</a><a href="../editorial-policy.html">Редакционная политика</a><a href="../privacy.html">Конфиденциальность</a><a href="../index.html#top">На главную ↑</a></nav></footer>
</body>
</html>
'''


def render_robots_and_sitemap(articles: list[dict]) -> None:
    sitemap_entries = [(SITE_BASE, "1.0", TODAY), (f"{SITE_BASE}articles/", "0.9", TODAY),
                       (f"{SITE_BASE}about-product.html", "0.7", TODAY), (f"{SITE_BASE}editorial-policy.html", "0.5", TODAY)]
    sitemap_entries.extend(
        (f"{SITE_BASE}articles/{quote(article['slug'])}/", "0.8", article.get("updated", article.get("published", PUBLISHED)))
        for article in articles
    )
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, priority, lastmod in sitemap_entries:
        sitemap.append(f"  <url><loc>{e(url)}</loc><lastmod>{lastmod}</lastmod><priority>{priority}</priority></url>")
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + SITE_BASE + "sitemap.xml\n",
        encoding="utf-8",
    )


def render_seo_plan(articles: list[dict]) -> None:
    lines = [
        "# SEO-контент-план: 25 статей «Семяздрав»",
        "",
        "Материалы ориентированы на информационные и коммерческие запросы по подкормке комнатных растений и рассады. Частотность и конкуренция не заявлены: перед масштабированием кластеров проверьте их через Яндекс Wordstat, Google Search Console и Яндекс Вебмастер.",
        "",
        "| № | Основной запрос | Заголовок | Раздел | URL |",
        "|---:|---|---|---|---|",
    ]
    for i, article in enumerate(articles, 1):
        url = f"{SITE_BASE}articles/{article['slug']}/"
        lines.append(f"| {i} | {article['query']} | {article['title']} | {article['category']} | [{article['slug']}]({url}) |")
    lines += [
        "",
        "## Перед публикацией",
        "",
        "- Проверьте факты о составе, норме и периодичности по этикетке текущего товара.",
        "- Главная и статьи используют OG/Twitter Card с уникальными заголовками и описаниями; у главной — обложка с настоящим флаконом `public/images/og-cover.jpg` (1200 × 630), у статей — тематические обложки `public/images/og/*-1200x630.jpg`.",
        "- Фото флакона на сайте — настоящее, из карточки Wildberries (см. `public/images/SOURCES.md`); при замене фото сохраняйте пропорцию OG-обложки и пересоберите статьи. Запуск проверок: `make check`.",
        "- Подключите Google Search Console и Яндекс Вебмастер, подтвердите домен, отправьте `sitemap.xml` и отслеживайте показы, клики и заявки.",
        "- Для коммерческих целей используйте официальную карточку продавца, актуальные цену и наличие; не обещайте гарантированный рост или цветение.",
        "- Измеряйте клики по карточке товара, но не добавляйте непроверенные отзывы, цены и контактные данные.",
        "",
        "## Пересборка страниц",
        "",
        "Запустите `python3 scripts/build_articles.py`. Чтобы использовать другой канонический адрес, задайте `SITE_BASE_URL`, например `SITE_BASE_URL=https://example.ru`.",
        "",
    ]
    (ROOT / "SEO_PLAN.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    articles = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    tips = json.loads(TIPS_PATH.read_text(encoding="utf-8"))
    if len(articles) != 25:
        raise SystemExit(f"Expected exactly 25 articles, got {len(articles)}")
    slugs = [item["slug"] for item in articles]
    if len(set(slugs)) != len(slugs):
        raise SystemExit("Article slugs must be unique")
    if set(slugs) != set(tips):
        missing = sorted(set(slugs) - set(tips))
        extra = sorted(set(tips) - set(slugs))
        raise SystemExit(f"Article tips mismatch; missing={missing}, extra={extra}")
    for item in articles:
        if not re.fullmatch(r"[a-z0-9-]+", item["slug"]):
            raise SystemExit(f"Slug must contain only latin lowercase, digits and hyphens: {item['slug']}")
        out_dir = ROOT / "articles" / item["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(render_article(item, articles, tips), encoding="utf-8")
    (ROOT / "articles" / "index.html").write_text(render_index(articles), encoding="utf-8")
    render_robots_and_sitemap(articles)
    render_seo_plan(articles)
    print(f"Generated {len(articles)} article pages and SEO metadata under {ROOT}")


if __name__ == "__main__":
    main()
