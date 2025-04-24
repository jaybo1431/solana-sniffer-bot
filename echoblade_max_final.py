import os
import time
import requests
import threading
import random
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, CallbackQueryHandler

# === Config ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SNIPER_WALLET = "8eqEx8z9gZsbWBv6MHZnv4Cge2agEPHJzA6oxopBMj1p"
RPC_URL = "https://api.devnet.solana.com"

app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
user_chats = set()
paused = False

def airdrop_devnet_sol():
    print(f"[💸 Airdrop] Requesting 2 SOL to {SNIPER_WALLET}")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "requestAirdrop",
        "params": [SNIPER_WALLET, int(2 * 1e9)]
    }
    try:
        res = requests.post(RPC_URL, json=payload, headers={"Content-Type": "application/json"})
        result = res.json()
        if "result" in result:
            print("[✅ Airdrop Confirmed] 2 SOL sent to sniper wallet.")
        else:
            print("[❌ Airdrop Failed]", result)
    except Exception as e:
        print(f"[Error] Airdrop exception: {e}")

def start(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="🧠 EchoBlade Devnet Sniper LIVE.")

def watchlaunches(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="👁️ Watching for simulated launches...")
    threading.Thread(target=simulate_launch_feed, daemon=True).start()

def pause(update: Update, context: CallbackContext):
    global paused
    paused = True
    context.bot.send_message(chat_id=update.message.chat_id, text="⏸️ Paused.")

def resume(update: Update, context: CallbackContext):
    global paused
    paused = False
    context.bot.send_message(chat_id=update.message.chat_id, text="▶️ Resumed.")

def simulate_launch_feed():
    seen = set()
    while True:
        if paused:
            time.sleep(5)
            continue
        token = f"SimToken{random.randint(10000,99999)}"
        if token in seen:
            continue
        seen.add(token)
        score = random.randint(60, 100)
        print(f"📡 Scored {token}: {score}")
        if score >= 90:
            notify_users(f"🧠 Auto-Buy: {token} (Score: {score}) — SIMULATED")
            simulate_buy(token)
        elif 75 <= score < 90:
            confirm_buy_prompt(token, score)
        else:
            print(f"🧊 Skipped {token} (Score: {score})")
        time.sleep(8)

def confirm_buy_prompt(token, score):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Buy", callback_data=f"buy:{token}"),
         InlineKeyboardButton("❌ Skip", callback_data=f"skip:{token}")]
    ])
    for chat_id in user_chats:
        bot.send_message(chat_id=chat_id, text=f"🤔 Token {token} scored {score}/100 — Buy?", reply_markup=kb)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data.startswith("buy:"):
        token = query.data.split(":")[1]
        query.edit_message_text(f"✅ Confirmed buy for {token} (Simulated)")
        simulate_buy(token)
    elif query.data.startswith("skip:"):
        token = query.data.split(":")[1]
        query.edit_message_text(f"❌ Skipped {token}")

def simulate_buy(token):
    notify_users(f"🛒 Simulated buy: {token}")
    threading.Thread(target=simulate_sell_cycle, args=(token,), daemon=True).start()

def simulate_sell_cycle(token):
    time.sleep(20)
    notify_users(f"💰 Simulated SELL: {token} at 2x")

def notify_users(msg):
    for chat_id in user_chats:
        bot.send_message(chat_id=chat_id, text=msg)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def index():
    return 'EchoBlade sniper is alive!'

def main():
    airdrop_devnet_sol()
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("watchlaunches", watchlaunches))
    dispatcher.add_handler(CommandHandler("pause", pause))
    dispatcher.add_handler(CommandHandler("resume", resume))
    dispatcher.add_handler(CallbackQueryHandler(button))

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()