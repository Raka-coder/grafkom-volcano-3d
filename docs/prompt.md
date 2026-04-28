Buatkan project Python menggunakan ModernGL untuk simulasi gunung berapi 3D dengan spesifikasi berikut:

## 1. Rendering
- Gunakan ModernGL sebagai rendering engine
- Setup context menggunakan GLFW
- Gunakan VAO, VBO, shader pipeline

---

## 2. Terrain
- Generate terrain grid minimal 200x200
- Gunakan Perlin noise (library noise)
- Kombinasikan dengan fungsi cone untuk bentuk gunung
- Buat crater di puncak
- Hitung normal vector per vertex

---

## 3. Shader
Buat shader terpisah:
- terrain.vert
- terrain.frag

Fitur shader:
- Blinn-Phong lighting
- Support:
  - model, view, projection
  - normal
  - light position
  - camera position

---

## 4. Lighting
- Directional light (sun)
- Point light (lava glow)
- Specular highlight
- Dynamic intensity (flicker)

---

## 5. Particle System
Implementasi particle system untuk:
- lava
- smoke
- debris

Fitur:
- spawn dari crater
- physics sederhana:
  - gravity
  - velocity
- warna berubah seiring waktu
- alpha blending aktif

---

## 6. Camera
- FPS camera
- WASD movement
- Mouse look (yaw, pitch)
- Perspective projection

---

## 7. Fog
- Exponential fog
- Berdasarkan jarak kamera

---

## 8. Texture
- Load texture menggunakan pillow
- Apply ke terrain
- Blend berdasarkan height

---

## 9. Struktur
Pisahkan module:
- camera
- terrain
- particle
- shader
- renderer

---

## 10. Output
- Program bisa dijalankan langsung
- Tidak menggunakan model eksternal
- Minimal 300 partikel aktif
- Terrain terlihat smooth dan realistis

---

## 11. Tambahkan:
- komentar kode (penjelasan grafika)
- error handling shader
- struktur clean dan readable

tambahkan komentar pada function