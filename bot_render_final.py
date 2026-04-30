import json
import os
import http.server
import socketserver
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- СЕРВЕР ДЛЯ СТАБІЛЬНОСТІ (ЩОБ НЕ ЗАСИНАВ) ---
def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🌍 Health check server started on port {port}")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Server error: {e}")

threading.Thread(target=run_health_check_server, daemon=True).start()
# -----------------------------------------------

# ТЕПЕР ТОКЕН БЕРЕТЬСЯ З НАЛАШТУВАНЬ RENDER
TOKEN = os.environ.get("TELEGRAM_TOKEN")
FILE_IDS_FILE = "video_file_ids.json"

try:
    with open(FILE_IDS_FILE, 'r', encoding='utf-8') as f:
        FILE_IDS_DICT = json.load(f)
    VIDEOS = list(FILE_IDS_DICT.keys())
    print(f"✅ Завантажено {len(VIDEOS)} File ID")
except Exception as e:
    print(f"❌ Помилка завантаження файлів: {e}")
    VIDEOS = []
    FILE_IDS_DICT = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "Привіт 🥰
Сьогодні твій день, і ми хочемо, щоб він почався по-особливому!
За цим посиланням - сюрприз від людей, яким пощастило працювати з тобою.
Рекомендуємо дивитись у спокійній атмосфері й з усмішкою ☺️
З днем народження! 🎂

*відео містить БТ 😉"
    keyboard = [[InlineKeyboardButton("🎉 Розпочати подорож", callback_data="video_0")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[1])
    
    if 0 <= idx < len(VIDEOS):
        file_id = FILE_IDS_DICT[VIDEOS[idx]]
        try:
            await query.message.reply_video(file_id)
            if idx < len(VIDEOS) - 1:
                kb = [[InlineKeyboardButton("💚 Хочу ще!", callback_data=f"video_{idx + 1}")]]
                txt = "💚"
            else:
                kb = [[InlineKeyboardButton("🔄 Переглянути ще раз", callback_data="video_0")]]
                txt = "З днем народження, Наталіє! 💚"
            await query.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e:
            await query.message.reply_text(f"❌ Помилка: {str(e)}")

def main():
    if not TOKEN:
        print("❌ ПОМИЛКА: Токен не знайдено в налаштуваннях Environment Variables!")
        return
    if not VIDEOS:
        return
    
    print("\n✅ БОТ ЗАПУЩЕНИЙ!\n🤖 Очікування повідомлень...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
