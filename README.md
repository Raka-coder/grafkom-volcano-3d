# 🌋 3D Volcano Eruption Simulation (ModernGL)

Simulasi gunung berapi 3D yang realistis menggunakan Python dan library ModernGL. Project ini menggunakan teknik rendering modern seperti procedural terrain, particle systems, dan lighting berbasis shader.

## ✨ Fitur Utama

- **Procedural Terrain:** Gunung dan kawah dihasilkan menggunakan algoritma Perlin Noise 3D dengan multiple cone-shaped mountains.
- **Eruption System:** Simulasi partikel advanced dengan 4 jenis partikel (Lava, Smoke, Ash, Debris) dengan realistic physics.
- **Advanced Shaders:**
  - Blinn-Phong lighting dengan dual light sources (Sun + Lava glow)
  - Rim lighting untuk efek dramatik
  - Dynamic flickering dari lava light (non-repetitive pattern)
  - Sky gradient dengan cloud animation dan sun disk
- **Texture Blending:** Multi-layer FBM textures untuk grass, rock, dan lava dengan height-based dan slope-based blending.
- **Particle Physics:**
  - Gravity dan air resistance untuk realistic motion
  - Collision detection dengan crater
  - Splashing dan bounce effects
  - Buoyancy untuk smoke rising
  - Turbulent swirl motion
- **FPS Camera:** Navigasi bebas dengan mouse dan keyboard, free-look system.
- **Dynamic Fog:** Exponential fog untuk atmospheric depth.
- **High Quality Visuals:** 512×512 procedural textures, smooth normal calculations, realistic material appearance.

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
- `docs/`: Dokumentasi lengkap untuk laporan:
  - `implementation_details.md` - Technical details lengkap semua sistem
  - `feature_summary.md` - Ringkasan fitur dengan formula dan konstanta
  - `visual_description.md` - Deskripsi visual hasil implementasi
  - `implementation_plan.md` - Rencana implementasi awal

## 📖 Dokumentasi untuk Laporan

Untuk penulisan laporan, silakan merujuk ke dokumentasi berikut:

### Bagian 3.1: Implementasi Lingkungan dan Medan

- File: [`docs/visual_description.md`](docs/visual_description.md) - Sektion "Aspek Visual Medan & Tekstur"
- File: [`docs/implementation_details.md`](docs/implementation_details.md) - Sektion "Implementasi Lingkungan dan Medan 3D"
- Topik: Procedural generation, texture blending, FBM implementation

### Bagian 3.2: Implementasi Sistem Partikel Erupsi

- File: [`docs/feature_summary.md`](docs/feature_summary.md) - Sektion "Implementasi Sistem Partikel Erupsi"
- File: [`docs/visual_description.md`](docs/visual_description.md) - Sektion "Aspek Visual Sistem Partikel"
- File: [`docs/implementation_details.md`](docs/implementation_details.md) - Sektion "Implementasi Sistem Partikel Erupsi"
- Topik: Physics simulation, particle types, dynamic eruption

### Bagian 3.3: Implementasi Pencahayaan dan Efek Atmosfer

- File: [`docs/feature_summary.md`](docs/feature_summary.md) - Sektion "Implementasi Pencahayaan & Efek Atmosfer"
- File: [`docs/visual_description.md`](docs/visual_description.md) - Sektion "Aspek Visual Pencahayaan & Atmosfer"
- File: [`docs/implementation_details.md`](docs/implementation_details.md) - Sektion "Implementasi Pencahayaan dan Efek Atmosfer"
- Topik: Blinn-Phong, light flickering, sky rendering, fog

---

_Dibuat untuk Tugas UAS Grafika Komputer._
