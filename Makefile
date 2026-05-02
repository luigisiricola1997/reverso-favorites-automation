.PHONY: install run dry test lint clean help

PY := .venv/bin/python
PIP := .venv/bin/pip
WORDS ?= words.txt

help:
	@echo "Targets:"
	@echo "  make install                  Create .venv, install deps and Chromium"
	@echo "  make run [WORDS=path.txt]     Run live (default: words.txt)"
	@echo "  make dry [WORDS=path.txt]     Dry-run: visit pages, do not click favorites"
	@echo "  make test                     Smoke check: import + CLI help + load_words"
	@echo "  make clean                    Remove .venv, __pycache__, screenshots"

install:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PY) -m playwright install chromium

run:
	$(PY) reverso_translate.py $(WORDS)

dry:
	$(PY) reverso_translate.py $(WORDS) --dry-run

test:
	$(PY) -c "import reverso_translate; print('import ok')"
	$(PY) reverso_translate.py --help > /dev/null && echo "cli ok"
	$(PY) -c "from pathlib import Path; from reverso_translate import load_words; w,s=load_words(Path('$(WORDS)')); print(f'load_words ok: {len(w)} words, {len(s)} skipped')"

clean:
	rm -rf .venv __pycache__ *.pyc _debug_*.png _smoke_*.png
