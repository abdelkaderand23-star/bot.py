import requests
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

pairs = ["EURUSD", "GBPUSD", "XAUUSD"]

# 📊 جلب بيانات من Binance (لأنها بدون حظر)
def get_data(symbol):
    try:
        symbol = symbol + "T" if symbol != "XAUUSD" else "BTCUSDT"
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": "1m", "limit": 100}
        data = requests.get(url, params=params).json()
        closes = [float(c[4]) for c in data]
        return closes
    except:
        return None

def calculate_rsi(closes, period=14):
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_ema(prices, period=9):
    ema = prices[0]
    k = 2 / (period + 1)
    for price in prices:
        ema = price * k + ema * (1 - k)
    return ema

def analyze(pair):
    closes = get_data(pair)
    if not closes:
        return "❌ خطأ في جلب البيانات"

    price = closes[-1]
    rsi = calculate_rsi(closes)
    ema = calculate_ema(closes)

    signal = "WAIT"

    if rsi < 35 and price > ema:
        signal = "BUY"
    elif rsi > 65 and price < ema:
        signal = "SELL"

    tp = round(price * 1.002, 5)
    sl = round(price * 0.998, 5)

    return f"""
📊 {pair} ANALYSIS

💰 Price: {price}
📈 RSI: {round(rsi,2)}
📉 EMA: {round(ema,5)}

🚦 Signal: {signal}

🎯 TP: {tp}
🛑 SL: {sl}
"""

# 🚀 عند /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[p] for p in pairs]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "اختر الزوج 👇",
        reply_markup=reply_markup
    )

# 📊 عند اختيار زوج
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = update.message.text

    if pair in pairs:
        result = analyze(pair)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("❌ اختر من الأزرار فقط")

# تشغيل البوت
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("🤖 BOT STARTED...")
app.run_polling()
