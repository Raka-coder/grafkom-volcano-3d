# Pembahasan Konsep Computer Graphics — Volcano Simulation

## 1. Transformasi Model (TRS Matrix)

**Lokasi:** `objects/base.py` — kelas `GameObject`

Setiap objek 3D memiliki matriks model sendiri yang menggabungkan **Translasi**, **Rotasi (Euler angles)**, dan **Skala** (TRS). Matriks ini dibangun manual di `_build_matrix()`:

- Translasi disimpan di kolom ke-3 (`m[0:3, 3] = pos`)
- Rotasi menggunakan sudut Euler sumbu X/Y/Z yang dikonversi ke matriks rotasi penuh
- Skala diterapkan dengan mengalikan baris 0-2 kolom 0-2 dengan faktor skala

Matriks TRS mengubah koordinat dari **Local Space → World Space**.

## 2. Sistem Koordinat & Ruang (Coordinate Spaces)

Seluruh pipeline transformasi mengikuti urutan:

```
Local Space  --[M_model]--> World Space  --[M_view]--> View Space
  --[M_proj]--> Clip Space  --[÷w]--> NDC  --[viewport]--> Screen Space
```

Di semua vertex shader: `gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0)`.

### Referensi:
- `shaders/terrain.vert:29` — terrain vertex ke clip space
- `shaders/object.vert:19` — object vertex ke clip space
- `shaders/particle.vert:14` — particle vertex ke clip space

## 3. Kamera & Proyeksi

**Lokasi:** `core/camera.py`

### View Matrix (LookAt)
Dibuat manual di `_look_at()` — menghitung basis orthogonal dari `front`, `right`, `up` vectors. Posisi kamera, yaw, dan pitch diupdate via input keyboard + mouse. Vektor `front` dihitung dari spherical coordinates.

### Perspective Projection
`get_projection_matrix()` membangun matriks frustum menggunakan FOV, aspect ratio, near/far plane.

### FPS Camera Control
- `process_keyboard()` — WASD dengan velocity × dt
- `process_mouse()` — delta mouse → yaw/pitch dengan sensitivity
- Pitch dibatasi ±89° agar tidak terjadi gimbal lock flip

## 4. Mesh Generation & Buffer Objects

**Lokasi:** `terrain/mesh.py`, `objects/base.py`

### VBO (Vertex Buffer Object)
Menyimpan array data vertex (posisi, normal, texcoord, warna) sebagai bytes di GPU.

### IBO/EBO (Index Buffer Object)
Menyimpan indeks segitiga untuk menghindari duplikasi vertex.

### VAO (Vertex Array Object)
Mengikat format data vertex ke shader attributes. Contoh:
- Terrain: `'3f 3f 2f'` → posisi(3) + normal(3) + texcoord(2)
- Objects: `'3f 3f 3f'` → posisi(3) + normal(3) + color(3)

### Indexed Rendering
`vao.render(mode=TRIANGLES)` — GPU melakukan reuse vertex via index buffer.

## 5. Shader Programming (GLSL)

**Lokasi:** `shaders/`, `rendering/shader.py`

### Vertex Shader
- `terrain.vert`, `object.vert`, `particle.vert`, `lava.vert`, `sky.vert`, `glow.vert`, `unlit.vert`, `shadow.vert`
- Bertanggung jawab atas transformasi vertex dan passing data (normal, UV, color) ke fragment shader

### Fragment Shader
- `terrain.frag`, `object.frag`, `particle.frag`, `lava.frag`, `sky.frag`, `glow.frag`, `unlit.frag`
- Bertanggung jawab atas per-pixel lighting, texturing, dan efek warna

### ShaderProgram (`rendering/shader.py`)
Membaca file `.vert`/`.frag`, compile via ModernGL, dan menyediakan `set_uniform()` untuk mengirim data ke GPU.

## 6. Blinn-Phong Lighting Model

**Lokasi:** `shaders/object.frag`, `shaders/terrain.frag`

### Komponen:
1. **Ambient** — iluminasi dasar `0.35 × sun_color` untuk area gelap
2. **Diffuse** — `max(dot(normal, light_dir), 0) × sun_color`
3. **Specular** — `pow(max(dot(normal, halfway), 0), shininess) × sun_color` dengan vektor halfway Blinn-Phong

