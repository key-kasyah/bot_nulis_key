# bot/bot.py

import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import io
import os

# --- KONFIGURASI BOT ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8311715181:AAHHH33gVQomZNkTP4pr9dELzCqeD_HkOfA") 

# Ambil URL API dari Variabel Lingkungan. URL ini harus URL PUBLIK API FASTAPI Anda.
# Jika tidak ditemukan, fallback ke URL lokal (hanya untuk pengujian lokal).
API_URL = os.environ.get("HANDWRITING_API_URL", "http://127.0.0.1:8000/generate")
# Konfigurasi Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- HANDLER PERINTAH ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menanggapi perintah /start."""
    await update.message.reply_text(
        "Halo! Saya adalah bot pembuat tulisan tangan. "
        "Kirimkan saja teks yang ingin Anda ubah, dan saya akan merendernya."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menanggapi perintah /help."""
    await update.message.reply_text(
        "Cukup kirimkan pesan teks. Saya akan mengirimkannya ke backend AI untuk diubah menjadi gambar tulisan tangan."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menerima teks, mengirim ke API, dan mengembalikan gambar."""
    user_text = update.message.text
    
    # Beri notifikasi ke user bahwa proses dimulai
    await update.message.reply_text("Memproses teks... Mohon tunggu sebentar.")

    try:
        # 1. KIRIM TEKS KE API FASTAPI LOKAL
        # FastAPI endpoint POST /generate mengharapkan data formulir atau JSON. 
        # Karena endpoint kita menerima 'text: str', kita bisa mengirimkannya sebagai JSON.
        
        # --- MISSING LINE GOES HERE ---
        user_text = update.message.text
        data_to_send = {"text": user_text} # <-- ADD THIS LINE

        response = requests.post(API_URL, data=data_to_send) 
        response.raise_for_status() # Cek jika ada HTTP error (4xx atau 5xx)

        # 2. API mengembalikan file gambar, kita membacanya
        image_data = response.content
    
        await update.message.reply_photo(
            photo=io.BytesIO(image_data),
            caption="Ini tulisan tangan Anda!"
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Error saat menghubungi API: {e}")
        await update.message.reply_text(
            "Maaf, terjadi kesalahan saat menghubungi server rendering. "
            "Pastikan server FastAPI (http://127.0.0.1:8000) sedang berjalan!"
        )
    except Exception as e:
        logger.error(f"Error tak terduga: {e}")
        await update.message.reply_text(f"Terjadi error tak terduga.")

def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    # Buat aplikasi bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Tambahkan handler
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Handler untuk semua pesan teks non-perintah
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Mulai bot (polling)
    print("Bot sedang berjalan...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Penting: Pastikan server FastAPI di 'backend' berjalan sebelum menjalankan bot ini!
    main()