import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from PIL import Image

TOKEN = os.getenv("TOKEN")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    await file.download_to_drive("chart.jpg")

    img = Image.open("chart.jpg")

    # تحليل بسيط (تقدر تطوره لاحقًا)
    decision = "📈 BUY" if img.size[0] > 500 else "📉 SELL"

    await update.message.reply_text(f"التحليل: {decision}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.PHOTO, handle_image))

app.run_polling)
