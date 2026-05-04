import argparse
import sys
import time
from pathlib import Path

from .config import load_config
from .env import load_dotenv
from .feishu import FeishuError
from .feishu import send_check_result as feishu_send_check_result
from .formatter import format_paper_list
from .models import AppState
from .service import check_for_new_papers
from .state import load_state, save_state
from .telegram import (
    TelegramError,
    extract_chat_id,
    extract_text,
    get_me,
    get_updates,
    newest_offset,
    send_check_result,
    send_message,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check quant-ph arXiv RSS for keyword-matched papers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Fetch the feed and print new matching papers.")
    check_parser.add_argument("--telegram", action="store_true", help="Also send the result to TELEGRAM_CHAT_ID.")
    check_parser.add_argument("--feishu", action="store_true", help="Also send the result to FEISHU_WEBHOOK_URL.")
    check_parser.add_argument(
        "--replay-current-feed",
        action="store_true",
        help="Ignore saved paper state and treat the current RSS feed as new for testing.",
    )
    check_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print results without updating the saved state file.",
    )

    bot_parser = subparsers.add_parser("telegram-bot", help="Run a Telegram bot using long polling.")
    bot_parser.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Delay between polling cycles after each getUpdates call.",
    )
    bot_parser.add_argument(
        "--once",
        action="store_true",
        help="Process one polling batch and exit. Useful for testing.",
    )

    subparsers.add_parser("reset-state", help="Clear the saved paper check state.")

    doctor_parser = subparsers.add_parser("doctor", help="Print configuration and Telegram diagnostics.")
    doctor_parser.add_argument(
        "--telegram",
        action="store_true",
        help="Also call Telegram getMe and getUpdates for a live diagnostic.",
    )

    return parser


def run_check(send_to_telegram: bool, send_to_feishu: bool, replay_current_feed: bool, dry_run: bool) -> int:
    config = load_config()
    state = load_state(config.state_path)
    effective_state = state
    if replay_current_feed:
        effective_state = AppState(telegram_update_offset=state.telegram_update_offset)

    result, next_state = check_for_new_papers(config, effective_state)

    if send_to_telegram:
        if not config.telegram_bot_token or not config.telegram_chat_id:
            raise SystemExit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required for --telegram.")
        send_check_result(config.telegram_bot_token, config.telegram_chat_id, result)

    if send_to_feishu:
        if not config.feishu_webhook_url:
            raise SystemExit("FEISHU_WEBHOOK_URL is required for --feishu.")
        feishu_send_check_result(config.feishu_webhook_url, result, config.feishu_webhook_secret)

    if not dry_run:
        save_state(config.state_path, next_state)
    print(format_paper_list(result.papers))
    if dry_run:
        print("\n[dry-run] state file not updated.")

    return 0


def _is_allowed_chat(config, chat_id: str) -> bool:
    if not config.telegram_allowed_chat_ids:
        return True
    return chat_id in config.telegram_allowed_chat_ids


def _build_replay_state(state: AppState) -> AppState:
    return AppState(telegram_update_offset=state.telegram_update_offset)


def _process_telegram_updates(config, state):
    updates = get_updates(config.telegram_bot_token, state.telegram_update_offset)
    for update in updates:
        chat_id = extract_chat_id(update)
        text = extract_text(update)
        if not chat_id or not text:
            continue
        if not _is_allowed_chat(config, chat_id):
            send_message(config.telegram_bot_token, chat_id, "This chat is not allowed.")
            continue

        if text.startswith("/help"):
            send_message(
                config.telegram_bot_token,
                chat_id,
                "Commands:\n/check - preview current matching quant-ph papers without changing saved state\n/help - show this message",
            )
        elif text.startswith("/check"):
            result, _ = check_for_new_papers(config, _build_replay_state(state))
            send_check_result(config.telegram_bot_token, chat_id, result)
        else:
            send_message(config.telegram_bot_token, chat_id, "Unknown command. Use /check or /help.")

    state.telegram_update_offset = newest_offset(updates, state.telegram_update_offset)
    save_state(config.state_path, state)
    return state, len(updates)


def run_telegram_bot(poll_interval: float, once: bool) -> int:
    config = load_config()
    if not config.telegram_bot_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required for telegram-bot mode.")

    state = load_state(config.state_path)
    _safe_stderr("Telegram bot polling started.")

    while True:
        try:
            state, update_count = _process_telegram_updates(config, state)
            if once:
                _safe_stderr(f"Processed {update_count} Telegram updates.")
                return 0
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            save_state(config.state_path, state)
            return 0
        except TelegramError as exc:
            _safe_stderr(f"Telegram API error: {exc}")
            time.sleep(max(poll_interval, 5))
        except Exception as exc:
            _safe_stderr(f"Telegram bot error: {exc}")
            time.sleep(max(poll_interval, 5))


def run_reset_state() -> int:
    config = load_config()
    state = load_state(config.state_path)
    reset_state = AppState(telegram_update_offset=state.telegram_update_offset)
    save_state(config.state_path, reset_state)
    print(f"Reset paper state in {config.state_path}.")
    return 0


def _bool_label(value: bool) -> str:
    return "yes" if value else "no"


def _safe_stderr(message: str) -> None:
    stream = getattr(sys, "stderr", None)
    if stream is None:
        return
    try:
        print(message, file=stream)
    except Exception:
        return


def run_doctor(include_telegram: bool) -> int:
    config = load_config()
    state = load_state(config.state_path)
    env_sources = [name for name in (".env", ".env.example") if Path(name).exists()]

    print(f"Loaded config files present: {', '.join(env_sources) if env_sources else 'none'}")
    print(f"State path: {config.state_path}")
    print(f"Last checked at: {state.last_checked_at.isoformat() if state.last_checked_at else 'never'}")
    print(f"Tracked processed ids: {len(state.processed_item_ids)}")
    print(f"Telegram update offset: {state.telegram_update_offset}")
    print(f"Telegram bot token configured: {_bool_label(bool(config.telegram_bot_token))}")
    print(f"Telegram chat id configured: {_bool_label(bool(config.telegram_chat_id))}")
    print(
        "Telegram allowed chats configured: "
        f"{', '.join(sorted(config.telegram_allowed_chat_ids)) if config.telegram_allowed_chat_ids else 'none'}"
    )
    print(f"Feishu webhook URL configured: {_bool_label(bool(config.feishu_webhook_url))}")
    print(f"Feishu webhook secret configured: {_bool_label(bool(config.feishu_webhook_secret))}")

    if include_telegram:
        if not config.telegram_bot_token:
            raise SystemExit("TELEGRAM_BOT_TOKEN is required for doctor --telegram.")

        bot_info = get_me(config.telegram_bot_token)
        print(f"Telegram getMe ok: @{bot_info.get('username', '')} ({bot_info.get('id', '')})")
        updates = get_updates(config.telegram_bot_token, state.telegram_update_offset)
        print(f"Pending updates fetched: {len(updates)}")

    return 0


def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "check":
        return run_check(
            send_to_telegram=args.telegram,
            send_to_feishu=args.feishu,
            replay_current_feed=args.replay_current_feed,
            dry_run=args.dry_run,
        )
    if args.command == "telegram-bot":
        return run_telegram_bot(poll_interval=args.poll_interval, once=args.once)
    if args.command == "reset-state":
        return run_reset_state()
    if args.command == "doctor":
        return run_doctor(include_telegram=args.telegram)

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
