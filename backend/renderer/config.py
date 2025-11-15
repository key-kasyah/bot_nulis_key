# config.py

# --- Umum ---
# Lokasi file font tulisan tangan
FONT_PATH = "handwriting.ttf"

# Lokasi background kertas
BACKGROUND_PATH = "kertas.jpg"

# Lokasi default untuk output
OUTPUT_PATH = "hasil_final.png" 

# --- Parameter Rendering ---
# Ukuran font, diatur ke 30
FONT_SIZE = 20

# Jarak vertikal antar garis kertas (dalam piksel). Anda atur ke 40.
LINE_DISTANCE = 35

# Margin horizontal dan vertikal
LEFT_MARGIN = 15 # Posisi X awal penulisan (Kiri)
TOP_LINE_Y = 162  # Posisi Y garis pertama (Atas)
RIGHT_MARGIN_PAD = 5 # Padding kanan untuk menghitung usable_width (Anda atur ke 20)

# Warna tinta (RGB Tuple - hitam hampir murni)
INK_COLOR = (20, 20, 20) 

# Offset Baseline (nilai kritis untuk keselarasan)
# Nilai ini harus memberikan teks "duduk" tepat di garis.
BASE_OFFSET_FACTOR = 0.27 # Nilai yang bekerja untuk Font Size 30

# --- Parameter Efek Natural (Untuk diaktifkan selanjutnya) ---
# Jitter: Pergeseran horizontal dan vertikal acak (0 = tanpa jitter)
JITTER_MAX_PIXELS = 0

# Tilt: Rotasi kecil per kata atau per baris (dalam derajat)
TILT_MAX_DEGREES = 0

# Ink Variation: Seberapa bervariasi warna tinta (dari 0-255)
INK_VARIATION_MAX = 0