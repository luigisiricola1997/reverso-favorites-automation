"""Batch-add words to your Reverso Context favorites."""

import argparse
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from playwright.sync_api import (
    Page,
    TimeoutError as PWTimeout,
    sync_playwright,
)

LOGIN_URL = "https://account.reverso.net/Account/Login"
TRANSLATION_URL = "https://context.reverso.net/translation/{lang_pair}/{word}"
FAVORITE_BUTTON = "button.save-fav"
DESKTOP_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def load_words(path: Path) -> tuple[list[str], list[str]]:
    """Return (unique_words_in_order, skipped_lines). Skips blanks and duplicates."""
    raw = path.read_text(encoding="utf-8").splitlines()
    seen: set[str] = set()
    words: list[str] = []
    skipped: list[str] = []
    for line in raw:
        w = line.strip()
        if not w:
            skipped.append("<empty>")
            continue
        if w in seen:
            skipped.append(w)
            continue
        seen.add(w)
        words.append(w)
    return words, skipped


class LoginFailed(Exception):
    """Reverso rejected the credentials."""


def login(page: Page, username: str, password: str) -> None:
    """Submit the Reverso login form and verify we are no longer on /Account/Login.
    Raises LoginFailed if Reverso shows the inline 'incorrect login' error."""
    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    page.fill("#Email", username)
    page.fill("#Password", password)
    page.click("button.btn-submit")
    try:
        page.wait_for_url(lambda url: "/Account/Login" not in url, timeout=10_000)
    except PWTimeout:
        err_loc = page.locator(".validation-summary-errors").first
        msg = err_loc.inner_text().strip() if err_loc.count() else "unknown reason"
        raise LoginFailed(msg)


def accept_cookies(page: Page) -> bool:
    """Dismiss the Didomi cookie consent banner on context.reverso.net.
    The accept cookie persists for the rest of the BrowserContext, so this
    only needs to run once per session. Returns True if dismissed, False
    if no banner was found within the timeout."""
    page.goto("https://context.reverso.net/", wait_until="domcontentloaded")
    try:
        page.locator("#didomi-notice-agree-button").click(timeout=5_000)
        return True
    except PWTimeout:
        return False


def add_to_favorites(page: Page, word: str, lang_pair: str, dry_run: bool) -> None:
    url = TRANSLATION_URL.format(lang_pair=lang_pair, word=quote(word))
    page.goto(url, wait_until="domcontentloaded")

    button = page.locator(FAVORITE_BUTTON).first
    button.wait_for(state="visible", timeout=10_000)

    if dry_run:
        return

    button.click()
    button.click()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch-add words to your Reverso Context favorites."
    )
    parser.add_argument(
        "words_file",
        type=Path,
        nargs="?",
        default=Path("words.txt"),
        help="Path to a text file with one word per line (default: words.txt)",
    )
    parser.add_argument(
        "--lang-pair",
        default="english-italian",
        help="Reverso language pair, e.g. english-italian, english-french (default: english-italian)",
    )
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run the browser headless. Use --no-headless to watch (default: --headless)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Visit each word's page but do not click the favorite button",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds to wait between words to avoid hammering Reverso (default: 2.0)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    load_dotenv()
    username = os.getenv("REVERSO_USERNAME")
    password = os.getenv("REVERSO_PASSWORD")
    if not username or not password:
        print("ERROR: set REVERSO_USERNAME and REVERSO_PASSWORD in .env", file=sys.stderr)
        return 1

    if not args.words_file.exists():
        print(f"ERROR: {args.words_file} not found", file=sys.stderr)
        return 1

    words, skipped = load_words(args.words_file)
    if skipped:
        print(f"Skipped {len(skipped)} blank or duplicate lines")
    if not words:
        print("ERROR: no usable words found", file=sys.stderr)
        return 1

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    print(f"{mode}: {len(words)} words, lang={args.lang_pair}, headless={args.headless}")

    added: list[str] = []
    failed: list[tuple[str, str]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context(user_agent=DESKTOP_UA)
        page = context.new_page()

        try:
            login(page, username, password)
        except LoginFailed as e:
            print(f"ERROR: Reverso rejected the credentials: {e}", file=sys.stderr)
            browser.close()
            return 2
        except PWTimeout as e:
            print(f"ERROR: login timed out: {e}", file=sys.stderr)
            browser.close()
            return 2

        if accept_cookies(page):
            print("(cookie banner dismissed)")

        for i, word in enumerate(words, 1):
            try:
                add_to_favorites(page, word, args.lang_pair, args.dry_run)
                added.append(word)
                print(f"[{i}/{len(words)}] OK: {word}")
            except PWTimeout:
                failed.append((word, "timeout"))
                print(f"[{i}/{len(words)}] FAIL: {word} (timeout)")
            except Exception as e:
                failed.append((word, type(e).__name__))
                print(f"[{i}/{len(words)}] FAIL: {word} ({type(e).__name__}: {e})")

            if i < len(words):
                time.sleep(args.delay)

        browser.close()

    print(f"\nSummary: {len(added)}/{len(words)} added, {len(failed)} failed")
    if failed:
        print("Failed words:")
        for w, reason in failed:
            print(f"  - {w}: {reason}")

    return 0 if not failed else 3


if __name__ == "__main__":
    sys.exit(main())
