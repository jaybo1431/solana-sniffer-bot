import os
import time
import threading
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from solana.rpc.api import Client

# === Config ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RPC_URL = os.getenv("RPC_URL", "https://api.devnet.solana.com")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SOL_PRIVATE_KEY = os.getenv("SOL_PRIVATE_KEY")
BUY_AMOUNT = float(os.getenv("BUY_AMOUNT", "0.1"))
SELL_TARGET_MULTIPLIER = float(os.getenv("SELL_TARGET_MULTIPLIER", "2.0"))
MIN_LIQUIDITY_SOL = float(os.getenv("MIN_LIQUIDITY_SOL", "1.0"))
MIN_EXPECTED_TOKENS = float(os.getenv("MIN_EXPECTED_TOKENS", "1000"))
BUY_DELAY_SECONDS = int(os.getenv("BUY_DELAY_SECONDS", "10"))

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
app = Flask(__name__)
user_chats = set()
rpc = Client(RPC_URL)

def start(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="🧪 Simulated sniper bot online for Pump.fun graduates on devnet.")

def watchlaunches(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="🎓 Watching for simulated Pump.fun graduates...")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("watchlaunches", watchlaunches))

def notify_users(message: str):
    for chat_id in user_chats:
        bot.send_message(chat_id=chat_id, text=message)

def simulate_jupiter_quote(input_mint: str, output_mint: str, amount: float):
    print(f"📊 Simulating quote for {amount} from {input_mint} to {output_mint}")
    notify_users(f"📊 Simulated Jupiter Quote\nFrom: {input_mint}\nTo: {output_mint}\nAmount: {amount} SOL\nExpected Tokens: ~{MIN_EXPECTED_TOKENS}+")
    return True

def auto_buy_token_simulated(mint_address: str):
    notify_users(f"🎓 Simulated graduation detected: {mint_address}")
    time.sleep(BUY_DELAY_SECONDS)
    if simulate_jupiter_quote("So11111111111111111111111111111111111111112", mint_address, BUY_AMOUNT):
        notify_users(f"🛒 Simulated auto-buy for token {mint_address} (would have spent {BUY_AMOUNT} SOL)")
        threading.Thread(target=monitor_and_sell_simulated, args=(mint_address,), daemon=True).start()

def monitor_and_sell_simulated(token_mint: str):
    notify_users(f"👀 Monitoring {token_mint} for simulated sell at {SELL_TARGET_MULTIPLIER}x...")
    time.sleep(30)
    notify_users(f"💰 Simulated SELL executed for {token_mint} at target price!")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def index():
    return 'Sniper Simulator running!'

def main():
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    print("🤖 Simulation bot running...")
    threading.Thread(target=lambda: auto_buy_token_simulated("SimMintTokenDev11111111111111111111111111111"), daemon=True).start()
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    main()