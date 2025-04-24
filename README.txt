EchoBlade MAX – Final Form + Safety Lock 🔐
===========================================

🔐 SAFETY FEATURES:
-------------------
✅ Pump.fun Graduator program check
✅ TRUSTED_CREATORS filtering (only mint authority in this list will be scored)
✅ Graduation tx deduplication (avoid re-scoring)
✅ Telegram logs for "skipped" tokens with reason
✅ Metadata check: reject tokens with no name/symbol (optional)
✅ Future-ready blacklist support

CORE FEATURES:
--------------
✅ Dynamic token scoring (liquidity, txs, time, holders, volatility)
✅ Telegram confirmation (score-based)
✅ AI-mode auto-buy/skip logic
✅ Adaptive buy amounts
✅ Trailing stop + partial sell strategy
✅ Simulated Jupiter quote + PnL tracker
✅ /pause and /resume from Telegram

Deploy Instructions:
---------------------
1. Upload to GitHub
2. Set ENV vars:
   TELEGRAM_BOT_TOKEN, RPC_URL, WEBHOOK_URL, SOL_PRIVATE_KEY
   BUY_AMOUNT, SELL_TARGET_MULTIPLIER, STOP_LOSS_MULTIPLIER
   MIN_EXPECTED_TOKENS, MIN_LIQUIDITY_SOL, BUY_DELAY_SECONDS

3. Start command:
   python echoblade_max_final.py

4. Launch bot via Telegram → /start → /watchlaunches

This version is simulation-only. Use it to test the logic safely.