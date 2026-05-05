# arxiv-check

This is a totally vibe coded amateur project based on Codex. Please use it at your discretion.

`arxiv-check` fetches the `quant-ph` arXiv RSS feed, applies a strict keyword filter, remembers the last check time, and can deliver updates through a Telegram bot or a Feishu (Lark) incoming webhook.

## What it does

- Pulls the RSS feed from `https://rss.arxiv.org/rss/quant-ph`
- Filters papers by configurable keywords only
- Includes only papers published between the previous check and the current check
- Exposes a CLI for manual checks
- Exposes a Telegram bot interface with `/check` and `/help`
- Sends results to a Feishu (Lark) group via an incoming webhook

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

4a. Optional Feishu (Lark) settings.

In the Feishu desktop app, go to **Group Settings → Bots → Add Bot → Custom Bot**, copy the
webhook URL, and optionally enable signature verification to get a secret.

```powershell
$env:FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx"
$env:FEISHU_WEBHOOK_SECRET = "your-signing-secret"   # optional
```

```sh
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx"
export FEISHU_WEBHOOK_SECRET="your-signing-secret"   # optional
```

Push the latest matching results to Feishu.

```powershell
$env:PYTHONPATH = "src"
python -m arxiv_check.cli check --feishu
```

```sh
PYTHONPATH=src python -m arxiv_check.cli check --feishu
```

You can combine both flags to send to Telegram and Feishu at the same time.

```sh
PYTHONPATH=src python -m arxiv_check.cli check --telegram --feishu
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

- Windows PowerShell: `scripts/run_scheduled_check.ps1`, `scripts/run_scheduled_check_feishu.ps1`, `scripts/run_telegram_bot.ps1`
- Linux/macOS/other POSIX shells: `scripts/run_scheduled_check.sh`, `scripts/run_scheduled_check_feishu.sh`, `scripts/run_telegram_bot.sh`

## Configuration

Configuration is environment-variable based.

- `ARXIV_FEED_URL`: defaults to `https://rss.arxiv.org/rss/quant-ph`
- `ARXIV_KEYWORDS`: comma-separated list of phrases to match against title and summary
- `ARXIV_STATE_PATH`: JSON state file path, defaults to `.data/state.json`
- `TELEGRAM_BOT_TOKEN`: bot token for Telegram
- `TELEGRAM_CHAT_ID`: chat id used by `check --telegram`
- `TELEGRAM_ALLOWED_CHAT_IDS`: comma-separated allowlist for bot polling mode
- `FEISHU_WEBHOOK_URL`: incoming webhook URL for a Feishu custom bot, used by `check --feishu`
- `FEISHU_WEBHOOK_SECRET`: optional signing secret for Feishu webhook signature verification

If `ARXIV_KEYWORDS` is not set, the project uses a default list centered on quantum computing, quantum complexity, quantum cryptography, and quantum error correction / fault tolerance.

The CLI also auto-loads a local `.env` file if present, so you can keep secrets and keyword settings there instead of setting them manually for every run.
Check `.env.example` for example.

## Daily runs

### Telegram

For a daily push on Windows, create a Task Scheduler task that runs:

```powershell
powershell -ExecutionPolicy Bypass -File "c:\Personal\Coding\arxiv-check\scripts\run_scheduled_check.ps1"
```

For a daily push on Linux or macOS, add a cron entry that runs the POSIX helper script:

```cron
0 9 * * * /bin/sh /path/to/arxiv-check/scripts/run_scheduled_check.sh >> /tmp/arxiv-check.log 2>&1
```

### Feishu (Lark)

Make sure `FEISHU_WEBHOOK_URL` (and optionally `FEISHU_WEBHOOK_SECRET`) are set in your `.env` file,
then schedule the Feishu helper script in the same way.

**macOS / Linux — cron:**

```cron
0 9 * * * /bin/sh /path/to/arxiv-check/scripts/run_scheduled_check_feishu.sh >> /tmp/arxiv-check-feishu.log 2>&1
```

**macOS — launchd** (`~/Library/LaunchAgents/com.arxiv-check.feishu.plist`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>            <string>com.arxiv-check.feishu</string>
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
  <key>StandardOutPath</key> <string>/tmp/arxiv-check-feishu.log</string>
  <key>StandardErrorPath</key><string>/tmp/arxiv-check-feishu.log</string>
</dict>
</plist>
```

Load it with:

```sh
launchctl load ~/Library/LaunchAgents/com.arxiv-check.feishu.plist
```

**Windows — Task Scheduler:**

```powershell
powershell -ExecutionPolicy Bypass -File "C:\path\to\arxiv-check\scripts\run_scheduled_check_feishu.ps1"
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
- `python -m arxiv_check.cli doctor`
  Also prints whether `FEISHU_WEBHOOK_URL` and `FEISHU_WEBHOOK_SECRET` are configured.

## Notes

- On the first run, the current matching items present in the RSS feed are returned.
- The filter is exact phrase substring matching after lowercasing. There is no semantic ranking or extra judgment.
