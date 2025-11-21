# backend/renderer/config.py

# --- KONFIGURASI UMUM (Bersama untuk Semua Template) ---
FONT_PATH = "handwriting.ttf"
OUTPUT_PATH = "hasil_final.png" 
INK_COLOR = (20, 20, 20) 
BASE_OFFSET_FACTOR = 0.27 # Offset yang didapat dari testing font size 30
JITTER_MAX_PIXELS = 2
INK_VARIATION_MAX = 10
TILT_MAX_DEGREES = 0.5 # Rotasi per kata

# --- KAMUS KONFIGURASI KERTAS (UNIQUE CONFIGS) ---
# Kunci di sini akan digunakan Bot Telegram sebagai opsi pilihan.
CONFIGS = {
    # DEFAULT (Kertas yang sudah Anda uji coba)
    "Kertas_Garis_A": {
        "BACKGROUND_PATH": "kertas.jpg",
        "FONT_SIZE": 20,
        "LINE_DISTANCE": 35,     # Jarak antar garis lebar
        "LEFT_MARGIN": 15,
        "TOP_LINE_Y": 162,
        "RIGHT_MARGIN_PAD": 5,
        "BOTTOM_LINE_Y": 1500,
    },
    # CONTOH KERTAS LAIN (Anda harus menyediakan file gambarnya di folder backend/)
    "Kertas_Garis_B": {
        "BACKGROUND_PATH": "kertas_garis_sempit.jpg",
        "FONT_SIZE": 28,
        "LINE_DISTANCE": 50,     # Jarak antar garis sempit
        "LEFT_MARGIN": 100,
        "TOP_LINE_Y": 160,
        "RIGHT_MARGIN_PAD": 30,
        "BOTTOM_LINE_Y": 1050,
    },
    "Kertas_Kotak": {
        "BACKGROUND_PATH": "kertas_kotak.jpg",
        "FONT_SIZE": 25,
        "LINE_DISTANCE": 40,     # Sangat kecil
        "LEFT_MARGIN": 80,
        "TOP_LINE_Y": 150,
        "RIGHT_MARGIN_PAD": 70,
        "BOTTOM_LINE_Y": 1080,
    },
}

# Tentukan template default jika tidak ada pilihan dari Bot
DEFAULT_TEMPLATE = "Kertas_Garis_A"