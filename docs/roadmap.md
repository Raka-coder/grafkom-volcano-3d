# Development Roadmap — volcano-moderngl

Dokumentasi lengkap seluruh fase pengembangan, dari perencanaan hingga implementasi.

---

## Fase 1 — Pohon Procedural ✅ Selesai

### Tujuan
Menambahkan vegetasi ke scene vulkan agar lingkungan tidak terlihat kosong.

### File

| File | Isi |
|------|-----|
| `objects/base.py` | `GameObject` — base class dengan TRS matrix |
| `objects/tree.py` | `PineTree` — pohon pinus procedural |
| `shaders/object.vert` | Generic vertex shader dengan `m_model` |
| `shaders/object.frag` | Blinn-Phong (ambient 35% + diffuse 65% + spec 15%) |

### GameObject Base Class (`objects/base.py`)

Setiap objek 3D diturunkan dari `GameObject`:

```python
class GameObject:
    def __init__(self, ctx, program, vertices, indices)
    def set_position(x, y, z)
    def set_rotation(x_deg, y_deg, z_deg)  # Euler Z-X-Y
    def set_rotation_y(deg)
    def set_scale(s)
    def render()
```

**TRS Matrix:** Semua transform disimpan sebagai parameter, lalu `_build_matrix()` membangun matrix penuh `Ry * Rx * Rz` setiap kali ada perubahan — tidak ada mutasi incremental.

### PineTree (`objects/tree.py`)

Pohon pinus procedural dengan 4 layer crown + batang melengkung:

```
     /\
    /__\    <- layer 4 (tip)
   /    \
  /______\  <- layer 3
   |    |
  /______\  <- layer 2
   |    |
  /______\  <- layer 1
   |    |
  |______|  <- trunk
```

| Parameter | Default | Range |
|-----------|---------|-------|
| `height` | 10.0 | 5.0 – 16.0 |
| `segments` | 10 | — |
| `seed` | 0 | — |

**Detail per seed:**
- Trunk 30-40% dari total height
- Radius trunk `0.030-0.045 × height`
- Batang melengkung random (`bend_x/z = ±0.15`)
- 4 layer crown dengan radius & tinggi random tiap layer
- Vertex trunk tidak bulat sempurna (±15% per vertex)

**Warna:**
- Batang: `(0.32, 0.18, 0.07)` — coklat
- Daun: gradien `(0.06, 0.25, 0.05)` → `(0.18, 0.55, 0.13)` — hijau

### Winding Order

Semua mesh harus CCW (front-facing) agar tidak di-cull `CULL_FACE`:

```python
# ✅ Tree (CCW):
idxs.extend([b, b+2, b+1,  b+2, b+3, b+1])
```

### Placement Logic

```python
for i in range(60):                     # 60 titik random
    try_place_tree(random_pos)
for (wx, wz) in tree_positions[:20]:     # cluster: 1-3 tetangga
    try_place_tree(wx + jitter, wz + jitter)
```

| Kriteria | Nilai |
|----------|-------|
| Elevasi | 2–40 m |
| Kemiringan | steep < 2.0 |
| Jarak kawah | > 20 m |
| Sink (Y) | `h - 0.4` (tertanam) |
| Rotasi X | ±3° (tilt) |
| Rotasi Y | 0-360° |
| Max pohon | ~50 |

---

## Fase 2 — Lava Flow ✅ Selesai

### Tujuan
Menambahkan aliran lava dari kawah ke lereng gunung.

### File

| File | Isi |
|------|-----|
| `objects/lava_flow.py` | `LavaFlow` — ribbon mesh dari path |
| `shaders/lava.vert` | Vertex shader dengan UV |
| `shaders/lava.frag` | Emissive lava + flow animation |

### LavaFlow — Ribbon Mesh

Path mengikuti lereng dengan sampling `terrain.get_height_at()`:

```
  ╔══ kawah (r=20)
  ║
  ║  ← ribbon mesh melebar ke bawah
  ║
  ╚══ kaki gunung (r=80-100)
```

