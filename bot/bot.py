# bot/bot.py

import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes, 
    ConversationHandler, CallbackQueryHandler
)
import io
import os

# --- KONFIGURASI BOT & API ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8311715181:AAHHH33gVQomZNkTP4pr9dELzCqeD_HkOfA") 
API_URL = os.environ.get("HANDWRITING_API_URL", "http://127.0.0.1:8000/generate")

# Konfigurasi Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- STATE MANAGEMENT & TEMPLATE OPTIONS (Harus sinkron dengan config.py di backend) ---
TUNGGU_TEMPLATE = 1
TUNGGU_TEKS = 2

# Asumsi template yang tersedia (digunakan untuk tombol inline)
TEMPLATE_OPTIONS = ["Kertas_Garis_A", "Kertas_Garis_B", "Kertas_Kotak"] 
DEFAULT_TEMPLATE = "Kertas_Garis_A"

# --- HANDLER UMUM ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menanggapi perintah /start."""
    await update.message.reply_text(
        "Halo! Saya adalah bot pembuat tulisan tangan.\n"
        "Gunakan /tulis untuk memulai render, atau /harga untuk melihat opsi kredit dan pembayaran."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menanggapi perintah /help."""
    await update.message.reply_text(
        "• /tulis: Mulai proses rendering (pilih kertas dan kirim teks).\n"
        "• /harga: Lihat paket kredit dan detail pembayaran.\n"
    )

async def price_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menanggapi perintah /harga atau /beli."""
    
    price_message = (
        "**💰 PRICE LIST BOT HANDWRITING GENERATOR**\n\n"
        # ... (Sisa pesan price list Anda yang sudah benar)
        "**— PAKET KREDIT JUAL —**\n"
        "1. **Paket Dasar (1.000 Kredit):** Rp 10.000\n"
        "2. **Paket Populer (3.000 Kredit):** Rp 25.000\n"
        "3. **Paket Super (7.500 Kredit):** Rp 50.000\n\n"

        "**— LANGGANAN PREMIUM —**\n"
        "Akses tanpa batas dan fitur eksklusif.\n"
        "• **Langganan 1 Bulan:** **Rp 35.000**\n\n"
        
        "**— METODE PEMBAYARAN (KONFIRMASI MANUAL) —**\n"
        "1. **SEA BANK (a.n. Ukkasyah M.a)**: `901165868910`\n"
        "2. **DANA (a.n. Ukkasyah M.a)**: `081342356336`\n\n"
        
        "**— KONFIRMASI —**\n"
        "Kirim bukti pembayaran dan ID Telegram Anda ke Admin (WA: 088804705283 atau Telegram: @Willionafree) untuk aktivasi."
    )
    
    await update.message.reply_text(
        price_message, 
        parse_mode='Markdown'
    )

# --- HANDLER CONVERSATION (/tulis) ---

async def tulis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ENTRY POINT: Memulai percakapan /tulis dan meminta pilihan template."""
    
    keyboard = []
    for template in TEMPLATE_OPTIONS:
        # Menghilangkan underscore untuk tampilan tombol
        keyboard.append([InlineKeyboardButton(template.replace('_', ' '), callback_data=template)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Pilih jenis kertas yang ingin Anda gunakan:",
        reply_markup=reply_markup
    )
    # Pindah ke state TUNGGU_TEMPLATE
    return TUNGGU_TEMPLATE

async def template_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """STATE 1: Menerima pilihan template dan meminta input teks."""
    query = update.callback_query
    await query.answer()

    template_name = query.data
    context.user_data['template_name'] = template_name # Simpan pilihan user

    # Hapus tombol setelah diklik
    await query.edit_message_text(
        text=f"Anda memilih: **{template_name.replace('_', ' ')}**\n\n"
             f"Sekarang, silakan kirimkan teks yang ingin Anda render.",
        parse_mode='Markdown'
    )
    # Pindah ke state TUNGGU_TEKS
    return TUNGGU_TEKS

async def render_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """STATE 2: Menerima input teks dan memicu rendering."""
    user_text = update.message.text
    template_name = context.user_data.get('template_name', DEFAULT_TEMPLATE)
    user_id = update.message.from_user.id
    
    await update.message.reply_text("Memproses teks... Mohon tunggu sebentar.")

    try:
        # Kirim data FORMULIR termasuk template_name
        data_to_send = {
            "text": user_text,
            "template_name": template_name,
            "user_id": user_id # Kirim User ID
        }
        response = requests.post(API_URL, data=data_to_send)
        response.raise_for_status() 

        # Ambil Header Kustom
        is_multi_page = response.headers.get("X-Multi-Page-Status", "False") == "True"

        # Kirim gambar
        image_data = response.content
        await update.message.reply_photo(
            photo=io.BytesIO(image_data),
            caption=f"Ini tulisan tangan Anda (Template: {template_name.replace('_', ' ')})!"
        )

        # Peringatan Multi-page
        if is_multi_page:
            await update.message.reply_text(
                "⚠️ **PERINGATAN:** Teks Anda terlalu panjang dan hanya Halaman 1 yang dikirimkan. "
                "Mohon kirim teks yang lebih pendek."
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Error saat menghubungi API: {e}")
        await update.message.reply_text("Maaf, terjadi kesalahan saat menghubungi server rendering.")
    except Exception as e:
        logger.error(f"Error tak terduga: {e}")
        await update.message.reply_text(f"Terjadi error tak terduga: {str(e)}")
        
    # Akhiri percakapan
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menghentikan percakapan saat ini."""
    await update.message.reply_text(
        "Percakapan dibatalkan. Anda dapat mulai lagi dengan /tulis."
    )
    context.user_data.clear()
    return ConversationHandler.END

# --- MAIN RUNNER ---

def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Conversation Handler untuk /tulis
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("tulis", tulis_command)],
        
        states={
            TUNGGU_TEMPLATE: [CallbackQueryHandler(template_callback)],
            TUNGGU_TEKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, render_state)],
        },
        
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    
    # Handler Umum
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("harga", price_list_command))
    application.add_handler(CommandHandler("beli", price_list_command))

    print("Bot sedang berjalan...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()