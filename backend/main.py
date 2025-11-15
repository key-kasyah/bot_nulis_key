# D:\kodingan\backend\main.py
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import Response, FileResponse # Import Response
import os
import tempfile
import glob
import shutil 
import io # Diperlukan untuk penanganan data biner

# Impor dengan perbaikan Impor Absolut
try:
    from renderer.renderer import render_handwriting 
    from renderer.config import OUTPUT_PATH 
except ImportError as e:
    raise ImportError(f"Gagal mengimpor modul renderer. Pastikan Anda sudah membuat file __init__.py di folder 'renderer/'. Error detail: {e}") 


app = FastAPI()

@app.get("/")
def read_root():
    """Endpoint dasar untuk mengecek status API."""
    return {"status": "Running", "message": "Handwriting Generator API is ready."}


@app.post("/generate")
def generate_handwriting_image(text: str = Form(...)):
    base_filename = "tulisan_tangan"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_output_base_path = os.path.join(tmpdir, base_filename)
        
        try:
            # 1. Panggil Renderer
            render_handwriting(
                text=text,
                output_path=temp_output_base_path + ".png" 
            )
            
            # 2. Cek File Output
            output_files = glob.glob(os.path.join(tmpdir, f"{base_filename}*.png"))
            output_files.sort()
            
            if not output_files:
                 raise Exception("Renderer gagal membuat file output.")

            # --- MODIFIKASI KRITIS UNTUK STABILITAS (Hanya Ambil Halaman 1) ---
            final_file_path = output_files[0] # Selalu ambil file pertama (Halaman 1)
            
            # Cek apakah ada halaman tambahan yang terpotong (untuk pesan peringatan di Bot)
            has_extra_pages = len(output_files) > 1
            
            # 3. Baca file ke memori
            with open(final_file_path, "rb") as f:
                file_content = f.read()

            # 4. Kembalikan Respons dari memori (bytes)
            # Kunci: Menggunakan header kustom untuk memberi tahu Bot status Multi-page
            return Response(
                content=file_content, 
                media_type="image/png", 
                headers={
                    "Content-Disposition": f"attachment; filename={base_filename}.png",
                    # Tambahkan header kustom untuk memberi tahu Bot
                    "X-Multi-Page-Status": "True" if has_extra_pages else "False"
                }
            )

        except Exception as e:
            print(f"Rendering Error: {e}")
            raise HTTPException(status_code=500, detail=f"Terjadi kesalahan rendering: {str(e)}")