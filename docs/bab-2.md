# BAB II TAHAPAN PENGEMBANGAN

## 2.1 Metodologi Pengembangan
Metode yang digunakan dalam pengembangan project ini adalah metode **Incremental Development**. Metode ini dipilih karena memungkinkan pengembangan dilakukan secara bertahap, mulai dari pembuatan kerangka dasar hingga implementasi sistem visual yang kompleks. Tahapan tersebut meliputi:
1.  **Inisialisasi Core:** Pembuatan windowing system dan kontrol kamera FPS.
2.  **Generasi Medan (Terrain):** Implementasi algoritma noise untuk membentuk gunung berapi.
3.  **Sistem Material & Shader:** Pembuatan shader untuk pencahayaan dan blending tekstur.
4.  **Sistem Partikel:** Implementasi simulasi erupsi (lava dan asap).
5.  **Optimasi & Finishing:** Integrasi efek kabut (fog) dan pengaturan performa.

## 2.2 Analisis Kebutuhan
Kebutuhan dalam sistem ini dibagi menjadi dua, yaitu:

### 2.2.1 Kebutuhan Fungsional
- Sistem dapat menghasilkan medan gunung berapi secara otomatis menggunakan algoritma prosedural.
- Sistem dapat mensimulasikan partikel erupsi (lava, asap, dan serpihan) dengan gravitasi.
- Sistem menyediakan kontrol kamera FPS (First Person Shooter) untuk navigasi bebas di lingkungan 3D.
- Sistem mengimplementasikan sistem pencahayaan dinamis (Blinn-Phong) dan efek atmosferik (kabut).

### 2.2.2 Kebutuhan Non-Fungsional
- **Real-time Performance:** Sistem harus berjalan mulus dengan frame rate minimal 30-60 FPS.
- **Library Modern:** Menggunakan ModernGL untuk akses API OpenGL yang lebih efisien di Python.
- **Respon Cepat:** Input handling (keyboard & mouse) harus memiliki latensi rendah.

## 2.3 Perancangan Sistem
Perancangan sistem meliputi arsitektur modul dan alur kerja aplikasi:
- **Arsitektur Program:**
    - `core/`: Modul pengelola jendela (GLFW) dan sistem kamera.
    - `terrain/`: Modul generator heightmap dan pengelola mesh gunung.
    - `particle/`: Modul sistem partikel dan emitter erupsi.
    - `rendering/`: Modul pengelola pipeline shader dan proses rendering.
- **Flow Program:** Dimulai dari inisialisasi resource, pembuatan tekstur prosedural, kompilasi shader, generasi mesh, lalu masuk ke *Main Loop* yang menangani update logika dan rendering frame secara bergantian.

## 2.4 Perancangan Objek 3D
### 2.4.1 Objek Prosedural yang Digunakan
Objek 3D dalam project ini tidak menggunakan model eksternal, melainkan dibangun secara kode:
- **Mountain Terrain:** Dibangun dari grid vertex yang ketinggiannya dimanipulasi menggunakan *Perlin Noise* untuk membentuk lereng dan kawah.
- **Eruption Particles:** Objek titik (Points) yang diberikan ukuran melalui shader untuk mewakili lava dan debu vulkanik.
- **Sky Background:** Bidang luas atau representasi atmosfer menggunakan warna gradien dan efek kabut.

### 2.4.2 Teknik Transformasi & Rendering
- **Transformasi:** Menggunakan matriks Model, View, dan Projection (MVP) untuk menghitung posisi objek di ruang 3D.
- **Vertex Buffer Object (VBO):** Mengirimkan data koordinat dan normal gunung secara efisien ke GPU.
- **Texture Blending:** Mencampur tekstur rumput (grass), batuan (rock), dan lava berdasarkan ketinggian vertex.

## 2.5 Perancangan Animasi Erupsi
Animasi dalam sistem ini bersifat dinamis (physics-based):
- **Emitter Logic:** Menghasilkan partikel baru secara berkala di pusat kawah.
- **Particle Physics:** Setiap partikel memiliki vektor kecepatan, massa, dan dipengaruhi oleh gaya gravitasi serta hambatan udara.
- **Life Cycle:** Partikel akan mengecil atau memudar (fade out) seiring berjalannya waktu (lifetime).

## 2.6 Implementasi dengan ModernGL & Python
Berbeda dengan OpenGL tradisional, implementasi ini menggunakan pendekatan modern:
- **Shader-Centric:** Semua rendering logika (pencahayaan, pewarnaan) dilakukan di GLSL (Vertex & Fragment Shader).
- **Buffer Management:** Menggunakan objek `ctx.buffer` dari ModernGL untuk manajemen memori GPU.
- **Uniform Handling:** Komunikasi data kamera dan cahaya ke GPU melalui variabel uniform.

## 2.7 Pengujian Sistem
Pengujian dilakukan melalui beberapa skenario:
- **Uji Visual:** Memastikan transisi tekstur dan efek kabut terlihat natural.
- **Uji Navigasi:** Memastikan kamera tidak menembus tanah (collision detection) dan bergerak lancar.
- **Uji Stabilitas:** Menjalankan simulasi dengan ribuan partikel untuk memantau penggunaan memori dan CPU/GPU.

## 2.8 Perangkat dan Tools
- **Bahasa Pemrograman:** Python 3.12
- **Library Utama:** ModernGL (Rendering), GLFW (Windowing), NumPy (Math), Pillow (Aset).
- **Shader Language:** GLSL (OpenGL Shading Language)
- **Sistem Operasi:** Windows 10/11