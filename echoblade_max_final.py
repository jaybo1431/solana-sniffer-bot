import os
import time
import threading
import random
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, CallbackQueryHandler

# === Config ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BUY_AMOUNT = float(os.getenv("BUY_AMOUNT", "0.1"))
SELL_TARGET_MULTIPLIER = float(os.getenv("SELL_TARGET_MULTIPLIER", "2.0"))
STOP_LOSS_MULTIPLIER = float(os.getenv("STOP_LOSS_MULTIPLIER", "0.7"))
MIN_EXPECTED_TOKENS = int(os.getenv("MIN_EXPECTED_TOKENS", "1000"))
BUY_DELAY_SECONDS = int(os.getenv("BUY_DELAY_SECONDS", "10"))

TRUSTED_CREATORS = [
    "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkgYrz6QkBEMq",  # Example Pump.fun authority
]

app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
user_chats = set()
paused = False

def start(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="🧠 EchoBlade Final Form active. Ready to monitor launches.")

def watchlaunches(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="👁️ Watching for trusted Pump.fun graduates...")
    threading.Thread(target=simulate_launch_feed, daemon=True).start()

def pause(update: Update, context: CallbackContext):
    global paused
    paused = True
    context.bot.send_message(chat_id=update.message.chat_id, text="⏸️ EchoBlade paused.")

def resume(update: Update, context: CallbackContext):
    global paused
    paused = False
    context.bot.send_message(chat_id=update.message.chat_id, text="▶️ EchoBlade resumed.")

def simulate_launch_feed():
    seen_mints = set()
    while True:
        if paused:
            time.sleep(5)
            continue
        mint_address = f"SimToken{random.randint(10000, 99999)}"
        creator = random.choice([TRUSTED_CREATORS[0], "FakeCreator111"])
        if creator not in TRUSTED_CREATORS:
            print(f"❌ Skipped untrusted creator: {creator}")
            time.sleep(8)
            continue
        if mint_address in seen_mints:
            continue
        seen_mints.add(mint_address)
        score = random.randint(60, 100)
        print(f"🎯 Detected graduated token: {mint_address} with score {score}")
        if score >= 90:
            notify_users(f"🧠 Auto-buying {mint_address} (score {score}) — SIMULATED")
            simulate_buy(mint_address, score)
        elif 75 <= score < 90:
            confirm_buy_prompt(mint_address, score)
        else:
            notify_users(f"🧊 Skipping {mint_address} — score too low ({score})")
        time.sleep(10)

def confirm_buy_prompt(token, score):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Buy", callback_data=f"buy:{token}"),
         InlineKeyboardButton("❌ Skip", callback_data=f"skip:{token}")]
    ])
    for chat_id in user_chats:
        bot.send_message(chat_id=chat_id, text=f"🤔 Token {token} scored {score}/100 — Buy?", reply_markup=keyboard)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    if data.startswith("buy:"):
        token = data.split(":")[1]
        query.edit_message_text(f"✅ Confirmed: Simulating buy for {token}")
        simulate_buy(token, score=85)
    elif data.startswith("skip:"):
        token = data.split(":")[1]
        query.edit_message_text(f"❌ Skipped: {token}")

def simulate_buy(token, score):
    notify_users(f"🛒 Simulated buy for {token} at score {score}")
    threading.Thread(target=simulate_sell_cycle, args=(token,), daemon=True).start()

def simulate_sell_cycle(token):
    time.sleep(20)
    notify_users(f"💰 Simulated SELL for {token} at {SELL_TARGET_MULTIPLIER}x")

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
    return 'EchoBlade is running.'

def main():
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("watchlaunches", watchlaunches))
    dispatcher.add_handler(CommandHandler("pause", pause))
    dispatcher.add_handler(CommandHandler("resume", resume))
    dispatcher.add_handler(CallbackQueryHandler(button))
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    main()