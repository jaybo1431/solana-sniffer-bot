EchoBlade HOT Version 🔥 – Mainnet Sniper
========================================

✅ Pulls real-time mint transactions from Solana
✅ Fetches live swap quotes from Jupiter Aggregator
✅ Sends real SOL swap transactions using solana-py
✅ Telegram integration for confirmation flow
✅ Stop-loss + sell-multiplier logic
✅ ENV-driven config and live mode toggle

Required Environment Variables:
-------------------------------
- TELEGRAM_BOT_TOKEN
- RPC_URL (Mainnet, like Helius or public RPC)
- WEBHOOK_URL
- SOL_PRIVATE_KEY (base58 or 64-byte array)
- BUY_AMOUNT
- SELL_TARGET_MULTIPLIER
- STOP_LOSS_MULTIPLIER
- MIN_EXPECTED_TOKENS
- MIN_LIQUIDITY_SOL
- BUY_DELAY_SECONDS
- LIVE_MODE=True

Start Command:
--------------
python echoblade_hot_sniper.py

CAUTION:
--------
This is a real mainnet sniper. Only deploy when ready.