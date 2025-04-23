import os
import time
import threading
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# === Config ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RPC_URL = os.getenv("RPC_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-render-app.onrender.com

# === Telegram Bot Setup ===
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# === Flask App ===
app = Flask(__name__)

# === Globals ===
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
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
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

def notify_users(message: str):
    for chat_id in user_chats:
        bot.send_message(chat_id=chat_id, text=message)

# === Telegram Handlers ===
def start(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="👋 Welcome! Use /watchlaunches to get notified about new Solana token launches.")

def watchlaunches(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="👀 Watching for new SPL token launches on Solana...")

# === Register Handlers ===
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("watchlaunches", watchlaunches))

# === Polling Blockchain in Background ===
def launch_poller():
    seen_signatures = set()
    while True:
        signatures = get_recent_token_mints()
        new_sigs = [s for s in signatures if s not in seen_signatures]
        for sig in new_sigs:
            msg = f"🪙 New token mint transaction detected!\nhttps://solscan.io/tx/{sig}"
            notify_users(msg)
            seen_signatures.add(sig)
        time.sleep(15)

# === Flask Route to Handle Telegram Webhook ===
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def index():
    return 'Solana Sniffer Bot is running!'

def main():
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    threading.Thread(target=launch_poller, daemon=True).start()
    print("🤖 Bot is running with webhook...")
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    main()