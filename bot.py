import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# أزواج مضمونة شغالة
symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

interval = "1"
last_signal = {}

headers = {
    "User-Agent": "Mozilla/5.0"
}

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        requests.post(url, data=data)
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def get_klines(symbol):
    try:
        # ✅ endpoint الجديد
        url = "https://api.bytick.com/v5/market/kline"

        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": 100
        }

        response = requests.get(url, params=params, headers=headers)

        if response.status_code != 200:
            print(f"❌ HTTP Error {symbol}: {response.status_code}")
            return None

        data = response.json()

        if data.get("retCode") != 0:
            print(f"❌ API Error {symbol}: {data}")
            return None

        return data["result"]["list"]

    except Exception as e:
        print(f"❌ Request Error {symbol}: {e}")
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

def analyze_symbol(symbol):
    global last_signal

    data = get_klines(symbol)

    if not data:
        return

    try:
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
                msg = f"🟢 BUY {symbol}\n💰 Price: {price}\n📊 RSI: {round(rsi,2)}\n🐋 Volume Spike: {whale}\n🎯 TP: {tp}\n🛑 SL: {sl}"
            else:
                msg = f"🔴 EXIT {symbol}\n💰 Price: {price}\n📊 RSI: {round(rsi,2)}"

            send_telegram(msg)
            last_signal[symbol] = signal

        print(f"{symbol} | RSI: {round(rsi,1)} | Signal: {signal}")

    except Exception as e:
        print(f"❌ Error in {symbol}: {e}")

while True:
    print("\n📊 SPOT BOT RUNNING...\n")

    for symbol in symbols:
        analyze_symbol(symbol)

    time.sleep(20)
