# arxiv-check

This is a totally vibe coded amateur project based on Codex. Please use it at your discretion.

`arxiv-check` fetches the `quant-ph` arXiv RSS feed, applies a strict keyword filter, remembers the last check time, and can deliver updates through a Telegram bot.

## What it does

- Pulls the RSS feed from `https://rss.arxiv.org/rss/quant-ph`
- Filters papers by configurable keywords only
- Includes only papers published between the previous check and the current check
- Exposes a CLI for manual checks
- Exposes a Telegram bot interface with `/check` and `/help`

## Quick start

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```sh
python3 -m venv .venv
. .venv/bin/activate
```

2. Run a local check.

```powershell
$env:PYTHONPATH = "src"
python -m arxiv_check.cli check
```

```sh
PYTHONPATH=src python -m arxiv_check.cli check
```

3. Optional Telegram settings.

```powershell
$env:TELEGRAM_BOT_TOKEN = "your-bot-token"
$env:TELEGRAM_CHAT_ID = "your-chat-id"
```

```sh
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
```

4. Push the latest matching results to Telegram.

```powershell
$env:PYTHONPATH = "src"
python -m arxiv_check.cli check --telegram
```

```sh
PYTHONPATH=src python -m arxiv_check.cli check --telegram
```

5. Run the Telegram bot.

```powershell
$env:PYTHONPATH = "src"
python -m arxiv_check.cli telegram-bot
```

```sh
PYTHONPATH=src python -m arxiv_check.cli telegram-bot
```

For a one-shot Telegram polling test:

```powershell
$env:PYTHONPATH = "src"
python -m arxiv_check.cli telegram-bot --once
```

```sh
PYTHONPATH=src python -m arxiv_check.cli telegram-bot --once
```

6. Test against the current feed without changing state.

```powershell
$env:PYTHONPATH = "src"
python -m arxiv_check.cli check --replay-current-feed --dry-run
```

```sh
PYTHONPATH=src python -m arxiv_check.cli check --replay-current-feed --dry-run
```

The repository also includes helper launchers for both environments:

- Windows PowerShell: `scripts/run_scheduled_check.ps1`, `scripts/run_telegram_bot.ps1`
- Linux/macOS/other POSIX shells: `scripts/run_scheduled_check.sh`, `scripts/run_telegram_bot.sh`

## Configuration

Configuration is environment-variable based.

- `ARXIV_FEED_URL`: defaults to `https://rss.arxiv.org/rss/quant-ph`
- `ARXIV_KEYWORDS`: comma-separated list of phrases to match against title and summary
- `ARXIV_STATE_PATH`: JSON state file path, defaults to `.data/state.json`
- `TELEGRAM_BOT_TOKEN`: bot token for Telegram
- `TELEGRAM_CHAT_ID`: chat id used by `check --telegram`
- `TELEGRAM_ALLOWED_CHAT_IDS`: comma-separated allowlist for bot polling mode

If `ARXIV_KEYWORDS` is not set, the project uses a default list centered on quantum computing, quantum complexity, quantum cryptography, and quantum error correction / fault tolerance.

The CLI also auto-loads a local `.env` file if present, so you can keep secrets and keyword settings there instead of setting them manually for every run.
Check `.env.example` for example.

## Daily runs

For a daily push on Windows, create a Task Scheduler task that runs:

```powershell
powershell -ExecutionPolicy Bypass -File "c:\Personal\Coding\arxiv-check\scripts\run_scheduled_check.ps1"
```

For a daily push on Linux or macOS, add a cron entry that runs the POSIX helper script:

```cron
0 9 * * * /bin/sh /path/to/arxiv-check/scripts/run_scheduled_check.sh >> /tmp/arxiv-check.log 2>&1
```

The state file prevents duplicate posts across runs.

The following feature is still under testing.

If you want Telegram `/check` and `/help` to respond automatically, that is a separate long-running bot process. Create another Task Scheduler task that runs at logon or startup:

```powershell
powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "c:\Personal\Coding\arxiv-check\scripts\run_telegram_bot.ps1"
```

On Linux or macOS, run the matching POSIX helper script under your preferred process manager:

```sh
/bin/sh /path/to/arxiv-check/scripts/run_telegram_bot.sh
```

`systemd`, `launchd`, `supervisord`, `screen`, or `tmux` are all reasonable ways to keep the bot running.

## Telegram commands

- `/check`: previews the current matching papers from the RSS feed without changing saved state
- `/help`: shows command help

## Useful commands

- `python -m arxiv_check.cli check --replay-current-feed --dry-run`
  Shows what currently matches in the RSS feed without changing saved state.
- `python -m arxiv_check.cli reset-state`
  Clears the saved paper-check timestamp and processed ids.
- `python -m arxiv_check.cli doctor`
  Shows config and state status.
- `python -m arxiv_check.cli doctor --telegram`
  Verifies the Telegram bot token live and shows pending update count.

## Notes

- On the first run, the current matching items present in the RSS feed are returned.
- The filter is exact phrase substring matching after lowercasing. There is no semantic ranking or extra judgment.
