from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔴 حط التوكن والايدي مباشرة (اختبار فقط)
TOKEN = "AAFK96pEm4URu46aGw9e7SAfsUTh9WxZd5k"
CHAT_ID = "6341614127"

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 البوت شغال!")

# أمر /test
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ كل شيء تمام")

# تشغيل البوت
def main():
    if not TOKEN:
        raise ValueError("❌ التوكن فاضي")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))

    print("🚀 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
