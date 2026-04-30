import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8730010021:AAFAKpsqk1olb2NIKGSWr4lBTg-gTkLsBMU"
FILE_IDS_FILE = "video_file_ids.json"

# Завантажимо File ID з JSON
try:
    with open(FILE_IDS_FILE, 'r', encoding='utf-8') as f:
        FILE_IDS_DICT = json.load(f)
    VIDEOS = list(FILE_IDS_DICT.keys())
    print(f"\n✅ Завантажено {len(VIDEOS)} File ID\n")
except FileNotFoundError:
    print(f"❌ Файл {FILE_IDS_FILE} не знайдено!")
    VIDEOS = []
    FILE_IDS_DICT = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """Привіт 🥰
Сьогодні твій день, і ми хочемо, щоб він почався по-особливому!
За цим посиланням - сюрприз від людей, яким пощастило працювати з тобою.
Рекомендуємо дивитись у спокійній атмосфері й з усмішкою ☺️
З днем народження! 🎂
*відео містить БТ 😉"""
    
    keyboard = [[InlineKeyboardButton("🎉 Розпочати подорож", callback_data="video_0")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("video_"):
        idx = int(data.split("_")[1])
        if 0 <= idx < len(VIDEOS):
            video_file = VIDEOS[idx]
            file_id = FILE_IDS_DICT[video_file]
            
            try:
                # Надсилаємо відео через File ID (дуже швидко!)
                await query.message.reply_video(file_id)
                await query.delete_message()
                
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
    if not VIDEOS:
        print("❌ Немає File ID для відео!")
        return
    
    print(f"\n{'='*60}\n✅ БОТ ГОТОВИЙ!\n{'='*60}\n🤖 Запускаємо...\n")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == "__main__":
    main()
