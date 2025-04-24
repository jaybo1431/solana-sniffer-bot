import os
import time
import json
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, CallbackQueryHandler

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BUY_AMOUNT = float(os.getenv("BUY_AMOUNT", "0.02"))
WALLET_ADDRESS = "BZ4eeduVPAzwDFQ3HpXUrg5FWM8onvqzVv8RfYZD2mES"
DRY_RUN = True
JUPITER_API = "https://quote-api.jup.ag/v6/quote"

app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
user_chats = set()
active_trades = []

def start(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="🧠 EchoBlade Mainnet Sniper is LIVE in Dry-run Mode.")

def watchlaunches(update: Update, context: CallbackContext):
    user_chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="👁️ Watching for token opportunities (simulated scoring)...")
    time.sleep(2)
    simulate_graduated_token()

def simulate_graduated_token():
    fake_token = "So11111111111111111111111111111111111111112"
    score = 92
    msg = f"🧠 Detected graduated token: {fake_token} (score: {score})\nReady to snipe {BUY_AMOUNT} SOL?"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm Buy", callback_data=f"buy:{fake_token}")]
    ])
    for chat_id in user_chats:
        bot.send_message(chat_id=chat_id, text=msg, reply_markup=kb)

def fetch_jupiter_quote(input_mint, output_mint):
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": str(int(BUY_AMOUNT * 1e9)),
        "slippageBps": 100,
        "onlyDirectRoutes": True
    }
    try:
        res = requests.get(JUPITER_API, params=params)
        quote = res.json()
        return quote.get("data", [])[0] if quote.get("data") else None
    except Exception as e:
        print(f"[Jupiter Error] {e}")
        return None

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data.startswith("buy:"):
        token = query.data.split(":")[1]
        query.edit_message_text(f"✅ Buy confirmed for {token}")
        threading.Thread(target=handle_dry_run_buy, args=(token,), daemon=True).start()

def handle_dry_run_buy(token):
    print(f"[Dry-Run] Fetching quote for token {token}")
    quote = fetch_jupiter_quote("So11111111111111111111111111111111111111112", token)
    if quote:
        print(f"[Quote] {json.dumps(quote, indent=2)}")
        tx_link = f"https://solscan.io/address/{token}"
        notify_users(f"💸 DRY-RUN: Would snipe {BUY_AMOUNT} SOL of {token}\nQuote: {quote['outAmount']} tokens\n🔗 {tx_link}")
    else:
        notify_users("❌ Failed to fetch quote or no route available.")

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
    return 'EchoBlade Mainnet Sniper (Dry-run) is live.'

def main():
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("watchlaunches", watchlaunches))
    dispatcher.add_handler(CallbackQueryHandler(button))
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    import threading
    main()