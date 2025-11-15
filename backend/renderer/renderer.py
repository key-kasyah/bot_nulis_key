# renderer/renderer.py
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io

# Impor relatif dari file config di direktori yang sama
from .config import (
    FONT_PATH, BACKGROUND_PATH, FONT_SIZE, LINE_DISTANCE,
    LEFT_MARGIN, TOP_LINE_Y, RIGHT_MARGIN_PAD, INK_COLOR,
    BASE_OFFSET_FACTOR, BOTTOM_LINE_Y, 
    JITTER_MAX_PIXELS, TILT_MAX_DEGREES, INK_VARIATION_MAX,
    OUTPUT_PATH 
)

def get_text_size(draw, text, font):
    """Menghitung lebar teks."""
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    return width, 0

def get_font_metrics(font):
    """Menghitung offset baseline dari font size."""
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
    output_path=OUTPUT_PATH,
):
    """Fungsi utama untuk merender teks, mendukung pemisahan menjadi multi-page."""
    
    # 1. Pra-pemrosesan Teks menjadi Baris Terstruktur
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    # Gunakan background image untuk mendapatkan lebar
    bg_width = Image.open(BACKGROUND_PATH).width
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

    # Dapatkan nama file base untuk output
    base_output_name = output_path.replace(".png", "") # Hapus ekstensi .png

    while line_index < total_lines:
        # Load background baru untuk halaman ini
        bg = Image.open(BACKGROUND_PATH).convert("RGBA")
        draw = ImageDraw.Draw(bg)
        
        y_position = TOP_LINE_Y # Reset posisi Y ke awal halaman
        
        lines_started_on_page = 0
        current_page_lines = []
        
        # 3. Loop untuk Merender Baris di Halaman Saat Ini
        while line_index < total_lines:
            line = all_lines[line_index]
            
            # Cek Batas Bawah: Jika baris berikutnya (y_position + LINE_DISTANCE) melebihi batas, hentikan halaman ini.
            if y_position > BOTTOM_LINE_Y:
                # Batas terlampaui, keluar dari loop halaman saat ini
                break 

            # --- RENDER BARIS ---
            if line: 
                # Logika Jitter dan Ink Variation
                jitter_x = random.randint(-JITTER_MAX_PIXELS, JITTER_MAX_PIXELS)
                jitter_y = random.randint(-JITTER_MAX_PIXELS, JITTER_MAX_PIXELS)
                ink_variation = random.randint(0, INK_VARIATION_MAX)
                final_ink_color = tuple(max(0, c - ink_variation) for c in INK_COLOR[:3])
                
                draw.text(
                    (LEFT_MARGIN + jitter_x, y_position - baseline_offset + jitter_y), 
                    line, 
                    font=font, 
                    fill=final_ink_color
                )
            
            # Pindah ke posisi Y berikutnya & update index global
            y_position += LINE_DISTANCE 
            line_index += 1
            lines_started_on_page += 1

        # 4. Simpan Halaman yang Sudah Selesai
        # Pastikan kita hanya menyimpan jika setidaknya ada satu baris yang diproses di halaman ini
        if lines_started_on_page > 0 or page_number == 1:
            output_filename = f"{base_output_name}_page{page_number}.png"
            bg.save(output_filename)
            print(f"Rendering Selesai. Disimpan ke {output_filename}")
            page_number += 1
        
        # Jika line_index mencapai total_lines, break dari loop utama
        if line_index == total_lines:
            break


# --------------------------------------------------------
# Contoh Pemakaian (Hanya untuk testing lokal)
# --------------------------------------------------------

if __name__ == "__main__":
    # Contoh teks panjang untuk menguji multi-page
    long_text = ""
    for i in range(1, 40): # 40 baris
        long_text += f"Baris ke-{i}: Ini adalah tulisan yang sangat panjang untuk menguji batas kertas.\n"
    
    render_handwriting(
        text=long_text,
        output_path="testing_output.png"
    )