| Parameter | Default | Range |
|-----------|---------|-------|
| `segments` | 40 | — |
| `width_start` | 2.0 | — |
| `width_end` | 6.0 | — |
| `curve` | 0.4 | — |

**Mesh:** Segitiga berpasangan (2 vertex per cross-section). Winding: CCW.

### Lava Fragment Shader

```glsl
vec3 hot_core = vec3(1.0, 0.7, 0.05);   // pusat
vec3 mid      = vec3(0.9, 0.35, 0.02);  // tengah
vec3 edge     = vec3(0.5, 0.08, 0.01);  // tepi

float edge = 1.0 - abs(TexCoord.x - 0.5) * 2.0;  // 0 tepi, 1 tengah
float flow = TexCoord.y * 2.0 + time * 0.4;        // UV scroll
float vein = pow(sin(TexCoord.x * 12.0 + flow * 1.5) * 0.5 + 0.5, 4.0);
float pulse = 0.85 + 0.15 * sin(time * 2.0);
```

**Additive blend:** `blendFunc(SRC_ALPHA, ONE)` agar lava bercahaya tanpa menggelapkan background.

### 3 Lava Streams

| Stream | Angle | Start R | End R | Width |
|--------|-------|---------|-------|-------|
| 1 | -45° | 20 | 80 | 2→5 |
| 2 | 135° | 20 | 90 | 2.5→7 |
| 3 | 20° | 20 | 100 | 3→9 |

---

## Fase 3 — Atmospheric Effects ✅ Selesai

### Tujuan
Menambahkan efek atmosferik untuk membuat scene lebih hidup: volcanic lightning, ground glow, dan embers.

### File

| File | Isi |
|------|-----|
| `effects/lightning.py` | `Lightning` — bolt generator |
| `objects/ground_glow.py` | `GroundGlow` — decal lingkaran |
| `shaders/unlit.vert/.frag` | Passthrough colored shader |
| `shaders/glow.vert/.frag` | Radial gradient shader |

### Volcanic Lightning (`effects/lightning.py`)

Bolt acak di atas smoke plume.

```python
class Lightning:
    def update(self, dt):
        # Setiap 0.5-3 detik: generate bolt baru
        # Bolt: 7 segment jagged line
        # 40% chance: branch bolt (4 segment)
        # Life: 0.1-0.25 detik
```

**Bolt structure:**
- Core line: `(1.0, 0.9, 1.0)` — white-blue
- Glow line: `(0.4, 0.3, 0.8)` — blue glow
- Jitter maksimal di midpoint, nol di ujung
- Posisi: `center=(0, 150, 0)`, spread=25, height=120-250

**Rendering:** GL_LINES dengan additive blend.

### Ground Glow (`objects/ground_glow.py`)

Decal lingkaran di terrain sekitar kawah.

```glsl
// glow.frag — radial gradient
float dist = length(TexCoord - 0.5) * 2.0;
float edge = 1.0 - smoothstep(0.0, 1.0, dist);
float glow = edge * edge;
float pulse = 0.85 + 0.15 * sin(time * 2.0);
FragColor = vec4(glow_color * glow * pulse, glow * 0.4);
```

**Decal placement:**
- 1 large glow di tengah kawah (r=25, intensity=1.2)
- 4 small glow di tepi kawah (r=12, intensity=0.8)
- Y-offset +1 untuk anti z-fighting

### Embers (Particles)

Particle type ke-5 di `VolcanoEmitter`:

| Property | Value |
|----------|-------|
| Ratio | 15% |
| Color | `(1.0, 0.6, 0.05)` → `(0.8, 0.15, 0.0)` |
| Life | 3–8s |
| Scale | 2–6 |
| Velocity Y | 25% normal (float) |
| Drift | ±4 horizontal |

### Render Order Final

