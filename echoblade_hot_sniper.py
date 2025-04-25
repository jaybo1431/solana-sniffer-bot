import os
import time
import requests
import json
import threading
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, CallbackQueryHandler
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from base64 import b64decode
import base58

# === Config ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
RPC_URL = os.getenv("RPC_URL")
SOL_PRIVATE_KEY = os.getenv("SOL_PRIVATE_KEY")
BUY_AMOUNT = float(os.getenv("BUY_AMOUNT", "0.1"))
SELL_TARGET_MULTIPLIER = float(os.getenv("SELL_TARGET_MULTIPLIER", "2.0"))
STOP_LOSS_MULTIPLIER = float(os.getenv("STOP_LOSS_MULTIPLIER", "0.7"))
LIVE_MODE = os.getenv("LIVE_MODE", "False").lower() == "true"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
app = Flask(__name__)
rpc = Client(RPC_URL)
user_chats = set()
seen_signatures = set()

# === Load Wallet ===
try:
    if SOL_PRIVATE_KEY.startswith("["):
        secret_key = json.loads(SOL_PRIVATE_KEY)
        keypair = Keypair.from_secret_key(bytes(secret_key))
    else:
        keypair = Keypair.from_secret_key(base58.b58decode(SOL_PRIVATE_KEY))
except Exception as e:
    print("⚠️ Error loading wallet:", e)
    keypair = None

# === Telegram Notifier ===
def notify(text):
    for chat_id in user_chats:
        bot.send_message(chat_id=chat_id, text=text)

# === Jupiter Quote ===
def fetch_jupiter_quote(input_mint, output_mint, amount):
    url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_mint}&outputMint={output_mint}&amount={int(amount*1e9)}&slippage=1"
    resp = requests.get(url)
    return resp.json()

# === Simulated TX Execution ===
def execute_transaction(route_info):
    if LIVE_MODE:
        # Simulated signing
        notify("✍️ TX would be signed and sent now.")
        print("✅ Simulated TX send.")
    else:
        notify("🧪 Simulation: TX not sent (LIVE_MODE=False)")

# === Confirm Prompt ===
def send_confirmation_prompt(route_info):
    out_amount = route_info['outAmount']
    msg = f"🧠 Swap {BUY_AMOUNT} SOL ➡️ {int(out_amount)/1e6:.2f} tokens
Confirm?"

    buttons = [[
        InlineKeyboardButton("✅ Confirm TX", callback_data="confirm_tx"),
        InlineKeyboardButton("❌ Skip", callback_data="skip_tx")
    ]]
    markup = InlineKeyboardMarkup(buttons)

    for chat_id in user_chats:
        bot.send_message(chat_id=chat_id, text=msg, reply_markup=markup)

# === Telegram Handlers ===
def start(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id, text="🧠 EchoBlade HOT version armed.")

def watchlaunches(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    notify("🔍 Watching for new token launches...")
    threading.Thread(target=watch_new_tokens, daemon=True).start()

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == "confirm_tx":
        notify("✅ Confirmation received.")
        route = context.bot_data.get("last_route")
        if route:
            execute_transaction(route)
        query.edit_message_text("💥 Transaction executed (or simulated).")
    elif query.data == "skip_tx":
        query.edit_message_text("⛔ TX skipped.")

# === Mint Watcher ===
def watch_new_tokens():
    target = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
    while True:
        try:
            sigs = rpc.get_signatures_for_address(target, limit=5)["result"]
            for sig in sigs:
                if sig["signature"] in seen_signatures:
                    continue
                seen_signatures.add(sig["signature"])
                print(f"🆕 New token mint: {sig['signature']}")
                notify(f"🆕 Detected new mint: {sig['signature']}")
                # Simulated mint token (replace with real parsed data)
                route = fetch_jupiter_quote("So11111111111111111111111111111111111111112", "Es9vMFrzaCERz7sNmL4hBymjEfgU9zyVYxZBhmzyD1zt", BUY_AMOUNT)
                bot_data = dispatcher.bot_data
                bot_data["last_route"] = route['data'][0]
                send_confirmation_prompt(route['data'][0])
        except Exception as e:
            print("❌ Error fetching mints or Jupiter:", e)
        time.sleep(15)

# === Flask & Webhook Setup ===
@app.route("/")
def index():
    return "EchoBlade Hot Sniper is Running"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# === Launch Bot ===
def main():
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("watchlaunches", watchlaunches))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    print("🔥 EchoBlade Hot Sniper is LIVE.")
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    main()