from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import Response
import os
import tempfile
import glob
import shutil 
import io 

# --- IMPOR ABSOLUT SANGAT SEDERHANA ---
from renderer.renderer import render_handwriting 
from renderer.config import DEFAULT_TEMPLATE, CONFIGS 
# -------------------------------------

app = FastAPI()
@app.get("/")
def read_root():
    """Endpoint dasar untuk mengecek status API."""
    return {"status": "Running", "message": "Handwriting Generator API is ready."}


@app.post("/generate")
# Menerima teks (wajib) dan template_name (opsional, dengan default)
def generate_handwriting_image(
    text: str = Form(...),
    template_name: str = Form(DEFAULT_TEMPLATE) # Gunakan template default
):
    """
    Endpoint yang menerima teks dan template, merender gambar, dan mengembalikannya (single-page stable).
    """
    
    base_filename = "tulisan_tangan"
    
    # 1. Validasi Template
    if template_name not in CONFIGS:
        template_name = DEFAULT_TEMPLATE
    
    # 2. Buat direktori sementara
    with tempfile.TemporaryDirectory() as tmpdir:
        
        temp_output_base_path = os.path.join(tmpdir, base_filename)
        
        try:
            # 3. Panggil Renderer dengan template_name
            render_handwriting(
                text=text,
                template_name=template_name, # Teruskan template_name ke renderer
                output_path=temp_output_base_path + ".png" 
            )
            
            # 4. Cek File Output
            output_files = glob.glob(os.path.join(tmpdir, f"{base_filename}*.png"))
            output_files.sort()
            
            if not output_files:
                 raise Exception("Renderer sukses, tetapi tidak ada file output PNG yang ditemukan.")

            # --- LOGIKA STABILITAS SINGLE-PAGE (Mengabaikan halaman > 1) ---
            
            final_file_path = output_files[0] # Selalu ambil file pertama (Halaman 1)
            
            # Cek apakah ada halaman tambahan yang terpotong untuk pesan peringatan
            has_extra_pages = len(output_files) > 1
            
            # 5. Baca file ke memori sebelum with tempfile berakhir
            with open(final_file_path, "rb") as f:
                file_content = f.read()

            # 6. Kembalikan Respons dari memori (bytes)
            return Response(
                content=file_content, 
                media_type="image/png", 
                headers={
                    "Content-Disposition": f"attachment; filename={base_filename}.png",
                    # Header kustom untuk memberi tahu Bot tentang status multi-page
                    "X-Multi-Page-Status": "True" if has_extra_pages else "False"
                }
            )

        except Exception as e:
            # Penanganan error jika rendering gagal
            print(f"Rendering Error: {e}")
            raise HTTPException(status_code=500, detail=f"Terjadi kesalahan rendering: {str(e)}")