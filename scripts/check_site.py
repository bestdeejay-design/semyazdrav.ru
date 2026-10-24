#!/usr/bin/env python3
"""Static checks for semyazdrav.ru (zero dependencies, Python 3).

Verifies product-link policy, internal links/anchors, canonicals, sitemap,
meta uniqueness/lengths, image attributes and sizes, JSON-LD, manifest,
fonts self-hosting and repository invariants. Exit 1 with file references
on any violation. Run: python3 scripts/check_site.py
"""
from __future__ import annotations

import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://semyazdrav.ru"
PRODUCT_URL = "https://www.wildberries.ru/catalog/784598331/detail.aspx"
errors: list[str] = []


def err(path: Path | str, message: str, line: int | None = None) -> None:
    loc = str(path.relative_to(ROOT)) if isinstance(path, Path) else path
    errors.append(f"{loc}:{line}: {message}" if line else f"{loc}: {message}")


class Page(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids: set[str] = set()
        self.refs: list[tuple[str, str, int, dict]] = []  # tag, ref, line, attrs
        self.imgs: list[tuple[dict, int]] = []
        self.canonicals: list[str] = []
        self.title = ""
        self.description = ""
        self.robots = ""
        self.ldjson: list[str] = []
        self._in_title = False
        self._ld: list[str] | None = None

    def handle_starttag(self, tag: str, attrs_list) -> None:
        attrs = dict(attrs_list)
        line = self.getpos()[0]
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "title":
            self._in_title = True
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._ld = []
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "")
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content", "")
        if tag == "link" and "canonical" in (attrs.get("rel") or ""):
            self.canonicals.append(attrs.get("href", ""))
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.refs.append((tag, attrs[attr], line, attrs))
        if attrs.get("srcset"):
            for part in attrs["srcset"].split(","):
                url = part.strip().split()
                if url:
                    self.refs.append((tag, url[0], line, attrs))
        if tag == "img":
            self.imgs.append((attrs, line))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._ld is not None:
            self.ldjson.append("".join(self._ld))
            self._ld = None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._ld is not None:
            self._ld.append(data)


def jpeg_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            return None
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return (w, h)
        if i + 3 >= len(data):
            return None
        seg = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg
    return None