```
1. render_shadow_map()              → depth texture (FBO), light POV
2. clear(0.55, 0.7, 0.95)
3. render_sky()                     → depth off, cull off
4. render_terrain() + shadow        → depth on, blend off, sample shadow_map
5. render_lava() + glow decals      → depth on, blend additive
6. render_objects() + shadow        → depth on, blend off, sample shadow_map
7. render_lightning()               → depth on, blend additive
8. render_particles()               → blend on
```

---

## Fase 4 — Struktur & Interaksi 🔲 Belum

### Tujuan
Menambahkan bangunan buatan manusia di sekitar gunung berapi: pos observasi, pagar, papan informasi.

### Rencana File

| File | Isi |
|------|-----|
| `objects/building.py` | `ObservationPost` — bangunan dari primitives |
| `objects/fence.py` | `Fence` — barrier rail |
| `objects/sign.py` | `Sign` — billboard dengan text texture |

### ObservationPost

Model dari primitives OpenGL:

```
    /\
   /  \     <- pyramid roof
  /____\
  |    |
  |    |    <- cubic body
  |____|
   |  |     <- stilts/legs
   |  |
```

**Approach:** Generate vertex manual dari box + pyramid. Warna kayu/coklat.
- Body: 6 faces (cube), 12 triangles
- Roof: 4 triangles (pyramid)
- Stilts: 4 narrow boxes
- Total ~200 vertices per building

### Fence

Barrier sederhana di sekitar area berbahaya kawah:

```
  |---o---|---o---|---o---|
  post    rail    post    rail
```

- Generate sebagai line strip + posts (box)
- Vertex color merah-putih (safety)
- Ditempatkan di ring radial sekitar kawah (r=20-30)

### Sign / Papan Informasi

Billboard sederhana:

- Satu quad dengan texture text (generated via Pillow)
- Atau vertex color dengan pola garis-garis
- Dipasang di dekat area parkir / awal pendakian

### Placement Rules

| Objek | Elevasi | Jarak Kawah | Jumlah |
|-------|---------|-------------|--------|
| Observation Post | 30-50 m | 50-70 m | 1-2 |
| Fence | 80-100 m | 18-25 m | 1 ring |
| Sign | 0-20 m | 100+ m | 2-3 |

**Effort:** Low | **Impact:** Medium

---

## Fase 5 — Shadow Mapping ✅ Selesai

### Tujuan
Menambahkan bayangan directional untuk terrain dan objek agar scene lebih realistis.

### File

| File | Isi |
|------|-----|
| `rendering/shadow.py` | `ShadowMap` — FBO + depth texture + light matrix |
| `shaders/shadow.vert` | Depth-only vertex shader (position only) |
| `shaders/shadow.frag` | Minimal fragment shader (depth auto) |

### File dimodifikasi

| File | Perubahan |
|------|-----------|
| `shaders/terrain.frag` | + `shadow_factor()` dengan PCF 3x3 |
| `shaders/object.frag` | + `shadow_factor()` untuk objek |
| `rendering/renderer.py` | + `shadow_shader`, `render_shadow_map()`, `set_shadow_uniforms()` |

### ShadowMap Class (`rendering/shadow.py`)

```python
class ShadowMap:
    def __init__(self, ctx, shadow_program, terrain_vbo, terrain_ibo, size=2048):
        # Depth texture 2048x2048
        # FBO dengan depth attachment
        # VAO dari terrain VBO (position only)
    
    def compute_light_matrix(self, light_dir, scene_center, scene_radius):
        # View matrix: lookAt from light position
        # Orthographic projection: -R to R
        # Bias matrix: [-1,1] → [0,1]
    
    def render(self):
        # Bind FBO, set viewport
        # Clear depth
        # Render terrain with shadow.vert (depth only)
        # Restore viewport
```

**Light matrix:**
```
light_matrix = bias_matrix * ortho_proj * look_at_matrix
```

Dimana:
- `look_at`: dari posisi cahaya (arah berlawanan sun_dir)
- `ortho`: bounding box scene (radius 250)
- `bias`: mapping [-1,1] ke [0,1] untuk texture sampling

### Shadow Fragment Shader (PCF 3×3)

