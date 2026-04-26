import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "PUT_TELEGRAM_TOKEN_HERE"

# 🔥 هنا نحط API تبع تحليل الصور (مؤقت تحليل بسيط)
def analyze_image():
    # تحليل مبدئي (نطور لاحقًا)
    import random

    signals = ["BUY 🟢", "SELL 🔴", "WAIT ⚠️"]
    reasons = [
        "ترند صاعد + زخم قوي",
        "ترند هابط + كسر دعم",
        "سوق متذبذب"
    ]

    strength = random.randint(50, 90)

    return signals[random.randint(0,2)], reasons[random.randint(0,2)], strength

# 📥 عند استقبال صورة
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 جاري تحليل الشارت...")

    signal, reason, strength = analyze_image()

    msg = f"""
🤖 تحليل الشارت

📊 الإشارة: {signal}
💡 السبب: {reason}
💪 القوة: {strength}%

⚠️ تأكد قبل الدخول
"""

    await update.message.reply_text(msg)

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("🤖 IMAGE BOT RUNNING...")
app.run_polling()
