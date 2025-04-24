import os
import time
import requests
import threading
import random
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, CallbackQueryHandler

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SNIPER_WALLET = "8eqEx8z9gZsbWBv6MHZnv4Cge2agEPHJzA6oxopBMj1p"
RPC_URL = "https://api.devnet.solana.com"

app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

user_chats = set()
paused = False
sniped_tokens = []
score_history = []
profit_log = []
start_time = time.time()

def airdrop_devnet_sol():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "requestAirdrop",
        "params": [SNIPER_WALLET, int(2 * 1e9)]
    }
    try:
        res = requests.post(RPC_URL, json=payload, headers={"Content-Type": "application/json"})
        result = res.json()
        print("[Airdrop]", result)
    except Exception as e:
        print(f"[Airdrop Error] {e}")

def start(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="🧠 EchoBlade Full Intel is now online.")

def watchlaunches(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="👁️ Watching simulated token mints...")
    threading.Thread(target=simulate_launch_feed, daemon=True).start()

def pause(update: Update, context: CallbackContext):
    global paused
    paused = True
    context.bot.send_message(chat_id=update.message.chat_id, text="⏸️ Paused.")

def resume(update: Update, context: CallbackContext):
    global paused
    paused = False
    context.bot.send_message(chat_id=update.message.chat_id, text="▶️ Resumed.")

def show_status(update: Update, context: CallbackContext):
    uptime = round(time.time() - start_time, 1)
    avg_score = round(sum(score_history) / len(score_history), 2) if score_history else 0
    msg = f"""📊 Status Report:
Uptime: {uptime}s
Sniped: {len(sniped_tokens)} tokens
Avg Score: {avg_score}
Memory: {len(score_history)} scores tracked"""
    context.bot.send_message(chat_id=update.message.chat_id, text=msg)

def show_pnl(update: Update, context: CallbackContext):
    if not profit_log:
        context.bot.send_message(chat_id=update.message.chat_id, text="💰 No simulated trades yet.")
        return
    total_profit = sum(profit_log)
    avg_profit = total_profit / len(profit_log)
    msg = f"""📈 Simulated PnL:
Trades: {len(profit_log)}
Total Sim Profit: {round(total_profit, 2)} SOL
Avg Profit per Trade: {round(avg_profit, 2)} SOL"""
    context.bot.send_message(chat_id=update.message.chat_id, text=msg)

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
        score_history.append(score)
        print(f"📡 Token {token} scored {score}")
        if score >= 90:
            sniped_tokens.append(token)
            notify_users(f"🧠 Auto-Buy: {token} (Score: {score}) — SIMULATED")
            simulate_buy(token, score)
        elif 75 <= score < 90:
            confirm_buy_prompt(token, score)
        else:
            print(f"🧊 Skipped {token} (Score: {score})")
        time.sleep(6)

def confirm_buy_prompt(token, score):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Buy", callback_data=f"buy:{token}:{score}"),
         InlineKeyboardButton("❌ Skip", callback_data=f"skip:{token}")]
    ])
    for chat_id in user_chats:
        bot.send_message(chat_id=chat_id, text=f"🤔 Token {token} scored {score}/100 — Buy?", reply_markup=kb)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    parts = query.data.split(":")
    action = parts[0]
    token = parts[1]
    score = int(parts[2]) if len(parts) > 2 else 85
    if action == "buy":
        sniped_tokens.append(token)
        query.edit_message_text(f"✅ Confirmed buy for {token} (Simulated)")
        simulate_buy(token, score)
    elif action == "skip":
        query.edit_message_text(f"❌ Skipped {token}")

def simulate_buy(token, score):
    notify_users(f"🛒 Simulated buy: {token}")
    threading.Thread(target=simulate_sell_cycle, args=(token, score), daemon=True).start()

def simulate_sell_cycle(token, score):
    time.sleep(10)
    profit = round(random.uniform(0.5, 2.5), 2)
    profit_log.append(profit)
    notify_users(f"💰 Simulated SELL: {token} — +{profit} SOL")

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
    return 'EchoBlade Full Intel is live.'

def main():
    airdrop_devnet_sol()
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("watchlaunches", watchlaunches))
    dispatcher.add_handler(CommandHandler("pause", pause))
    dispatcher.add_handler(CommandHandler("resume", resume))
    dispatcher.add_handler(CommandHandler("status", show_status))
    dispatcher.add_handler(CommandHandler("pnl", show_pnl))
    dispatcher.add_handler(CallbackQueryHandler(button))

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()