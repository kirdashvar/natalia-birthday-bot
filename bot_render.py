import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
import googleapiclient.discovery
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8730010021:AAFAKpsqk1olb2NIKGSWr4lBTg-gTkLsBMU"
GOOGLE_DRIVE_FOLDER_ID = "1hGoCZT7eXtFDHGE24khuT2ufuFie30b_"

# Завантажимо список відео з Google Drive
def get_videos_from_drive():
    try:
        service = googleapiclient.discovery.build('drive', 'v3', developerKey='AIzaSyBKp9Ql-QQwDHSZiQEPPM9J3q_h6j-1y4Q')
        
        query = f"'{GOOGLE_DRIVE_FOLDER_ID}' in parents and mimeType='video/mp4' and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=100,
            orderBy='name'
        ).execute()
        
        videos = results.get('files', [])
        logger.info(f"✅ Знайдено {len(videos)} відео на Google Drive")
        return videos
    except Exception as e:
        logger.error(f"Помилка при завантаженні з Google Drive: {e}")
        return []

VIDEOS = get_videos_from_drive()

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
            video = VIDEOS[idx]
            video_id = video['id']
            
            try:
                service = googleapiclient.discovery.build('drive', 'v3', developerKey='AIzaSyBKp9Ql-QQwDHSZiQEPPM9J3q_h6j-1y4Q')
                
                # Завантажуємо відео з Google Drive
                request = service.files().get_media(fileId=video_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                fh.seek(0)
                await query.message.reply_video(fh)
                await query.delete_message()
                
                if idx < len(VIDEOS) - 1:
                    kb = [[InlineKeyboardButton("💚 Хочу ще!", callback_data=f"video_{idx + 1}")]]
                    txt = "💚"
                else:
                    kb = [[InlineKeyboardButton("🔄 Переглянути ще раз", callback_data="video_0")]]
                    txt = "З днем народження, Наталіє! 💚"
                    
                await query.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))
                
            except Exception as e:
                logger.error(f"Помилка при завантаженні відео: {e}")
                await query.message.reply_text(f"❌ Помилка: {str(e)}")

def main():
    if not VIDEOS:
        logger.error("❌ Відео не знайдено на Google Drive!")
        return
    
    print(f"\n{'='*60}\n✅ БОТ ГОТОВИЙ!\n{'='*60}\n🤖 Запускаємо...\n")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == "__main__":
    main()
