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
# Menerima teks sebagai Data Formulir (Form Data)
def generate_handwriting_image(text: str = Form(...)):
    """
    Endpoint yang menerima teks dan mengembalikan gambar tulisan tangan.
    Menggunakan Response dari memori untuk menghindari FileNotFoundError pada temporary directory.
    """
    
    base_filename = "tulisan_tangan"
    
    # Buat direktori sementara
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
                 raise Exception("Renderer sukses, tetapi tidak ada file output PNG yang ditemukan.")

            # KASUS A: SATU HALAMAN (ATAU Halaman Pertama)
            if len(output_files) >= 1:
                final_file_path = output_files[0]
                
                # --- PERBAIKAN KRITIS: Baca file ke memori sebelum with berakhir ---
                with open(final_file_path, "rb") as f:
                    file_content = f.read()

                # Kembalikan Respons dari memori (bytes)
                return Response(
                    content=file_content, 
                    media_type="image/png", 
                    headers={
                        "Content-Disposition": f"attachment; filename={base_filename}.png"
                    }
                )
            
            # KASUS B: MULTI-PAGE (Mengembalikan ZIP)
            # Logika ini tidak akan tercapai jika hanya ada 1 halaman, tapi tetap penting.
            else: 
                zip_name = f"{base_filename}_multi"
                
                shutil.make_archive(
                    base_name=os.path.join(tmpdir, zip_name),
                    format='zip',
                    root_dir=tmpdir,
                    base_dir='.' 
                )
                
                zip_path = os.path.join(tmpdir, f"{zip_name}.zip")

                # Kembalikan file ZIP
                return FileResponse(
                    path=zip_path,
                    media_type="application/zip",
                    filename=f"{zip_name}.zip"
                )

        except Exception as e:
            print(f"Rendering Error: {e}")
            raise HTTPException(status_code=500, detail=f"Terjadi kesalahan rendering: {str(e)}")