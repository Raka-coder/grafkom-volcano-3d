# 🌋 3D Volcano Eruption Simulation (ModernGL)

Simulasi gunung berapi 3D yang realistis menggunakan Python dan library ModernGL. Project ini menggunakan teknik rendering modern seperti procedural terrain, particle systems, dan lighting berbasis shader.

## ✨ Fitur Utama
- **Procedural Terrain:** Gunung dan kawah dihasilkan menggunakan algoritma Perlin Noise.
- **Eruption System:** Simulasi partikel lava, asap, dan debris yang diproses di GPU.
- **Advanced Shaders:** Implementasi Blinn-Phong lighting, kabut (fog), dan skybox.
- **FPS Camera:** Navigasi bebas menggunakan mouse dan keyboard.
- **Texture Mapping:** Blending tekstur grass, rock, dan lava berdasarkan ketinggian.

## 📚 Library yang Digunakan
Project ini menggunakan beberapa library Python utama untuk grafika dan komputasi:
1. **ModernGL:** Wrapper OpenGL modern untuk manajemen buffer, shader, dan rendering pipeline.
2. **GLFW:** Library untuk pembuatan window, manajemen konteks OpenGL, dan input handling.
3. **NumPy:** Digunakan untuk komputasi matriks (view/projection) dan pemrosesan vertex data.
4. **Pillow (PIL):** Digunakan untuk memuat dan memproses aset tekstur gambar.
5. **Noise (Local):** Implementasi Perlin Noise lokal untuk generasi medan dan variasi partikel.

## 🛠️ Prasyarat
- **Python 3.10** atau versi yang lebih baru.
- Kartu grafis yang mendukung **OpenGL 3.3+**.

## 🚀 Panduan Instalasi

1. **Clone Repositori:**
   ```bash
   git clone https://github.com/username/uas-grafkom.git
   cd volcano-moderngl
   ```

2. **Buat Virtual Environment (Disarankan):**
   ```bash
   python -m venv venv
   # Aktifkan di Windows:
   venv\Scripts\activate
   # Aktifkan di Linux/macOS:
   source venv/bin/activate
   ```

3. **Instal Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Cara Menjalankan

Jalankan skrip utama menggunakan perintah berikut:
```bash
python main.py
```

### Kontrol Navigasi:
- **W, A, S, D:** Bergerak maju, kiri, mundur, dan kanan.
- **Mouse:** Mengarahkan pandangan (Look around).
- **ESC:** Keluar dari simulasi.

## 📂 Struktur Folder
- `core/`: Logika dasar window (GLFW) dan kamera FPS.
- `terrain/`: Generator heightmap dan pengelolaan mesh gunung.
- `particle/`: Sistem partikel untuk efek erupsi.
- `rendering/`: Pengelolaan shader dan proses rendering utama.
- `shaders/`: Source code GLSL (Vertex & Fragment shaders).
- `assets/`: Tekstur dan aset visual lainnya.

---
*Dibuat untuk Tugas UAS Grafika Komputer.*
