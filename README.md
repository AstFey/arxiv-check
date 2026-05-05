# arxiv-check

This is a totally vibe coded amateur project based on Codex and Cursor. Please use it at your discretion.

A lightweight, stateful CLI tool that monitors the [quant-ph](https://arxiv.org/list/quant-ph/recent)
arXiv RSS feed, filters papers by configurable keywords, and delivers daily digests to
**Telegram** and/or **Feishu (Lark)**.

---

## Table of Contents

- [arxiv-check](#arxiv-check)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [Environment variables](#environment-variables)
    - [Keyword customisation](#keyword-customisation)
    - [Using a .env file](#using-a-env-file)
  - [Quick Start](#quick-start)
  - [Notification Channels](#notification-channels)
    - [Feishu (Lark)](#feishu-lark)
    - [Telegram](#telegram)
  - [Scheduled Daily Runs](#scheduled-daily-runs)
    - [macOS — launchd](#macos--launchd)
    - [Linux — cron](#linux--cron)
    - [Windows — Task Scheduler](#windows--task-scheduler)
  - [CLI Reference](#cli-reference)
    - [`check`](#check)
    - [`reset-state`](#reset-state)
    - [`doctor`](#doctor)
    - [`telegram-bot`](#telegram-bot)
  - [Telegram Bot](#telegram-bot-1)
  - [Project Layout](#project-layout)
  - [Notes \& FAQ](#notes--faq)

---

## Features

- Pulls the RSS feed from `https://rss.arxiv.org/rss/quant-ph` (configurable).
- Filters papers by exact keyword phrases against title and abstract.
- Remembers the last check time and processed paper IDs — no duplicate notifications.
- Sends digests to a **Feishu** group via an incoming webhook (with optional signature verification).
- Sends digests to a **Telegram** chat via a bot token.
- Both channels can be used simultaneously with a single command.
- Pure-stdlib implementation — no third-party runtime dependencies.
- `.env` file support so secrets are never exposed on the command line.

---

## Requirements

- Python **3.9** or later
- Internet access to `rss.arxiv.org`
- (Optional) A Feishu custom bot webhook URL
- (Optional) A Telegram bot token and chat ID

---

## Installation

```sh
# 1. Clone the repository
git clone https://github.com/AstFey/arxiv-check.git
cd arxiv-check

# 2. Create and activate a virtual environment
python3 -m venv .venv
. .venv/bin/activate          # macOS / Linux
# .\.venv\Scripts\Activate.ps1  # Windows PowerShell

# 3. Install the package in editable mode (no extra dependencies required)
pip install -e .

# 4. Copy the example env file and fill in your secrets
cp .env.example .env
```

> **Windows PowerShell alternative for step 2–3:**
> ```powershell
> python -m venv .venv
> .\.venv\Scripts\Activate.ps1
> pip install -e .
> ```

---

## Configuration

### Environment variables

All settings are read from environment variables (or from a `.env` file in the project root).

| Variable | Default | Description |
|---|---|---|
| `ARXIV_FEED_URL` | `https://rss.arxiv.org/rss/quant-ph` | arXiv RSS feed URL |
| `ARXIV_KEYWORDS` | *(built-in list)* | Comma-separated keyword phrases to match |
| `ARXIV_STATE_PATH` | `.data/state.json` | Path to the JSON state file |
| `FEISHU_WEBHOOK_URL` | — | Feishu custom bot incoming webhook URL |
| `FEISHU_WEBHOOK_SECRET` | — | *(Optional)* Feishu signing secret for HMAC-SHA256 verification |
| `TELEGRAM_BOT_TOKEN` | — | Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | — | Target chat / channel ID for `check --telegram` |
| `TELEGRAM_ALLOWED_CHAT_IDS` | — | Comma-separated allowlist for bot polling mode |

### Keyword customisation

If `ARXIV_KEYWORDS` is not set, the following built-in list is used:

```
quantum computing, quantum computation, quantum complexity, query complexity,
communication complexity, quantum cryptography, quantum key distribution, qkd,
quantum error correction, fault tolerance, fault-tolerant, quantum code,
stabilizer code, surface code, magic state, logical qubit, bosonic code
```

To override, set your own comma-separated list in `.env`:

```
ARXIV_KEYWORDS=topological qubit,majorana,quantum advantage,boson sampling
```

Matching is **case-insensitive exact substring** — no fuzzy or semantic matching.

### Using a .env file

The CLI auto-loads `.env` from the project root on every run, so you only need to set
your secrets once:

```
# .env
ARXIV_KEYWORDS=surface code,logical qubit,magic state
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx
FEISHU_WEBHOOK_SECRET=your-signing-secret
TELEGRAM_BOT_TOKEN=123456:ABC-your-token
TELEGRAM_CHAT_ID=-1001234567890
```

See `.env.example` for a complete template.

---

## Quick Start

After installation and `.env` configuration, run a one-shot check that prints results
to the terminal without sending any notifications and without changing state:

```sh
PYTHONPATH=src python -m arxiv_check.cli check --replay-current-feed --dry-run
```

When the output looks right, run a real check (updates state so the next run won't
repeat the same papers):

```sh
PYTHONPATH=src python -m arxiv_check.cli check
```

> **Tip:** if you installed with `pip install -e .`, the `PYTHONPATH=src` prefix is not needed.

---

## Notification Channels

### Feishu (Lark)

**Step 1 — Create a custom bot in your Feishu group**

1. Open the target group in the Feishu desktop or web app.
2. Go to **Group Settings (···) → Bots → Add Bot → Custom Bot**.
3. Give the bot a name and click **Add**.
4. Copy the **Webhook URL** (`https://open.feishu.cn/open-apis/bot/v2/hook/…`).
5. *(Recommended)* Enable **Signature Verification** and copy the **Secret**.

**Step 2 — Set environment variables**

```sh
# .env
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx
FEISHU_WEBHOOK_SECRET=your-signing-secret   # omit if not enabled
```

**Step 3 — Send a test digest**

```sh
PYTHONPATH=src python -m arxiv_check.cli check --feishu --replay-current-feed --dry-run
```

Remove `--dry-run` when you are satisfied to perform a real run.

---

### Telegram

**Step 1 — Create a bot**

1. Open Telegram and start a chat with [@BotFather](https://t.me/BotFather).
2. Send `/newbot`, follow the prompts, and copy the **bot token**.

**Step 2 — Find your chat ID**

- For a personal chat: send any message to your new bot, then visit
  `https://api.telegram.org/bot<TOKEN>/getUpdates` and read the `chat.id` field.
- For a group or channel: add the bot as an admin, post a message, and use the same
  `getUpdates` endpoint.

**Step 3 — Set environment variables**

```sh
# .env
TELEGRAM_BOT_TOKEN=123456:ABC-your-token
TELEGRAM_CHAT_ID=-1001234567890
```

**Step 4 — Send a test digest**

```sh
PYTHONPATH=src python -m arxiv_check.cli check --telegram --replay-current-feed --dry-run
```

**Sending to both channels at once**

```sh
PYTHONPATH=src python -m arxiv_check.cli check --telegram --feishu
```

---

## Scheduled Daily Runs

The `scripts/` directory contains ready-made launcher scripts that:
- locate the correct Python interpreter (`.venv` or system)
- set `PYTHONPATH` automatically
- source `.env` (POSIX scripts only; Windows reads from process environment)

| Script | Platform | Channel |
|---|---|---|
| `run_scheduled_check.sh` | macOS / Linux | Telegram |
| `run_scheduled_check.ps1` | Windows | Telegram |
| `run_scheduled_check_feishu.sh` | macOS / Linux | Feishu |
| `run_scheduled_check_feishu.ps1` | Windows | Feishu |
| `run_telegram_bot.sh` | macOS / Linux | Telegram bot daemon |
| `run_telegram_bot.ps1` | Windows | Telegram bot daemon |

### macOS — launchd

launchd is the recommended scheduler on macOS because it survives reboots and does not
require the user to keep a terminal open.

Create `~/Library/LaunchAgents/com.arxiv-check.feishu.plist` (adjust the path):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.arxiv-check.feishu</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/sh</string>
    <string>/path/to/arxiv-check/scripts/run_scheduled_check_feishu.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>   <integer>9</integer>
    <key>Minute</key> <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>  <string>/tmp/arxiv-check-feishu.log</string>
  <key>StandardErrorPath</key><string>/tmp/arxiv-check-feishu.log</string>
</dict>
</plist>
```

Load and verify:

```sh
launchctl load   ~/Library/LaunchAgents/com.arxiv-check.feishu.plist
launchctl list | grep arxiv-check   # should show the job
```

To unload: `launchctl unload ~/Library/LaunchAgents/com.arxiv-check.feishu.plist`

> To target Telegram instead, replace the script path with `run_scheduled_check.sh`
> and change the `Label` to avoid conflicts.

### Linux — cron

```sh
crontab -e
```

Add one of the following lines (runs at 09:00 every day):

```cron
# Feishu
0 9 * * * /bin/sh /path/to/arxiv-check/scripts/run_scheduled_check_feishu.sh >> /tmp/arxiv-check-feishu.log 2>&1

# Telegram
0 9 * * * /bin/sh /path/to/arxiv-check/scripts/run_scheduled_check.sh >> /tmp/arxiv-check.log 2>&1
```

### Windows — Task Scheduler

1. Open **Task Scheduler → Create Basic Task**.
2. Set the trigger to **Daily** at your preferred time.
3. Set the action to **Start a Program** with:
   - **Program:** `powershell.exe`
   - **Arguments** (Feishu): `-ExecutionPolicy Bypass -File "C:\path\to\arxiv-check\scripts\run_scheduled_check_feishu.ps1"`
   - **Arguments** (Telegram): `-ExecutionPolicy Bypass -File "C:\path\to\arxiv-check\scripts\run_scheduled_check.ps1"`

> Make sure `FEISHU_WEBHOOK_URL` / `TELEGRAM_BOT_TOKEN` etc. are set as **system or user
> environment variables** on Windows, or add a step in the script to load them from a file.

---

## CLI Reference

All commands share the form `python -m arxiv_check.cli <command> [options]`.

### `check`

Fetch the RSS feed and print new matching papers.

| Flag | Description |
|---|---|
| `--feishu` | Send results to `FEISHU_WEBHOOK_URL` |
| `--telegram` | Send results to `TELEGRAM_CHAT_ID` |
| `--replay-current-feed` | Ignore saved state; treat the whole current feed as new (useful for testing) |
| `--dry-run` | Print results without updating the state file |

**Examples**

```sh
# Print new papers since the last check
PYTHONPATH=src python -m arxiv_check.cli check

# Send to Feishu only
PYTHONPATH=src python -m arxiv_check.cli check --feishu

# Send to both channels
PYTHONPATH=src python -m arxiv_check.cli check --telegram --feishu

# Preview all papers currently in the feed without touching state
PYTHONPATH=src python -m arxiv_check.cli check --replay-current-feed --dry-run
```

### `reset-state`

Clear the saved timestamp and processed paper IDs. The next `check` run will treat
all papers currently in the feed as new.

```sh
PYTHONPATH=src python -m arxiv_check.cli reset-state
```

### `doctor`

Print a summary of the current configuration and state.

```sh
PYTHONPATH=src python -m arxiv_check.cli doctor
```

Add `--telegram` to also call `getMe` and `getUpdates` for a live Telegram diagnostic:

```sh
PYTHONPATH=src python -m arxiv_check.cli doctor --telegram
```

### `telegram-bot`

Run a long-polling Telegram bot that responds to `/check` and `/help` in real time.

```sh
PYTHONPATH=src python -m arxiv_check.cli telegram-bot
```

| Flag | Description |
|---|---|
| `--poll-interval <seconds>` | Delay between polling cycles (default `2.0`) |
| `--once` | Process one polling batch then exit (useful for smoke-testing) |

---

## Telegram Bot

When the bot daemon is running, it responds to:

| Command | Description |
|---|---|
| `/check` | Preview papers currently matching in the RSS feed (does **not** update saved state) |
| `/help` | Show available commands |

To restrict access, set `TELEGRAM_ALLOWED_CHAT_IDS` to a comma-separated list of
allowed chat IDs. Requests from any other chat receive a rejection message.

**Keeping the bot alive on macOS / Linux**

Use any process supervisor, for example `tmux`:

```sh
tmux new -s arxiv-bot
/bin/sh /path/to/arxiv-check/scripts/run_telegram_bot.sh
# Ctrl-B D to detach
```

Or `systemd`, `supervisord`, or `launchd` for a proper daemon setup.

**On Windows**, create a Task Scheduler task that runs at logon with:

```powershell
powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass `
  -File "C:\path\to\arxiv-check\scripts\run_telegram_bot.ps1"
```

---

## Project Layout

```
arxiv-check/
├── src/arxiv_check/
│   ├── arxiv.py        # RSS fetch and XML parsing
│   ├── cli.py          # Argument parsing and command dispatch
│   ├── config.py       # Environment-variable based configuration
│   ├── env.py          # .env file loader
│   ├── feishu.py       # Feishu webhook client
│   ├── filtering.py    # Keyword matching logic
│   ├── formatter.py    # Plain-text paper formatter
│   ├── models.py       # Dataclasses: Paper, AppState, CheckResult
│   ├── service.py      # Core check logic (fetch → filter → state update)
│   ├── ssl_utils.py    # SSL context helper
│   ├── state.py        # State file read / write
│   └── telegram.py     # Telegram Bot API client
├── scripts/
│   ├── run_scheduled_check.sh / .ps1           # Telegram daily launcher
│   ├── run_scheduled_check_feishu.sh / .ps1    # Feishu daily launcher
│   └── run_telegram_bot.sh / .ps1              # Telegram bot daemon launcher
├── tests/
│   └── test_filtering.py
├── .env.example
└── pyproject.toml
```

---

## Notes & FAQ

**Q: I ran `check` but got no papers.**  
The state file records which papers have already been processed. If this is not the
first run, only papers published *after* the previous check are returned. Use
`--replay-current-feed --dry-run` to see everything currently in the feed regardless
of state.

**Q: How do I reset and start fresh?**  
Run `python -m arxiv_check.cli reset-state`. The next `check` will pick up all papers
currently in the RSS feed.

**Q: The Feishu message was not delivered.**  
1. Confirm `FEISHU_WEBHOOK_URL` is correct (it starts with `https://open.feishu.cn/open-apis/bot/v2/hook/`).
2. If signature verification is enabled in Feishu, make sure `FEISHU_WEBHOOK_SECRET` is also set.
3. Run `doctor` to verify the URL is loaded: `python -m arxiv_check.cli doctor`.

**Q: How is keyword matching done?**  
Each keyword phrase is checked as a **case-insensitive substring** against the
concatenation of the paper's title and abstract. There is no stemming, fuzzy matching,
or semantic ranking.

**Q: Can I monitor a different arXiv subject area?**  
Yes. Set `ARXIV_FEED_URL` to any arXiv RSS feed, e.g.:
```
ARXIV_FEED_URL=https://rss.arxiv.org/rss/cs.CC
```

**Q: Does this work without any notification channel configured?**  
Yes. Running `check` without `--telegram` or `--feishu` simply prints results to
stdout, which is useful for scripting or piping output elsewhere.
