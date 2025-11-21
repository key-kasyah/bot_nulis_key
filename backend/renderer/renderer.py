# backend/renderer/renderer.py
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io

# Import semua konfigurasi, termasuk kamus CONFIGS dan DEFAULT_TEMPLATE
from .config import (
    FONT_PATH, OUTPUT_PATH, INK_COLOR, BASE_OFFSET_FACTOR, 
    JITTER_MAX_PIXELS, TILT_MAX_DEGREES, INK_VARIATION_MAX,
    CONFIGS, DEFAULT_TEMPLATE
)

def get_text_size(draw, text, font):
    """Menghitung lebar teks menggunakan textbbox."""
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    return width, 0

def get_font_metrics(font):
    """Menghitung offset baseline dari font size."""
    # Menggunakan faktor BASE_OFFSET_FACTOR dari config
    return int(font.size * BASE_OFFSET_FACTOR) 

def wrap_text(text, font, max_width, draw):
    """Memecah teks menjadi baris berdasarkan batas lebar (word wrap)."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        w, _ = get_text_size(draw, test_line, font)

        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    lines.append(current_line.strip())
    return lines


def render_handwriting(
    text,
    template_name=DEFAULT_TEMPLATE, # Tambahkan template_name sebagai input
    output_path=OUTPUT_PATH,
):
    """Fungsi utama untuk merender teks, menggunakan konfigurasi dinamis dan multi-page."""
    
    # --- PENTING: Panggil Konfigurasi Sesuai Nama Template ---
    config = CONFIGS.get(template_name, CONFIGS[DEFAULT_TEMPLATE])
    
    # Tetapkan variabel dari konfigurasi yang dipilih
    BACKGROUND_PATH = config["BACKGROUND_PATH"]
    FONT_SIZE = config["FONT_SIZE"]
    LINE_DISTANCE = config["LINE_DISTANCE"]
    LEFT_MARGIN = config["LEFT_MARGIN"]
    TOP_LINE_Y = config["TOP_LINE_Y"]
    RIGHT_MARGIN_PAD = config["RIGHT_MARGIN_PAD"]
    BOTTOM_LINE_Y = config["BOTTOM_LINE_Y"]
    # ----------------------------------------------------
    
    # 1. Pra-pemrosesan Teks menjadi Baris Terstruktur
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    
    # Gunakan background image untuk mendapatkan lebar (harus membaca file karena lebar kertas berbeda)
    try:
        bg_width = Image.open(BACKGROUND_PATH).width
    except FileNotFoundError:
        raise FileNotFoundError(f"File background '{BACKGROUND_PATH}' tidak ditemukan. Pastikan sudah ada di folder backend/.")

    draw_dummy = ImageDraw.Draw(Image.new('RGB', (bg_width, 100))) 
    usable_width = bg_width - LEFT_MARGIN - RIGHT_MARGIN_PAD
    
    all_lines = []
    paragraphs = text.split("\n")
    for p in paragraphs:
        if p.strip() == "":
            all_lines.append("")
        else:
            wrapped_lines = wrap_text(p, font, usable_width, draw_dummy)
            all_lines.extend(wrapped_lines)

    # 2. Inisialisasi Proses Rendering Multi-page
    baseline_offset = get_font_metrics(font)
    page_number = 1
    line_index = 0
    total_lines = len(all_lines)

    base_output_name = output_path.replace(".png", "") 

    while line_index < total_lines:
        # Load background baru untuk halaman ini
        bg = Image.open(BACKGROUND_PATH).convert("RGBA")
        
        y_position = TOP_LINE_Y # Reset posisi Y ke awal halaman
        lines_started_on_page = 0
        
        while line_index < total_lines:
            line = all_lines[line_index]
            
            # Cek Batas Bawah: Jika baris berikutnya melebihi batas, hentikan halaman ini.
            if y_position > BOTTOM_LINE_Y:
                break 

            # --- RENDER KATA PER KATA DENGAN ROTASI ---
            if line: 
                words = line.split(' ')
                current_x = LEFT_MARGIN

                for word in words:
                    word_with_space = word + ' ' 
                    
                    # 1. Tentukan Efek Realisme
                    jitter_x = random.randint(-JITTER_MAX_PIXELS, JITTER_MAX_PIXELS)
                    jitter_y = random.randint(-JITTER_MAX_PIXELS, JITTER_MAX_PIXELS)
                    ink_variation = random.randint(0, INK_VARIATION_MAX)
                    final_ink_color = tuple(max(0, c - ink_variation) for c in INK_COLOR[:3])
                    tilt_degree = random.uniform(-TILT_MAX_DEGREES, TILT_MAX_DEGREES)

                    # 2. Ukur dan Gambar pada Canvas Sementara
                    bbox = draw_dummy.textbbox((0, 0), word_with_space, font=font)
                    temp_width = bbox[2] - bbox[0]
                    temp_height = bbox[3] - bbox[1]
                    
                    # Buat kanvas sementara dengan padding untuk rotasi
                    pad = int(temp_height * 0.5) 
                    temp_img = Image.new('RGBA', (temp_width + pad, temp_height + pad), (255, 255, 255, 0))
                    temp_draw = ImageDraw.Draw(temp_img)
                    
                    # Gambar kata
                    temp_draw.text(
                        (pad // 2, pad // 2), 
                        word_with_space, 
                        font=font, 
                        fill=final_ink_color
                    )
                    
                    # 3. Rotasi dan Tempel
                    rotated_img = temp_img.rotate(tilt_degree, expand=True)

                    y_start = y_position - baseline_offset + jitter_y
                    
                    bg.paste(rotated_img, (current_x + jitter_x, y_start), rotated_img)
                    
                    current_x += temp_width

            # Pindah ke posisi Y berikutnya & update index global
            y_position += LINE_DISTANCE 
            line_index += 1
            lines_started_on_page += 1

        # 4. Simpan Halaman yang Sudah Selesai
        if lines_started_on_page > 0 or page_number == 1:
            output_filename = f"{base_output_name}_page{page_number}.png"
            bg.save(output_filename)
            print(f"Rendering Selesai. Disimpan ke {output_filename}")
            page_number += 1
        
        if line_index == total_lines and lines_started_on_page > 0:
            break


# --------------------------------------------------------
# Contoh Pemakaian (Hanya untuk testing lokal)
# --------------------------------------------------------

if __name__ == "__main__":
    # Contoh teks panjang untuk menguji multi-page
    long_text = ""
    for i in range(1, 40): # 40 baris
        long_text += f"Baris ke-{i}: Ini adalah tulisan yang sangat panjang untuk menguji batas kertas.\n"
    
    # Pastikan Anda memiliki file kertas_garis_b.jpg jika ingin menguji template ini
    render_handwriting(
        text=long_text,
        template_name="Kertas_Garis_B", # Uji template lain
        output_path="testing_output.png"
    )