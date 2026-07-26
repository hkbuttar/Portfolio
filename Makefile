.PHONY: install build serve test clean new-project new-course

install:
	pip install -r requirements.txt --break-system-packages 2>/dev/null || pip install -r requirements.txt

build:
	python3 build.py

serve: build
	@echo "Serving at http://localhost:8000 — Ctrl+C to stop"
	python3 -m http.server 8000

test:
	python3 -m unittest tests.test_content -v

clean:
	rm -f index.html projects.html coursework.html sitemap.xml
	rm -rf projects/*.html coursework/*.html

new-project:
	@test -n "$(SLUG)" || (echo "usage: make new-project SLUG=my-new-project"; exit 1)
	python3 scripts/new_entry.py project $(SLUG)

new-course:
	@test -n "$(SLUG)" || (echo "usage: make new-course SLUG=my-new-course"; exit 1)
	python3 scripts/new_entry.py coursework $(SLUG)
