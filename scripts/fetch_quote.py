#!/usr/bin/env python3
"""
Daily Motivation Quote Bot
--------------------------
Fetches a motivational/inspirational quote from a live API (primary + secondary),
logs it to quotes_log.json, and injects it into README.md between marker comments.

API-first design:
  1. ZenQuotes.io  (primary)   - https://zenquotes.io/api/random
  2. Quotable      (secondary) - https://api.quotable.io/random?tags=motivational|inspirational
  3. Local fallback list (last resort only, small, just to guarantee a commit
     never fails outright if both live APIs are down at the same time).
"""

import json
import os
import random
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT / "quotes_log.json"
README_FILE = ROOT / "README.md"

START_MARKER = "<!-- QUOTE:START -->"
END_MARKER = "<!-- QUOTE:END -->"

REQUEST_TIMEOUT = 10

# Small last-resort list only — not meant to be hit often.
LOCAL_FALLBACK = [
    {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"quote": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
    {"quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
    {"quote": "Do what you can, with what you have, where you are.", "author": "Theodore Roosevelt"},
    {"quote": "Your time is limited, so don't waste it living someone else's life.", "author": "Steve Jobs"},
    {"quote": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"quote": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"quote": "Hardships often prepare ordinary people for an extraordinary destiny.", "author": "C.S. Lewis"},
]


def fetch_from_zenquotes():
    """Primary source: ZenQuotes.io — free, no API key required."""
    resp = requests.get("https://zenquotes.io/api/random", timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    item = data[0]
    quote = item.get("q", "").strip()
    author = item.get("a", "").strip()
    if not quote:
        raise ValueError("Empty quote from ZenQuotes")
    return {"quote": quote, "author": author or "Unknown", "source": "zenquotes"}


def fetch_from_quotable():
    """Secondary source: Quotable API — free, no API key required."""
    resp = requests.get(
        "https://api.quotable.io/random",
        params={"tags": "motivational|inspirational|success|wisdom"},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    quote = data.get("content", "").strip()
    author = data.get("author", "").strip()
    if not quote:
        raise ValueError("Empty quote from Quotable")
    return {"quote": quote, "author": author or "Unknown", "source": "quotable"}


def get_daily_quote():
    for fetcher in (fetch_from_zenquotes, fetch_from_quotable):
        try:
            result = fetcher()
            print(f"Fetched quote from live API: {result['source']}")
            return result
        except Exception as exc:  # noqa: BLE001 - we deliberately try the next source
            print(f"API attempt failed ({fetcher.__name__}): {exc}")

    print("Both live APIs failed — using local fallback list.")
    picked = random.choice(LOCAL_FALLBACK)
    return {"quote": picked["quote"], "author": picked["author"], "source": "local_fallback"}


def load_log():
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(log):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
        f.write("\n")


def update_readme(entry):
    if not README_FILE.exists():
        print("README.md not found — skipping README update.")
        return

    content = README_FILE.read_text(encoding="utf-8")

    if START_MARKER not in content or END_MARKER not in content:
        print(f"README.md is missing {START_MARKER} / {END_MARKER} markers — skipping README update.")
        return

    block = (
        f"{START_MARKER}\n"
        f"> \"{entry['quote']}\"\n"
        f">\n"
        f"> — {entry['author']}\n"
        f"\n"
        f"_Updated daily at 07:00 AM PKT · last refreshed {entry['date']}_\n"
        f"{END_MARKER}"
    )

    before = content.split(START_MARKER)[0]
    after = content.split(END_MARKER)[1]
    new_content = before + block + after

    README_FILE.write_text(new_content, encoding="utf-8")


def main():
    result = get_daily_quote()
    entry = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "quote": result["quote"],
        "author": result["author"],
        "source": result["source"],
    }

    log = load_log()
    log.append(entry)
    save_log(log)

    update_readme(entry)

    print(f"Logged quote for {entry['date']} (source: {entry['source']})")


if __name__ == "__main__":
    main()
