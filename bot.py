import requests
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "PUT_YOUR_TELEGRAM_TOKEN_HERE"

# =========================
# جلب البيانات من Binance
# =========================
def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100"
    data = requests.get(url).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    df["close"] = df["close"].astype(float)
    return df

# =========================
# التحليل
# =========================
def analyze(symbol):
    df = get_data(symbol)

    ema = EMAIndicator(df["close"], window=20).ema_indicator()
    rsi = RSIIndicator(df["close"], window=14).rsi()

    last_price = df["close"].iloc[-1]
    last_ema = ema.iloc[-1]
    last_rsi = rsi.iloc[-1]

    if last_price > last_ema and last_rsi < 30:
        signal = "BUY 🟢"
        sl = last_price - 0.002
        tp = last_price + 0.004

    elif last_price < last_ema and last_rsi > 70:
        signal = "SELL 🔴"
        sl = last_price + 0.002
        tp = last_price - 0.004

    else:
        signal = "NO TRADE ⚠️"
        sl = "-"
        tp = "-"

    return f"""
📊 {symbol}

السعر: {last_price:.5f}
EMA: {last_ema:.5f}
RSI: {last_rsi:.2f}

📈 الإشارة: {signal}

🎯 TP: {tp}
🛑 SL: {sl}
"""

# =========================
# الأوامر
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["EURUSD", "GBPUSD", "XAUUSD"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "اختر الزوج 👇",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    mapping = {
        "EURUSD": "EURUSDT",
        "GBPUSD": "GBPUSDT",
        "XAUUSD": "XAUUSDT"
    }

    if text in mapping:
        result = analyze(mapping[text])
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("اختر زوج من الأزرار فقط")

# =========================
# تشغيل البوت
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