### Multiple Light Sources:
- **Directional Light (Sun)** — dari arah `(0.6, 1.0, 0.4)` di kedua shader
- **Point Light (Lava Glow)** — posisi kawah `(0, 100, 0)` dengan atenuasi inverse-square di `terrain.frag:103-105`
- **Rim Lighting** — di `terrain.frag:117-123`, memberikan efek cahaya di tepi objek (fresnel-like)

### Normal Transformation
Di vertex shader: `Normal = mat3(transpose(inverse(M_model))) * in_normal` — menormalkan normal setelah transformasi non-uniform.

## 7. Shadow Mapping

**Lokasi:** `rendering/shadow.py`, `shaders/object.frag`, `shaders/terrain.frag`

### Implementation:
1. **Shadow Map Generation** — Render scene dari sudut pandang cahaya ke depth texture 2048×2048 (`render_shadow_map()`)
2. **Light Space Matrix** — `bias × proj × view` dari perspektif cahaya (`shadow.py:51-58`)
3. **Shadow Factor** — Di fragment shader, world position diproyeksikan ke light space, dibandingkan depth-nya dengan shadow map

### PCF (Percentage Closer Filtering)
`object.frag:27-34` dan `terrain.frag:39-47` — sampling 3×3 texel sekitar untuk anti-aliasing bayangan.

### Bias
`max(0.002, 0.002 × (1 - dot(normal, light_dir)))` untuk mencegah shadow acne.

## 8. Particle System

**Lokasi:** `particle/system.py`, `particle/emitter.py`, `shaders/particle.*`

### GPU-Friendly Design
Partikel disimpan sebagai array struct CPU, lalu di-flush ke dynamic VBO setiap frame — single draw call untuk semua partikel.

### Physics per Partikel:
| Tipe | Gaya | Perilaku |
|------|------|----------|
| **Lava** | Gravity (−15 m/s²), drag 0.98 | Bounce + splash saat collision dengan crater |
| **Smoke** | Buoyancy (+28 m/s²), wind drift, curl noise | Scale membesar 8× seiring waktu |
| **Ash** | Gravity ringan, wind drift | Scale mengecil |
| **Debris** | Gravity penuh, drag | Bounce minimal |
| **Embers** | Gravity ringan, spread horizontal | Scale kecil, glow |
| **Mist** | Curl noise horizontal | Scale membesar 1.5×, life sangat panjang |

### Particle Rendering (Point Sprites)
Vertex shader `particle.vert` mengatur `gl_PointSize` berdasarkan jarak (scale/dist). Fragment shader menggunakan `gl_PointCoord` untuk menggambar bentuk gas cloud dengan warp sinusoidal.

### Dynamic Emission
`VolcanoEmitter.get_eruption_intensity()` — kombinasi sine wave multi-frekuensi mensimulasikan siklus erupsi natural.

## 9. Blending & Transparency

**Lokasi:** `core/window.py:38-39`, `rendering/renderer.py`

### Alpha Blending
`SRC_ALPHA, ONE_MINUS_SRC_ALPHA` — untuk particle system dan objek transparan.

### Additive Blending
`SRC_ALPHA, ONE` — untuk lava dan glow decals agar tampak bercahaya (emissive).

### Depth Test
Dinyalakan untuk semua objek padat, dimatikan untuk sky dome.

### Face Culling
Dinyalakan (CCW = front face) untuk semua geometry, dimatikan saat render sky.

## 10. Texturing

**Lokasi:** `main.py:24-119`, `shaders/terrain.frag`

### Procedural Texture Generation
Tiga tekstur 512×512 dibuat di `create_procedural_textures()` menggunakan **FBM (Fractional Brownian Motion)**:
1. **Grass** — hijau gelap/terang, 7 octaves
2. **Rock** — abu-abu variatif, 8 octaves
3. **Lava** — merah/oranye dengan crack pattern via noise thresholding

### Multi-Texturing Terrain
Di `terrain.frag:51-85`, terrain di-mix berdasarkan:
- **Ketinggian** — grass (low) → rock (mid) → lava (high)
- **Slope** — lereng curam diganti rock
- **Ash layer** — overlay abu di sekitar kawah yang pudar menjauh