```glsl
float shadow_factor(vec3 world_pos) {
    vec4 proj = light_space * vec4(world_pos, 1.0);
    vec3 ndc = proj.xyz / proj.w;
    if (clamp test) return 1.0;  // outside shadow map

    float current = ndc.z;
    float bias = 0.002 * (1.0 - dot(normal, sun_dir));  // slope bias

    float shadow = 0.0;
    vec2 texel = 1.0 / textureSize(shadow_map, 0);
    for (int x = -1; x <= 1; x++)
        for (int y = -1; y <= 1; y++) {
            float s = texture(shadow_map, ndc.xy + vec2(x,y) * texel).r;
            shadow += current - bias > s ? 1.0 : 0.0;
        }
    return 1.0 - shadow / 9.0;
}
```

### Penerapan di Lighting

Diffuse sun light dikalikan dengan shadow factor:

```glsl
// terrain.frag
float shad = shadow_factor(FragPos);
vec3 lighting = (0.25 * ao + 0.75 * diff_sun * shad) * sun_color * base_color;
lighting += spec_sun * 0.2 * sun_color * shad;
```

Area lava (crater glow, rim lighting) tidak terpengaruh shadow (tetap terang).

### Teknis

| Item | Nilai |
|------|-------|
| Shadow map resolution | 2048×2048 |
| Filter | PCF 3×3 (9 samples) |
| Bias | Slope-based (0.002 base) |
| Scene boe ortho | ±250 units |

### Constraints

- Shadow hanya dari **directional light** (matahari)
- Point light (lava glow) tidak menghasilkan shadow
- Shadow map di-render tiap frame (bisa optimize jika perlu)
- Perfoma: shadow pass ≈ +1 draw call (terrain depth-only)

### Render Order (final)
unds | Center (0, 50, 0), radius 250 |
| Sun direction | `normalize(0.6, 1.0, 0.4)` |
| Light spac
```
1. render_shadow_map()             → depth texture (FBO)
2. clear color buffer
3. render_sky()
4. render_terrain() + shadow sample
5. render_lava() + glow decals
6. render_objects() + shadow sample
7. render_lightning()
8. render_particles()
```

---

## Ringkasan Statistik

### Scene Saat Ini (Fase 1-3)

| Objek | Jumlah | Vertex |
|-------|--------|--------|
| Pohon | ~50 | 10,000 |
| Lava flow (3 stream) | 3 | 240 |
| Glow decal | 5 | 165 |
| Partikel (max) | 10,000 | — |
| Terrain | 1 | ~160,000 |

### Jika Fase 4 ditambahkan

| Objek | Jumlah | Vertex |
|-------|--------|--------|
| Building | 2 | ~400 |
| Fence | 1 ring | ~200 |

### File Structure Final

```
volcano-moderngl/
├── core/
│   ├── window.py
│   └── camera.py
├── terrain/
│   ├── generator.py
│   └── mesh.py
├── rendering/
│   ├── renderer.py
│   ├── shader.py
│   └── shadow.py              ✅ Fase 5
├── particle/
│   ├── system.py
│   └── emitter.py
├── objects/
│   ├── base.py
│   ├── tree.py
│   ├── lava_flow.py
│   ├── ground_glow.py
│   ├── building.py         🔲 Fase 4
│   ├── fence.py            🔲 Fase 4
│   └── sign.py             🔲 Fase 4
├── effects/
│   ├── lighting.py
│   ├── fog.py
│   └── lightning.py
├── shaders/
│   ├── terrain.vert/.frag
│   ├── sky.vert/.frag
│   ├── particle.vert/.frag
│   ├── object.vert/.frag
│   ├── lava.vert/.frag
│   ├── unlit.vert/.frag
│   ├── glow.vert/.frag
│   └── shadow.vert/.frag      ✅ Fase 5
├── assets/textures/
├── docs/
│   └── roadmap.md
├── main.py
├── noise.py
├── AGENTS.md
└── requirements.txt
```
