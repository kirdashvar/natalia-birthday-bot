import json, os, http.server, socketserver, threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Сервер для стабільності на Render
def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
FILE_IDS_FILE = "video_file_ids.json"

try:
    with open(FILE_IDS_FILE, 'r', encoding='utf-8') as f:
        FILE_IDS_DICT = json.load(f)
    VIDEOS = list(FILE_IDS_DICT.keys())
except:
    VIDEOS = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Використовуємо потрійні лапки для багаторядкового тексту
    text = """Привіт 🥰
Сьогодні твій день, і ми хочемо, щоб він почався по-особливому!
За цим посиланням - сюрприз від людей, яким пощастило працювати з тобою.
Рекомендуємо дивитись у спокійній атмосфері й з усмішкою ☺️
З днем народження! 🎂

*відео містить БТ 😉"""
    
    kb = [[InlineKeyboardButton("🎉 Розпочати подорож", callback_data="v_0")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[1])
    if 0 <= idx < len(VIDEOS):
        try:
            await query.message.reply_video(FILE_IDS_DICT[VIDEOS[idx]])
            if idx < len(VIDEOS) - 1:
                kb, txt = [[InlineKeyboardButton("💚 Хочу ще!", callback_data=f"v_{idx+1}")]], "💚"
            else:
                kb, txt = [[InlineKeyboardButton("🔄 З початку", callback_data="v_0")]], "З днем народження! 💚"
            await query.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))
        except: pass

def main():
    if not TOKEN or not VIDEOS: return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
