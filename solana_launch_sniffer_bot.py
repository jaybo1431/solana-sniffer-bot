import requests
import time
import threading
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# === Config ===
import os
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RPC_URL = os.getenv("RPC_URL")

# === Globals ===
tracked_tokens = set()
user_chats = set()

# === Solana Helpers ===
def get_recent_token_mints():
    url = f"{RPC_URL}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # SPL Token Program
            {"limit": 10}
        ]
    }
    try:
        resp = requests.post(url, headers=headers, json=payload)
        result = resp.json().get("result", [])
        return [tx["signature"] for tx in result]
    except Exception as e:
        print(f"[RPC Error] {e}")
        return []

def notify_users(bot: Bot, message: str):
    for chat_id in user_chats:
        bot.send_message(chat_id=chat_id, text=message)

# === Bot Handlers ===
def start(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    update.message.reply_text("👋 Welcome! Use /watchlaunches to get notified about new Solana token launches.")

def watchlaunches(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    update.message.reply_text("👀 Watching for new SPL token launches on Solana...")

# === Background Poller ===
def launch_poller(bot: Bot):
    seen_signatures = set()
    while True:
        signatures = get_recent_token_mints()
        new_sigs = [s for s in signatures if s not in seen_signatures]

        for sig in new_sigs:
            msg = f"🪙 New token mint transaction detected!\nhttps://solscan.io/tx/{sig}"
            notify_users(bot, msg)
            seen_signatures.add(sig)

        time.sleep(15)  # poll every 15 seconds

# === Main Bot Init ===
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("watchlaunches", watchlaunches))

    threading.Thread(target=launch_poller, args=(updater.bot,), daemon=True).start()

    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()