### Mipmapping
`texture.build_mipmaps()` + `LINEAR_MIPMAP_LINEAR` filtering untuk减少 aliasing jarak jauh.

## 11. Terrain Generation

**Lokasi:** `terrain/generator.py`

### Perlin Noise
Implementasi pure-Python di `noise.py` berdasarkan algoritma Ken Perlin:
- Permutation table 256
- Gradient vectors, fade function (6t⁵ - 15t⁴ + 10t³)
- 3D noise dengan trilinear interpolation

### FBM (Fractional Brownian Motion)
Multiple octaves noise dengan persistence ×0.5 dan lacunarity ×2:
- **Terrain base** — 4 octaves × 22 amplitude
- **Peak variation** — 3 octaves × 14 amplitude
- **Texture generation** — 6-8 octaves

### Volcano Shape
`terrain/generator.py:51` — `(1 - t²)²` memberikan bentuk kerucut landai. Crater dibuat dengan mengurangi ketinggian di area pusat (`(crater_radius - dist) × 2.5`).

### Normal Calculation
Central differences: `dx = (h(i+1) - h(i-1)) / 2scale` untuk mendapatkan gradien, lalu `normal = normalize(-dx, 1, -dz)`.

## 12. Procedural 3D Modeling

### Pine Tree (`objects/tree.py`)
- **Trunk** — tabung 10-segment dengan slight random bend dan variasi radius per segment
- **Crown** — 4 layer cone dengan radius mengecil ke atas, warna hijau bervariasi
- Setiap tree unik via random seed

### Rock (`objects/rock.py`)
- UV sphere dideformasi dengan hash-based jitter pada radius tiap vertex
- Warna abu-abu dengan variasi warm/cool tone

### Grass Patch (`objects/grass.py`)
- Cross-shaped billboard (2 quad tegak lurus)
- Warna hijau gradasi dari dark ke light

### Fumarole (`objects/fumarole.py`)
- Ring geometry dengan inner (kuning) dan outer (abu) ring
- Steam emitter memancar ke atas

### Lava Flow (`objects/lava_flow.py`)
- Path dihasilkan dari spiral/archimedean curve
- Mesh dibangun sebagai ribbon dengan width bervariasi (melebar ke bawah)
- UV mapping: x=0..1 (cross-section), y=0..1 (panjang aliran)

## 13. Lava Procedural Shader

**Lokasi:** `shaders/lava.frag`

Efek lava dihasilkan sepenuhnya di fragment shader tanpa tekstur:
- **Edge glow** — `pow(1 - dist_from_center, 1.8)` untuk tepi terang
- **Flow pattern** — kombinasi sine wave yang bergerak seiring waktu (`sin(flow × 2) + sin(flow × 3.7)`)
- **Vein/crack** — `sin(texcoord.x × 12 + flow × 1.5)` dipow(4) untuk garis-garis terang
- **Pulse** — denyut ganda dengan frekuensi berbeda (2.0 dan 1.3 Hz)
- **Color grading** — hot_core (kuning) → mid (oranye) → edge (merah gelap)

## 14. Sky & Atmospheric Effects

### Sky Dome (`shaders/sky.frag`)
Sky plane raksasa 4000×4000 yang mengikuti kamera horizontal (`sky.vert:14-16`). Warna gradasi:
- Horizon (biru muda) → mid (biru cerah) → upper (biru) → zenith (biru tua)
- Sun disc — smoothstep circle dengan glow di posisi `(0.3, 0.15)` UV space

### Fog (`shaders/terrain.frag:125-129`)
Exponential fog: `exp(-(dist × density)²)` untuk transisi halus ke fog_color.

### Glow Decals (`shaders/glow.frag`)
Circle radial gradient dengan pulse sin(time × 2) untuk efek lava glow di kawah.

### Volcanic Lightning (`effects/lightning.py`)
- Bolt dihasilkan dari midpoint displacement dengan jitter maksimum di tengah
- Core (putih terang) + glow (biru/ungu) sebagai garis paralel
- Branching — 40% probabilitas cabang
- Life pendek 0.1-0.25 detik dengan alpha fade

