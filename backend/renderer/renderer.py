# renderer.py

from PIL import Image, ImageDraw, ImageFont
import random
import os


# Impor semua konfigurasi dari file config.py
from .config import (
    FONT_PATH, BACKGROUND_PATH, FONT_SIZE, LINE_DISTANCE,
    LEFT_MARGIN, TOP_LINE_Y, RIGHT_MARGIN_PAD, INK_COLOR,
    BASE_OFFSET_FACTOR, 
    JITTER_MAX_PIXELS, TILT_MAX_DEGREES, INK_VARIATION_MAX,
    OUTPUT_PATH 
)

def get_text_size(draw, text, font):
    """Menghitung lebar dan tinggi bounding box teks."""
    # textbbox (Pillow 10+): (left, top, right, bottom)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    # height = bbox[3] - bbox[1] # Tidak digunakan
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
    """Fungsi utama untuk merender teks tulisan tangan ke gambar."""
    # Cek ketersediaan file
    if not os.path.exists(BACKGROUND_PATH):
        print(f"ERROR: File background '{BACKGROUND_PATH}' tidak ditemukan.")
        return
    if not os.path.exists(FONT_PATH):
        print(f"ERROR: File font '{FONT_PATH}' tidak ditemukan.")
        return

    # Load background image
    bg = Image.open(BACKGROUND_PATH).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Offset dan Lebar dihitung dari config
    baseline_offset = get_font_metrics(font) 
    usable_width = bg.width - LEFT_MARGIN - RIGHT_MARGIN_PAD 

    paragraphs = text.split("\n")
    lines_rendered = 0 # Penghitung baris untuk mencegah penyimpangan vertikal (drift)

    for p in paragraphs:
        if p.strip() == "":
            wrapped_lines = [""]
        else:
            wrapped_lines = wrap_text(p, font, usable_width, draw)

        for line in wrapped_lines:
            # HITUNG POSISI Y DENGAN AKURAT:
            # Y = Posisi Y Awal + (Jumlah Baris yang Sudah Dirender * Jarak Antar Baris)
            y_position = TOP_LINE_Y + (lines_rendered * LINE_DISTANCE)
            
            if line: 
                # --- Implementasi Efek Natural (Masih 0, tapi kodenya siap) ---
                jitter_x = random.randint(-JITTER_MAX_PIXELS, JITTER_MAX_PIXELS)
                jitter_y = random.randint(-JITTER_MAX_PIXELS, JITTER_MAX_PIXELS)
                
                ink_variation = random.randint(0, INK_VARIATION_MAX)
                final_ink_color = tuple(max(0, c - ink_variation) for c in INK_COLOR[:3])
                # ---------------------------------------------------
                
                # Menggambar teks dengan penyesuaian Jitter
                draw.text(
                    (LEFT_MARGIN + jitter_x, y_position - baseline_offset + jitter_y), 
                    line, 
                    font=font, 
                    fill=final_ink_color
                )
            
            # Tingkatkan penghitung baris untuk baris berikutnya
            lines_rendered += 1 

    bg.save(output_path)
    print(f"Rendering Selesai. Disimpan ke {output_path}")


# --------------------------------------------------------
# Contoh Pemakaian
# --------------------------------------------------------

