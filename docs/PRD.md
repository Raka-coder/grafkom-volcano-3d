# 📘 PRODUCT REQUIREMENT DOCUMENT (PRD)

## 1. 📌 Judul
Realistic 3D Volcano Eruption Simulation menggunakan ModernGL (Python)

---

## 2. 🎯 Tujuan
Membangun simulasi gunung berapi 3D dengan visual realistis menggunakan pipeline grafika modern (shader-based rendering) berbasis Python.

---

## 3. 🧠 Konsep Utama Grafika
- Procedural Terrain (Perlin Noise)
- Physically-based Lighting (Phong/Blinn-Phong)
- Particle System (GPU-friendly)
- Camera FPS (free exploration)
- Fog (atmospheric scattering sederhana)
- Texture Mapping
- Normal Calculation (smooth shading)

---

## 4. 🧱 Scope

### ✅ Termasuk:
- Terrain realistis (noise-based)
- Kawah (crater deformation)
- Lava eruption (particle system)
- Dynamic lighting (lava glow + sun)
- Fog effect
- Texture terrain

### ❌ Tidak termasuk:
- PBR (Physically Based Rendering full)
- Vulkan / ray tracing
- AI simulation

---

## 5. ⚙️ Functional Requirements

### 5.1 Terrain System
- Grid ≥ 200x200
- Height = kombinasi:
  - cone function
  - Perlin noise
- Smooth normal interpolation
- Crater di puncak

---

### 5.2 Rendering Pipeline
- Menggunakan ModernGL context
- Vertex Buffer Object (VBO)
- Vertex Array Object (VAO)
- Shader terpisah (GLSL)

---

### 5.3 Lighting System
- Blinn-Phong shading
- 2 light sources:
  - Directional (matahari)
  - Point light (lava)
- Specular highlight

---

### 5.4 Particle System
Jenis:
- Lava
- Smoke
- Debris

Fitur:
- Spawn dari kawah
- Velocity + gravity
- Color interpolation (merah → gelap)
- Alpha blending

---

### 5.5 Camera System
- FPS camera
- WASD movement
- Mouse look
- Projection matrix (perspective)

---

### 5.6 Fog System
- Exponential fog
- Berdasarkan jarak kamera

---

### 5.7 Texture Mapping
- Terrain:
  - grass
  - rock
  - lava
- Blend berdasarkan ketinggian

---

## 6. ⚙️ Non-Functional Requirements

- 100% Python
- Modular architecture
- Minimal 30 FPS (target 60 FPS)
- Cross-platform

---

## 7. 📦 Teknologi

- Python 3.10+
- ModernGL
- glfw
- numpy
- noise (Perlin)
- pillow (texture)

---

## 8. 📁 Struktur Project

volcano-moderngl/
│
├── main.py
├── requirements.txt
│
├── core/
│   ├── window.py
│   ├── camera.py
│
├── terrain/
│   ├── generator.py
│   ├── mesh.py
│
├── particle/
│   ├── system.py
│   ├── emitter.py
│
├── rendering/
│   ├── shader.py
│   ├── renderer.py
│
├── effects/
│   ├── fog.py
│   ├── lighting.py
│
├── shaders/
│   ├── terrain.vert
│   ├── terrain.frag
│   ├── particle.vert
│   ├── particle.frag
│
├── assets/
│   ├── textures/

---

## 9. 🎮 Use Case

### UC-01: Explore Scene
User menjelajah gunung dengan kamera FPS

### UC-02: Observe Eruption
User melihat partikel lava keluar

### UC-03: Dynamic Lighting
User melihat efek cahaya lava berubah

---

## 10. 🎯 Output

- Gunung realistis (smooth)
- Erupsi dinamis
- Lighting natural
- Fog depth effect

---

## 11. 📊 KPI

| Metric | Target |
|--------|--------|
| FPS | ≥ 30 |
| Particle Count | ≥ 300 |
| Grid Resolution | ≥ 200x200 |

---

## 12. ⚠️ Risiko

| Risiko | Solusi |
|--------|--------|
| FPS drop | batching / limit particle |
| shader error | logging |
| memory tinggi | optimize mesh |

---

## 13. 🚀 Future Work
- Shadow mapping
- HDR rendering
- Sound effect
- UI debug (ImGui)