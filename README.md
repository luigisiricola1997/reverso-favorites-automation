# reverso-favorites-automation

Batch-add words to your [Reverso Context](https://context.reverso.net) favorites from a text file. Useful when you have a stack of new vocabulary from a book, podcast, or class and you do not want to click "save" 30 times by hand.

## Who is this for

Language learners who already use Reverso Context as their vocabulary stash and want to script the boring part of growing it.

## Quickstart

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # then edit with your Reverso credentials
python reverso_translate.py words.txt
```

## Usage

```
python reverso_translate.py [WORDS_FILE] [--lang-pair PAIR] [--headless|--no-headless] [--dry-run] [--delay SECONDS]
```

Defaults: `words.txt`, `english-italian`, headless on, no dry-run, 2s between words.

Examples:

```sh
# Default: read words.txt, english <-> italian, headless
python reverso_translate.py

# Other language pair, with the browser visible (handy for debugging)
python reverso_translate.py my-words.txt --lang-pair english-french --no-headless

# Dry-run: visit each page and verify the favorite button is found, but do not click
python reverso_translate.py --dry-run

# Slow it down to be polite
python reverso_translate.py --delay 5
```

The script prints a per-word OK/FAIL line and a summary at the end. Exit code:
`0` all word added, `1` config/file errors, `2` login failed, `3` some words failed.

## Words file format

One word or phrase per line. Blank lines and duplicates are skipped automatically.

```
stall
to be squashed
to feel numb
oven
```

## How it works

Playwright opens a Chromium browser (headless by default), logs into Reverso using credentials from `.env`, then for each word visits `context.reverso.net/translation/<lang-pair>/<word>` and clicks the favorite button. Two consecutive clicks are needed because the Reverso UI requires it (observed empirically; if it stops working, re-record with `playwright codegen`).

## Notes

- This is a personal-use script.
- Do not point it at huge word lists: keep it to a few dozen words at a time, leave the default `--delay`, and respect Reverso's terms of service.
  The script is not affiliated with Reverso.
- Headless mode works on Linux/macOS/Windows.
  WSL2 works.
- Credentials live in `.env` (gitignored).
  Use `.env.example` as a template.

## License

MIT. See [LICENSE](LICENSE).