## 15. Collision Detection

**Lokasi:** `core/camera.py:55-60`, `particle/system.py:84-107`

### Camera-Terrain
Ketinggian kamera dicek terhadap `terrain_gen.get_height_at()`. Kamera tidak bisa turun di bawah `terrain_height + 5.0`.

### Particle-Crater
Lava particles mendeteksi tabrakan dengan crater floor (y < 102 dan dist < 20):
- Bounce dengan energi 40%
- Splatter effect ke samping
- Life extension saat splash

## 16. Animation & Time-Based Effects

### Delta Time
`main.py:287` — `dt = current_time - last_time` memastikan animasi konsisten terlepas dari frame rate.

### Pulsing
- Lava texture UV scrolling: `texcoord + time × 0.03`
- Lava glow: `sin(time × 2.5)` dan `sin(time × 6.3)`
- Eruption intensity: `sin(time × 0.3)` dan `sin(time × 1.2)`

### Color Interpolation
Partikel: `color_start × (1-t) + color_end × t` dengan alpha falloff di 70% lifecycle.

## 17. Dynamic Point Size

**Lokasi:** `shaders/particle.vert:17-22`

Ukuran partikel dihitung per-vertex: `gl_PointSize = (in_scale / dist) × 100`, di-clamp ke range 6-100. Partikel jauh mengecil secara natural.

## 18. Shadow Map Pipeline

**Lokasi:** `rendering/shadow.py`

1. `compute_light_matrix()` — membangun view-projection dari perspektif cahaya
2. `render()` — render ke framebuffer offscreen dengan depth attachment
3. `light_matrix = bias × proj × view` — matrix yang memetakan world → shadow UV (+ bias 0.5 untuk remap [-1,1] ke [0,1])

## 19. Ambient Occlusion (AO)

**Lokasi:** `shaders/terrain.frag:96-97`

AO sederhana berdasarkan ketinggian dan slope:
- `mix(0.4, 1.0, smoothstep(-20, 30, h))` — lembah lebih gelap
- `mix(0.6, 1.0, smoothstep(0.3, 0.8, 1-slope))` — lereng curam lebih gelap

## 20. Light Attenuation

**Lokasi:** `effects/lighting.py:45-58`, `shaders/terrain.frag:103-105`

Inverse-square law: `1 / (1 + 0.005d + 0.0002d²)` dengan smooth falloff. Lava flicker: kombinasi sine wave 2.5 Hz dan 5.0 Hz.

## 21. Double Buffering

**Lokasi:** `core/window.py:81-82`

`glfw.swap_buffers()` — menukar front buffer (display) dengan back buffer (render) untuk mencegah screen tearing.

## 22. Depth Test & Face Culling

**Lokasi:** `core/window.py:38`

- `DEPTH_TEST` — Z-buffer memastikan objek depan menutupi belakang
- `CULL_FACE` — menghilangkan render back-face (CCW = front) untuk efisiensi
- `PROGRAM_POINT_SIZE` — diaktifkan di `main.py:131` agar shader bisa kontrol `gl_PointSize`

## 23. GPU Data Flow

### Uniforms
Data dikirim per-frame via `ShaderProgram.set_uniform()`:
- Matriks (proj, view, model) — dikirim sebagai bytes `(4×4 .T.tobytes())`
- Float (time, intensity) — langsung via `.value`
- Textures — di绑定 ke texture unit (0,1,2,4)

### Vertex Attributes
Format string seperti `'3f 3f 2f'` mendefinisikan layout buffer → shader input.

### Dynamic Buffers
Particle VBO dibuat dengan `dynamic=True` dan ditulis ulang setiap frame via `.write()`.

## 24. Curl Noise for Fluid Motion

**Lokasi:** `particle/system.py:56-58, 72-74`

Simulasi turbulensi angin tanpa texture noise:
- Smoke: `vel.x += -sin(pos.z × freq + t × 1.5) × curl × dt`
- Mist: `vel.x += -sin(pos.z × freq + t × 0.6) × curl × dt`
Memberikan gerakan swirling natural pada asap dan kabut.