def png_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def main() -> int:
    html_files = sorted(
        p for p in ROOT.rglob("*.html")
        if ".git" not in p.parts and "image-search" not in p.parts
    )
    if not html_files:
        print("No HTML files found", file=sys.stderr)
        return 1
    pages: dict[Path, Page] = {}
    for path in html_files:
        page = Page(path)
        page.feed(path.read_text(encoding="utf-8"))
        pages[path] = page

    def resolve(page_path: Path, raw: str):
        """Return (target_file, fragment) for a local ref or None if external/skipped."""
        if not raw or raw.startswith(("mailto:", "tel:", "data:", "javascript:")):
            return None
        parsed = urlparse(raw)
        if parsed.scheme in ("http", "https"):
            return None
        frag = parsed.fragment
        ref_path = unquote(parsed.path)
        if not ref_path:
            return (page_path, frag)
        if ref_path.startswith("/"):
            target = ROOT / ref_path.lstrip("/")
        else:
            target = (page_path.parent / ref_path)
        target = Path(str(target).replace("\\", "/"))
        # normalise ../ segments without resolving symlinks outside ROOT assumptions
        try:
            target = target.resolve()
        except OSError:
            pass
        if ref_path.endswith("/") or target.is_dir():
            target = target / "index.html"
        elif not target.exists() and target.suffix == "":
            if (target / "index.html").exists():
                target = target / "index.html"
            elif target.with_suffix(".html").exists():
                target = target.with_suffix(".html")
        return (target, frag)

    wb_count = 0
    external_count = 0
    titles: dict[str, Path] = {}
    descriptions: dict[str, Path] = {}
    for path, page in pages.items():
        rel = path.relative_to(ROOT)
        # title / description
        if not page.title.strip():
            err(path, "empty <title>")
        elif page.title.strip() in titles:
            err(path, f"duplicate <title> also in {titles[page.title.strip()]}")
        else:
            titles[page.title.strip()] = rel
        if not page.description.strip():
            err(path, "empty meta description")
        elif page.description.strip() in descriptions:
            err(path, f"duplicate meta description also in {descriptions[page.description.strip()]}")
        else:
            descriptions[page.description.strip()] = rel
        # canonical
        if path.name == "404.html":
            if "noindex" not in page.robots:
                err(path, "404 page must be noindex")
        else:
            if len(page.canonicals) != 1:
                err(path, f"expected exactly 1 canonical, found {len(page.canonicals)}")
            elif not page.canonicals[0].startswith(BASE + "/"):
                err(path, f"canonical not on {BASE}: {page.canonicals[0]}")
        # JSON-LD
        for block in page.ldjson:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                err(path, f"invalid JSON-LD: {exc}")
        # images
        for attrs, line in page.imgs:
            if "alt" not in attrs:
                err(path, "<img> without alt", line)
            if not (attrs.get("width") and attrs.get("height")):
                err(path, f"<img> without width/height: {attrs.get('src', '')[:90]}", line)
        # references
        for tag, ref, line, attrs in page.refs:
            parsed = urlparse(ref)
            if parsed.scheme in ("http", "https"):
                host = parsed.netloc.lower()
                if "wildberries.ru" in host:
                    wb_count += 1
                    if ref != PRODUCT_URL:
                        err(path, f"non-canonical Wildberries link: {ref}", line)
                if tag == "a" and "semyazdrav.ru" not in host:
                    external_count += 1
                    rel_attr = set((attrs.get("rel") or "").split())
                    if attrs.get("target") != "_blank" or not {"noopener", "noreferrer"} <= rel_attr:
                        err(path, f"external link without target=_blank rel='noopener noreferrer': {ref}", line)
                continue
            resolved = resolve(path, ref)
            if resolved is None:
                continue
            target, frag = resolved
            if not target.exists():
                err(path, f"broken local reference: {ref}", line)
                continue
            if frag and frag != "top" and target.suffix == ".html":
                target_page = pages.get(target)
                if target_page is None:
                    alt_page = Page(target)
                    alt_page.feed(target.read_text(encoding="utf-8"))
                    target_page = alt_page
                if frag not in target_page.ids:
                    err(path, f"anchor #{frag} not found in {target.relative_to(ROOT)} (from {ref})", line)

    # Invariants
    cname = ROOT / "CNAME"
    if not cname.exists() or cname.read_text(encoding="utf-8").strip() != "semyazdrav.ru":
        err("CNAME", "must contain exactly 'semyazdrav.ru'")
    if not (ROOT / ".nojekyll").exists():
        err(".nojekyll", "missing")
    for ext in ("*.html", "*.xml", "*.txt", "*.js", "*.css", "*.webmanifest"):
        for path in ROOT.rglob(ext):
            if ".git" in path.parts or "image-search" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "bestdeejay-design.github.io" in text:
                err(path, "forbidden github.io domain in published file")
            if path.suffix in (".html", ".css") and ("fonts.googleapis.com" in text or "fonts.gstatic.com" in text):
                err(path, "external Google Fonts reference (fonts must be self-hosted)")

    # Fonts referenced from fonts.css must exist
    fonts_css = ROOT / "public/fonts/fonts.css"
    if not fonts_css.exists():
        err("public/fonts/fonts.css", "missing")
    else:
        for fname in re.findall(r"url\(([^)]+\.woff2)\)", fonts_css.read_text(encoding="utf-8")):
            if not (fonts_css.parent / fname).exists():
                err(fonts_css, f"font file missing: {fname}")

    # Sitemap
    articles_data = json.loads((ROOT / "articles/content.json").read_text(encoding="utf-8"))
    tips = json.loads((ROOT / "articles/tips.json").read_text(encoding="utf-8"))
    expected = {BASE + "/", BASE + "/articles/", BASE + "/about-product.html", BASE + "/editorial-policy.html"}
    expected |= {f"{BASE}/articles/{a['slug']}/" for a in articles_data}
    try:
        tree = ET.parse(ROOT / "sitemap.xml")
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        found = {el.text.strip() for el in tree.getroot().findall(".//sm:loc", ns) if el.text}
    except Exception as exc:  # noqa: BLE001
        err("sitemap.xml", f"unparsable: {exc}")
        found = set()
    if found != expected:
        err("sitemap.xml", f"URL set mismatch. missing={sorted(expected - found)} extra={sorted(found - expected)}")

    # Articles meta + volume (A3/A5 outcomes)
    if len(articles_data) != 25:
        err("articles/content.json", f"expected 25 articles, got {len(articles_data)}")
    seen_titles: set[str] = set()
    seen_desc: set[str] = set()
    expanded = 0
    for article in articles_data:
        slug = article["slug"]
        if article["title"] in seen_titles:
            err("articles/content.json", f"{slug}: duplicate title")
        seen_titles.add(article["title"])
        if article["description"] in seen_desc:
            err("articles/content.json", f"{slug}: duplicate description")
        seen_desc.add(article["description"])
        if not (48 <= len(article["title"]) <= 65):
            err("articles/content.json", f"{slug}: title length {len(article['title'])} outside 48-65")
        if not (140 <= len(article["description"]) <= 160):
            err("articles/content.json", f"{slug}: description length {len(article['description'])} outside 140-160")
        text = article["lead"] + " " + tips.get(slug, "") + " " + " ".join(
            s["heading"] + " " + " ".join(s.get("paragraphs", [])) + " " + " ".join(s.get("bullets", []))
            for s in article["sections"]
        ) + " " + " ".join(q + " " + a for q, a in article.get("faq", []))
        words = len(re.findall(r"[\wЁё-]+", text, flags=re.UNICODE))
        links = len(re.findall(r"\[\[[a-z0-9-]+\|", json.dumps(article, ensure_ascii=False)))
        if words >= 700:
            expanded += 1
            if len(article.get("sources", [])) < 2:
                err("articles/content.json", f"{slug}: expanded article has <2 sources")
            if links < 2:
                err("articles/content.json", f"{slug}: expanded article has <2 contextual internal links")
    if expanded < 10:
        err("articles/content.json", f"expected at least 10 articles >=700 words, got {expanded}")

    # Image sizes & manifest
    og = ROOT / "public/images/og-cover.jpg"
    if not og.exists() or jpeg_size(og) != (1200, 630):
        err("public/images/og-cover.jpg", f"must be 1200x630, got {jpeg_size(og) if og.exists() else 'missing'}")
    for name, size in (("icon-512.png", (512, 512)), ("icon-192.png", (192, 192)), ("apple-touch-icon.png", (180, 180))):
        icon = ROOT / "public/images" / name
        if not icon.exists() or png_size(icon) != size:
            err(f"public/images/{name}", f"must be {size}, got {png_size(icon) if icon.exists() else 'missing'}")
    manifest = ROOT / "manifest.webmanifest"
    if not manifest.exists():
        err("manifest.webmanifest", "missing")
    else:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            for icon in data.get("icons", []):
                rel_icon = icon.get("src", "").lstrip("/")
                if not (ROOT / rel_icon).exists():
                    err("manifest.webmanifest", f"icon missing: {icon.get('src')}")
        except json.JSONDecodeError as exc:
            err("manifest.webmanifest", f"invalid JSON: {exc}")
    if not (ROOT / "public/images/product/wb-card-516.jpg").exists():
        err("public/images/product/wb-card-516.jpg", "real product photo derivative missing")
    if not (ROOT / "public/images/SOURCES.md").exists():
        err("public/images/SOURCES.md", "image provenance file missing")

    print(f"pages: {len(pages)} | Wildberries links: {wb_count} (all must be product {PRODUCT_URL}) | external links checked: {external_count}")
    print(f"sitemap URLs: {len(found)} | expanded articles (>=700 words): {expanded}")
    if errors:
        print(f"\nFAIL — {len(errors)} error(s):", file=sys.stderr)
        for item in errors:
            print(" -", item, file=sys.stderr)
        return 1
    print("OK — all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
