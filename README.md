# Daily Motivation Quote

A small daily-committing bot that pulls a fresh motivational/inspirational quote from a live API
every morning and displays it right here.

## Today's Quote

<!-- QUOTE:START -->
> "Showing off is the fool's idea of glory."
>
> — Bruce Lee

_Updated daily at 07:00 AM PKT · last refreshed 2026-08-30_
<!-- QUOTE:END -->

## How it works

- `scripts/fetch_quote.py` fetches a quote from [ZenQuotes.io](https://zenquotes.io) first,
  falling back to [Quotable](https://api.quotable.io) if that fails, and only drops to a small
  local list if both live APIs are unreachable.
- Every quote fetched is appended to `quotes_log.json` (full history).
- The section above is rewritten in place between the `QUOTE:START` / `QUOTE:END` markers.
- A GitHub Actions workflow (`.github/workflows/daily-quote.yml`) runs this daily at
  02:00 UTC (07:00 AM PKT) and commits the changes under the repo owner's identity so it
  counts toward the contribution graph.

## Setup

1. Push this repo to GitHub.
2. No secrets needed — the workflow uses the default `GITHUB_TOKEN` since it only writes to
   this same repo.
3. Confirm Actions are enabled under **Settings → Actions → General**.
4. Trigger the workflow manually once via **Actions → Daily Motivation Quote → Run workflow**
   to verify it fetches and commits correctly before waiting for the first scheduled run.