if __name__ == "__main__":
    render_handwriting(
        text=""" Di kota kecil bernama Lumina, hujan selalu turun setiap sore, dan warga menganggapnya sebagai bagian dari kehidupan sehari-hari, tetapi bagi seorang pemuda bernama Nara, hujan selalu membawa sesuatu yang lebih dalam dari sekadar cuaca, karena setiap tetesnya membangkitkan kenangan tentang seseorang yang sudah lama pergi. Nara sering berjalan menyusuri trotoar basah dengan payung biru tua yang warnanya mulai pudar, sambil merasakan udara lembap yang menempel di kulitnya, dan ia selalu berhenti di depan toko buku tua bernama Harmonia, tempat yang dulu menjadi dunia kecil milik dirinya dan sahabat masa kecilnya, Aurel. Toko itu berderit ketika pintunya dibuka, seakan menyambutnya dengan suara nostalgia, dan aroma kertas tua yang memenuhi ruangan selalu membuat dadanya terasa hangat sekaligus sesak, terutama karena tempat itu pernah menjadi saksi tawa—dan kepergian. Pemilik toko, seorang pria tua ramah bernama Renga, masih ingat betul bagaimana dua anak kecil dulu menghabiskan berjam-jam membaca buku petualangan di sudut toko, dan ia selalu menyapa Nara dengan tatapan yang seolah mengerti lebih dari yang ia ucapkan. Aurel pindah kota sepuluh tahun lalu tanpa sempat mengucapkan selamat tinggal dengan cara yang pantas, dan sejak saat itu Nara merasa bagian besar dari dirinya ikut hilang bersamanya, meski ia terus berusaha menjalani hari dengan normal. Hujan hari itu turun lebih deras dari biasanya, membuat kaca jendela toko terlihat seperti lukisan buram yang bergerak, dan Nara duduk di kursi kayu dekat jendela sambil membuka buku yang dulu sering ia baca bersama Aurel, sebuah buku yang halamannya masih menyimpan aroma kenangan. Ia teringat bagaimana Aurel pernah berkata bahwa hujan adalah cara langit untuk menunjukkan rasa rindu, dan kalimat itu melekat begitu kuat hingga ia tak pernah bisa mendengar hujan tanpa mengingatnya. Ketika ia menutup buku itu, ia merasa dadanya bergetar seperti sedang menahan sesuatu yang berat, dan Renga yang memperhatikannya kemudian berkata bahwa kenangan bisa menjadi beban ketika dipikul sendirian, tetapi juga bisa menjadi kekuatan jika mau dibagi. Sebelum Nara sempat menjawab, pintu toko kembali terbuka dan angin membawa aroma hujan ke dalam ruangan, membuat beberapa halaman buku di rak bergoyang pelan. Seorang perempuan masuk dengan payung berwarna krem, rambut coklat gelapnya sedikit basah dan matanya tampak mencari sesuatu, atau seseorang, tanpa ia sadari. Nara menatapnya lama, dengan tatapan yang berubah dari bingung menjadi tak percaya, karena ada sesuatu dalam wajah perempuan itu yang terasa begitu familiar. Jantungnya berdetak lebih cepat, perasaannya terseret ke masa lalu, dan tanpa bisa menahannya ia berbisik, “Aurel…?” Perempuan itu menoleh cepat, dan saat mata mereka bertemu, waktu seolah berhenti bergerak, membuat suara hujan di luar terdengar seperti musik latar yang lembut. Aurel menatapnya dengan mata melebar, penuh kejutan dan sedikit ketidakpastian, lalu bibirnya perlahan menggambar senyum yang pernah hilang dari hidup Nara selama bertahun-tahun. Ia menyebut nama Nara dengan suara yang bergetar halus, seolah tak yakin apakah yang ia lihat ini nyata atau hanya bayangan yang dibentuk rindu, dan Nara berdiri dengan gerakan yang bahkan ia sendiri tidak sadari. Mereka saling mendekat, tenggelam dalam keheningan yang penuh cerita, dan Aurel berkata bahwa ia baru kembali ke kota itu setelah bertahun-tahun merantau, mencari sesuatu yang tidak pernah benar-benar ia temukan di tempat lain. Nara hampir tidak bisa berbicara karena pikirannya sibuk bergulir, memikirkan segala kemungkinan dan pertanyaan yang seharusnya ia ajukan, tetapi ia mulai dengan pertanyaan sederhana tentang kapan Aurel kembali, dan Aurel menjelaskan bahwa ia baru tiba pagi itu dan tanpa alasan yang jelas ia merasa harus mengunjungi toko buku Harmonia. Renga tersenyum sambil berpura-pura sibuk mengatur buku, karena ia tahu betul bahwa pertemuan itu adalah sesuatu yang selama ini Nara butuhkan, dan sesuatu yang mungkin akan mengubah hidup mereka. Aurel kemudian berkata bahwa ia selalu merindukan toko itu, dan juga merindukan seseorang yang selalu ada di sisinya ketika hujan turun, dan ucapan itu membuat udara di sekitar mereka terasa lebih hangat. Nara tertawa kecil, sebuah tawa yang sudah lama tak keluar, dan ia berkata bahwa ia tidak pernah berhenti berharap agar suatu hari Aurel kembali. Mereka duduk di sudut toko yang dulu menjadi tempat favorit mereka, dan percakapan pun mengalir seperti air hujan yang mengalir di atap, penuh cerita yang menumpuk selama satu dekade. Aurel menceritakan bagaimana ia pernah ingin kembali tetapi takut bahwa Lumina sudah berubah, atau lebih tepatnya, takut bahwa Nara sudah berubah, sementara Nara menjelaskan bagaimana ia selalu menunggu tetapi tidak pernah tahu apakah yang ia tunggu masih mungkin untuk kembali. Hujan di luar semakin deras tetapi ruangan terasa hangat karena percakapan yang tak pernah terasa cukup, dan mereka tertawa tentang hal-hal kecil yang dulu penting bagi mereka, seperti bagaimana Aurel selalu membenci sampul buku yang terlalu mencolok atau bagaimana Nara selalu salah menyebut nama tokoh utama. Setelah beberapa saat, Aurel menghentikan ceritanya dan menatap Nara dengan mata yang sedikit berkaca, lalu ia berkata bahwa ada alasan lain ia kembali ke kota itu, sesuatu yang lebih besar daripada sekadar nostalgia atau rasa rindu. Nara menunggu dengan napas tertahan, dan Aurel mengaku bahwa selama bertahun-tahun pergi, ia tidak pernah benar-benar menemukan tempat yang membuatnya merasa seperti rumah selain Lumina, dan tidak pernah menemukan rasa nyaman yang ia dapatkan ketika berada di dekat Nara. Kalimat itu membuat Nara terdiam lama, memaksa hatinya untuk mengakui sesuatu yang selama ini berusaha ia sembunyikan dari dirinya sendiri, dan akhirnya ia berkata bahwa ia juga tidak pernah berhenti menyimpan Aurel dalam pikirannya. Mereka saling tersenyum, senyum yang perlahan menghapus jarak sepuluh tahun, dan Aurel meletakkan tangannya di meja sambil menunggu, lalu Nara menyentuh tangan itu dengan ragu namun penuh tekad. Sentuhan itu sederhana, tetapi cukup untuk membuat keduanya tahu bahwa sesuatu telah berubah, atau mungkin belum pernah berubah sejak awal. Hujan mulai mereda, meninggalkan titik-titik air yang jatuh perlahan di atap, dan langit menampakkan sedikit warna keemasan yang muncul di balik awan. Aurel berkata bahwa hujan hari itu terasa berbeda, seperti hujan yang menandai awal baru, bukan akhir dari sesuatu, dan Nara mengatakan bahwa ia juga merasakannya. Mereka keluar dari toko bersama, dengan udara segar hujan menyambut mereka, dan Aurel memandangi jalanan basah sambil berkata bahwa kota itu masih sama seperti dulu, tetapi terlihat jauh lebih indah dari yang ia ingat. Nara menawarkan untuk mengantar Aurel pulang, dan Aurel menerima tawaran itu dengan senyum yang hangat, lalu mereka berjalan berdampingan menyusuri trotoar yang berkilau terkena pantulan cahaya lampu jalan. Di bawah payung biru tua yang sama yang Nara gunakan selama bertahun-tahun, mereka berjalan pelan sambil berbincang tentang masa depan, bukan hanya tentang masa lalu. Aurel bertanya apakah Nara masih suka duduk di tepi sungai saat hujan, dan Nara menjawab bahwa ia berhenti melakukannya sejak Aurel pergi, tetapi mungkin ia akan mulai lagi jika ditemani. Aurel menunduk sambil tersenyum, membiarkan suasana hening berbicara untuk mereka, dan Nara menyadari bahwa setiap langkah bersama Aurel terasa lebih ringan daripada langkah mana pun yang pernah ia lalui selama sepuluh tahun terakhir. Ketika mereka tiba di persimpangan, Aurel berhenti dan menatap Nara seolah ingin memastikan sesuatu, lalu ia bertanya apakah Nara bersedia bertemu lagi besok, dan lusa, dan mungkin setiap hari setelah itu. Nara menjawab tanpa ragu, karena untuk pertama kalinya dalam waktu yang sangat lama, ia merasa masa depan tidak lagi terasa menakutkan. Aurel tertawa kecil, lalu berkata bahwa mungkin hujan benar-benar membawa keberuntungan bagi mereka, bukan hanya kerinduan. Mereka berpisah dengan janji untuk bertemu lagi keesokan harinya, dan Nara menyaksikan Aurel berjalan pergi sambil membawa payung krem yang masih meneteskan air, sementara hatinya berdebar seperti dulu ketika mereka masih kecil. Saat Aurel menghilang di tikungan jalan, hujan sisa turun pelan-pelan seperti restu langit, dan Nara merasa bahwa hari itu adalah awal dari sesuatu yang baru. Ia berjalan pulang dengan langkah ringan, merasakan setiap tetes hujan di payungnya seperti musik yang menenangkan, dan ia tahu bahwa Lumina tidak pernah benar-benar kehilangan sinarnya—ia hanya menunggu. Di kamar malam itu, Nara menatap jendela yang masih basah dan mengulang kembali pertemuannya dengan Aurel dalam pikirannya, menyadari bahwa tidak ada hujan yang lebih indah daripada hujan yang mempertemukan dua hati yang belum selesai. Aurel pun di rumahnya menatap langit malam yang mulai cerah dan merasakan perasaan hangat yang lama hilang perlahan kembali, dan ia tahu bahwa keputusannya pulang adalah keputusan terbaik yang pernah ia buat. Kedua hati itu beristirahat malam itu dengan damai, membawa harapan yang tumbuh pelan-pelan seperti embun di pagi hari, dan ketika pagi tiba, Nara dan Aurel menantikan pertemuan baru yang akan membawa mereka lebih dekat. Dan sejak hari itu, hujan di Lumina tidak lagi menjadi kenangan yang menyakitkan bagi Nara, melainkan simbol dari awal yang manis bersama seseorang yang akhirnya kembali. Karena kadang hujan tidak datang untuk menghapus, tapi untuk menumbuhkan—dan itulah yang terjadi pada mereka."""
    )