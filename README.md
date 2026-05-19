# 3D Volcano Eruption Simulation (ModernGL)

Simulasi gunung berapi 3D realistis menggunakan Python dan ModernGL (OpenGL 3.3+). Menampilkan procedural terrain, multi-partikel erupsi, dynamic lighting, shadow mapping, dan efek atmosferik vulkanik.

## Fitur

### Terrain & Medan
- **400×400 heightmap grid** (~160K vertex, ~318K segitiga) dari Perlin Noise 3D
- Multiple cone-shaped mountains dengan crater depression
- Multi-layer texture splatting: Grass, Rock, Lava (height-based + slope-based)
- FBM (Fractional Brownian Motion) procedural textures 512×512 (7-8 octaves)
- Ash deposition layer dinamis (intensitas 0.3-0.55, radius 55)
- Rim lighting di tepi kawah dengan pulsa sinusoidal

### Sistem Partikel Erupsi
- **20.000 max particles** — single GL_POINTS draw call
- 5 jenis partikel: Lava (15%), Smoke (45%), Ash (20%), Debris (10%), Embers (15%)
- Dynamic emission rate: 500 partikel/detik × intensitas erupsi
- Intensitas erupsi: produk 2 gelombang sinus — pola natural tidak seragam
- Fisika: Gravity (−15 m/s²), air resistance, bounce (35% energi), splash, buoyancy (+28 m/s² asap)
- Smoke curl turbulence, wind drift oscillasi horizontal
- 14 fumarole vents (steam), mist/low cloud ring

### Pencahayaan
- **Blinn-Phong** dengan dual light sources: Sun (directional) + Lava Glow (point)
- Dynamic lava light flickering: kombinasi sine waves non-repetitif
- PCF Soft Shadows 2048×2048 dengan kernel 3×3
- Ambient occlusion berdasarkan ketinggian
- Exponential fog

### Efek Atmosfer
- Sky gradient 4 lapis + sun disk dengan glow halo
- Volcanic lightning: random interval 0.5-3 detik, branch probability 40%
- 3 aliran lava procedural dari kawah (flow animation + pulse)
- Ground glow decals di crater

### Kamera & Kontrol
- FPS camera: WASD + mouse look
- Collision detection dengan terrain
- R: reset ke spawn
- F: fullscreen toggle
- ESC: keluar

### 8 Shader Programs
| Shader | Fungsi |
|--------|--------|
| Terrain | Texture splatting, Blinn-Phong, PCF shadow, rim light, ash, fog |
| Object | Blinn-Phong + PCF shadow, vertex color (pohon, fumarol) |
| Particle | Point sprite, distance-based size, radial alpha |
| Lava | Procedural flow, pulse, vein patterns |
| Sky | Multi-layer gradient + sun disk |
| Shadow | Depth-only pass 2048×2048 |
| Unlit | Flat color + alpha (lightning bolts) |
| Glow | Radial gradient glow decals |

## Prasyarat

- Python 3.10+
- OpenGL 3.3+ GPU

## Instalasi

```bash
git clone https://github.com/username/uas-grafkom.git
cd volcano-moderngl
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python main.py
```

## Kontrol

| Tombol | Aksi |
|--------|------|
| W/A/S/D | Bergerak maju/kiri/mundur/kanan |
| Mouse | Look around |
| R | Reset kamera ke spawn |
| F | Fullscreen toggle |
| ESC | Keluar |

## Struktur Proyek

```
volcano-moderngl/
├── main.py                 # Entrypoint — pipeline inisialisasi & main loop
├── requirements.txt        # Dependensi Python
├── noise.py                # Implementasi Perlin Noise lokal (override PyPI noise)
│
├── core/
│   ├── window.py           # GLFW window, input, fullscreen
│   └── camera.py           # FPS camera, view/projection matrix
│
├── terrain/
│   ├── generator.py        # Perlin noise heightmap + volcano shape
│   └── mesh.py             # Terrain mesh (VBO/IBO/VAO)
│
├── rendering/
│   ├── renderer.py         # Orchestrator rendering: 8 shader programs, shadow pass
│   ├── shader.py           # ShaderProgram loader + uniform setter
│   └── shadow.py           # Shadow map 2048×2048 + light matrix
│
├── particle/
│   ├── system.py           # GPU particle system (dynamic VBO, physics update)
│   └── emitter.py          # Volcano emitter (5 particle types, eruption cycle)
│
├── effects/
│   ├── lighting.py         # Sun + lava glow + fog config
│   └── lightning.py        # Volcanic lightning (procedural bolts + branches)
│
├── objects/
│   ├── base.py             # GameObject base (model matrix, Euler rotation)
│   ├── tree.py             # PineTree procedural (trunk + 4 cone layers)
│   ├── lava_flow.py        # LavaFlow procedural strip with terrain follow
│   ├── ground_glow.py      # GroundGlow radial decal
│   ├── fumarole.py         # Fumarole vent + steam emitter
│   └── mist.py             # MistEmitter ring around volcano
│
├── shaders/                # 16 file GLSL (8 vertex + 8 fragment)
│   ├── terrain.vert/frag   # Main terrain shader
│   ├── particle.vert/frag  # Point sprite particles
│   ├── sky.vert/frag       # Sky dome gradient
│   ├── object.vert/frag    # 3D objects (trees, fumaroles)
│   ├── lava.vert/frag      # Lava flow decal
│   ├── shadow.vert/frag    # Shadow map depth pass
│   ├── unlit.vert/frag     # Lightning bolts
│   └── glow.vert/frag      # Ground glow decals
│
└── assets/textures/        # Procedural textures (auto-generated, .gitignore)
    ├── grass.png           # 512×512 FBM grass
    ├── rock.png            # 512×512 FBM rock
    └── lava.png            # 512×512 FBM lava + crack pattern
```

## Parameter Kunci

| Parameter | Nilai |
|-----------|-------|
| Grid terrain | 400×400 |
| World bounds | −200 s/d +200 |
| Puncak gunung | ~105 unit |
| Kawah | radius 18, depth ~20 unit |
| Shadow map | 2048×2048 |
| Max partikel | 20.000 |
| FOV | 45° |
| Near/far plane | 0.1 / 1000 |
| Pohon | ~50 PineTree procedural |
| Aliran lava | 3 strip, radius 20→90 |
| Fumarol | 14 vents |
| Mist | ring 25→90, height 25-60 |

## Dependensi

- ModernGL
- glfw
- numpy
- Pillow
- noise (PyPI — tetapi efektif tidak digunakan; local `noise.py` yang aktif)

---

_Dibuat untuk Tugas UAS Grafika Komputer._
