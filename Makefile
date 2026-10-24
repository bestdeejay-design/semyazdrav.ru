.PHONY: build check serve

build:
	python3 scripts/build_articles.py

check: build
	python3 scripts/check_site.py
	python3 -m json.tool articles/content.json >/dev/null
	python3 -m json.tool articles/tips.json >/dev/null
	python3 -m json.tool manifest.webmanifest >/dev/null

serve:
	python3 -m http.server 4173
