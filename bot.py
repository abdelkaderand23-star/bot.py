import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("8748579409:AAFK96pEm4URu46aGw9e7SAfsUTh9WxZd5k")
CHAT_ID = os.getenv("6341614127")

symbols = ["SOLUSDT", "ORDIUSDT", "TRUMPUSDT"]
interval = "1"

last_signal = {}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

def get_klines(symbol):
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit=100"
    data = requests.get(url).json()
    return data["result"]["list"]

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

def analyze_symbol(symbol):
    global last_signal

    try:
        data = get_klines(symbol)

        closes = [float(c[4]) for c in data[::-1]]
        volumes = [float(c[5]) for c in data[::-1]]

        price = closes[-1]
        prev_price = closes[-2]

        rsi = calculate_rsi(closes)
        ema = calculate_ema(closes)

        avg_volume = sum(volumes[-10:]) / 10
        current_volume = volumes[-1]

        whale = current_volume > avg_volume * 2

        signal = "WAIT"

        if rsi < 35 and price > ema and prev_price < ema and whale:
            signal = "BUY"
        elif rsi > 65 or price < ema:
            signal = "EXIT"

        tp = round(price * 1.02, 4)
        sl = round(price * 0.99, 4)

        if signal != "WAIT" and last_signal.get(symbol) != signal:
            if signal == "BUY":
                msg = f"🟢 BUY {symbol}\n💰 السعر: {price}\n📊 RSI: {round(rsi,2)}\n🐋 Volume: {whale}\n🎯 TP: {tp}\n🛑 SL: {sl}"
            else:
                msg = f"🔴 EXIT {symbol}\n💰 السعر: {price}\n📊 RSI: {round(rsi,2)}"

            send_telegram(msg)
            last_signal[symbol] = signal

        print(f"{symbol} | RSI: {round(rsi,1)} | Signal: {signal}")

    except:
        print(f"❌ خطأ في {symbol}")

while True:
    print("\n📊 SPOT BOT RUNNING...\n")

    for symbol in symbols:
        analyze_symbol(symbol)

    time.sleep(15)
