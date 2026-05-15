# Phase 1, 2, 3 — Objek 3D + Lava Flow + Atmospheric Effects

## Ringkasan

Menambahkan pohon pinus procedural, lava flow, dan efek atmosferik (volcanic lightning, ground glow, embers) ke dalam scene vulkan. Sistem objek modular dengan full 3D transformasi.

---

## File Baru / Dimodifikasi

```
volcano-moderngl/
├── objects/                    # Package objek 3D
│   ├── __init__.py
│   ├── base.py                 # GameObject base class
│   ├── tree.py                 # PineTree — pohon pinus procedural
│   ├── lava_flow.py            # LavaFlow — ribbon mesh lava
│   └── ground_glow.py          # GroundGlow — decal glow kawah
├── effects/
│   ├── __init__.py
│   ├── lighting.py             # LightingConfig
│   ├── fog.py                  # FogConfig
│   └── lightning.py            # Lightning — volcanic lightning bolts
├── shaders/
│   ├── terrain.vert/.frag
│   ├── sky.vert/.frag
│   ├── particle.vert/.frag
│   ├── object.vert/.frag       # Generic textured object shader
│   ├── lava.vert/.frag         # Emissive animated lava
│   ├── unlit.vert/.frag        # Passthrough colored (lightning)
│   └── glow.vert/.frag         # Radial gradient (ground glow)
├── .vscode/
│   └── settings.json
└── docs/
    └── phase1-objects-walkthrough.md
```

### File dimodifikasi

| File | Perubahan |
|------|-----------|
| `main.py` | + import objek; generate ~50 trees; render lava/glow/lightning |
| `rendering/renderer.py` | + `object_shader`, `lava_shader`, `unlit_shader`, `glow_shader` + render methods |
| `terrain/generator.py` | + `get_steepness_at()` |
| `particle/emitter.py` | + ember particle type (15%) |
| `AGENTS.md` | Update arsitektur & performance notes |

### ❌ Dihapus

| Item | Alasan |
|------|--------|
| Batu (`objects/rock.py`) | Tidak digunakan lagi |
| Rumput (`objects/grass.py`) | Tidak digunakan lagi |

---

## Arsitektur

### `objects/base.py` — GameObject

```python
GameObject
  ├── set_position(x, y, z)      → translasi
  ├── set_rotation(x, y, z)      → Euler XYZ (Rx * Ry * Rz)
  ├── set_rotation_y(deg)        → rotasi sumbu Y saja
  ├── set_scale(s)               → skala seragam
  └── render()                   → draw call TRIANGLES
```

**Matrix building:** Semua transform disimpan sebagai parameter (`_pos`, `_rot[3]`, `_scale`), lalu `_build_matrix()` membangun matrix TRS penuh:

```
M = Ry * Rx * Rz (Euler Z-X-Y order)
  → yaw(Y), pitch(X), roll(Z)
```

Setiap `set_*` memicu rebuild matrix — tidak ada mutasi incremental.

**Vertex format:** `3f pos + 3f normal + 3f color` = 9 floats (36 bytes stride)

---

### `objects/tree.py` — PineTree (satu-satunya objek terrain)

Pohon pinus dengan 4 layer crown acak + batang melengkung:

```
     /\          <- layer 4 (tip)
    /  \
   /____\        <- layer 3
    |  |
   /____\        <- layer 2
    |  |
   /____\        <- layer 1
    |  |
   |____|        <- trunk top
   |    |
   |____|        <- trunk base (y=0)
```

| Parameter | Default | Range | Ketergantungan seed |
|-----------|---------|-------|---------------------|
| `height` | 10.0 | 5.0 – 16.0 | ✓ |
| `segments` | 10 | — | — |
| `seed` | 0 | — | ✓ |

**Variasi per seed:**
- Tinggi trunk `30-40%` dari total height
- Radius trunk `0.030-0.045 × height`
- Radius crown base `0.18-0.26 × height`
- **Batang melengkung** — `bend_x/z` = ±0.15, memberikan kesan pohon asli
- **Trunk tidak bulat sempurna** — radius setiap vertex ±15% random
- **4 layer crown** dengan tinggi dan radius random tiap layer

**Warna:**
- Batang: coklat `(0.32, 0.18, 0.07)`
- Daun: gradien hijau `(0.06, 0.25, 0.05)` → `(0.18, 0.55, 0.13)`

---

### `objects/rock.py` — Rock ❌ Dihapus

~~Batu procedural dari UV-sphere dengan vertex displacement pseudo-random.~~

| Parameter | Default | Range |
|-----------|---------|-------|
| `radius` | 2.0 | 1.0 – 4.0 |
| `segments` | 8 | — |
| `rings` | 5 | — |
| `seed` | 0 | — |

**Tidak digunakan lagi.** Hapus import di `main.py` jika ada.

---

### `shaders/object.frag` — Object Shader

```glsl
vec3 sun_dir = normalize(vec3(0.6, 1.0, 0.4));
float diff = max(dot(norm, sun_dir), 0.0);

vec3 ambient = 0.35 * sun_color;
vec3 diffuse = 0.65 * diff * sun_color;
vec3 result = (ambient + diffuse) * Color;
```

- Ambient 35% — objek tetap terlihat tanpa shadow mapping
- Specular 15% — kilau minimal
- Tidak ada texture — warna murni dari vertex color

---

## Winding Order (Critical Fix)

Semua mesh harus **CCW (Counter-Clockwise)** dari luar agar tidak di-cull oleh `CULL_FACE`.

```python
# ✅ Correct (CCW):
idxs.extend([b, b+2, b+1,  b+2, b+3, b+1])   # Tree
idxs.extend([bl, br, tl,  tl, br, tr])          # Rock (tidak dipakai)
```

Verifikasi dengan cross product:
```python
e1 = v1 - v0; e2 = v2 - v0
normal = cross(e1, e2)
dot(normal, outward_direction) > 0  # → CCW ←
```

---

## Rendering Pipeline

```
Render order:
1. clear(0.55, 0.7, 0.95)        → biru langit
2. render_sky()                   → DEPTH_TEST off, CULL_FACE off
3. render_terrain()               → DEPTH_TEST on, BLEND off
4. render_lava()                  → DEPTH_TEST on, BLEND additif
5. render_objects()               → DEPTH_TEST on, BLEND off
6. render_particles()             → BLEND on
```

Lava menggunakan **additive blending** (`SRC_ALPHA, ONE`) agar terlihat bercahaya.

`render_objects()` flow:
```python
def render_objects(self, camera):
    set m_proj, m_view, cam_pos (sekali)
    for each obj:
        set m_model uniform
        obj.vao.render(TRIANGLES)
```

---

## Placement Logic

### `main.py` — Generator

```python
random.seed(42)

# Tahap 1: 60 posisi random
for i in range(60):
    wx = random(-140, 140)
    wz = random(-140, 140)
    try_place_tree(wx, wz, i)
    try_place_rock(wx, wz, i+100)

# Tahap 2: cluster — 20 pohon pertama masing2 dpt 1-3 tetangga
for (wx, wz) in tree_positions[:20]:
    for j in range(random(1, 4)):
        try_place_tree(wx +/- 8, wz +/- 8, ...)
```

**Rules per objek:**

| Objek | Elevasi | Kemiringan | Jarak kawah | Sink (Y-offset) | Rotation |
|-------|---------|------------|-------------|-----------------|----------|
| Pohon | 2 – 40 m | < 2.0 | > 20 m | `y - 0.4` | X: ±3°, Y: 0-360° |

**Cluster effect:** pohon tidak tersebar uniform, melainkan mengelompok natural.

---

## Statistik

| Objek | Jumlah | Vertex/objek | Total vertex |
|-------|--------|-------------|--------------|
| Pohon | ~50 | 200 | 10,000 |
| Lava flow | 3 stream | 80 | 240 |
| Glow decal | 5 | 33 | 165 |
| **Total** | **~58** | — | **~10,400** |

Tambahan ~6.5% dari terrain (160K vertex). Lava + glow dampak minimal.

---

## Bug Fixes (Iterasi)

| Issue | Cause | Fix |
|-------|-------|-----|
| **Objek tidak muncul** | Winding CW → di-cull `CULL_FACE` | Reversed triangle indices |
| **Scale corrupt matrix** | Incremental element mutation | Rebuild TRS dari parameter |
| **Langit kuning** | `CULL_FACE` cull sky plane | `disable(CULL_FACE)` pas render sky |
| **Pohon menempel** | Y = terrain height, vertikal sempurna | Sink (-0.4) + tilt ±3° |

---

## Phase 2 — Lava Flow

### Files

| File | Isi |
|------|-----|
| `objects/lava_flow.py` | `LavaFlow` — ribbon mesh dari path points |
| `shaders/lava.vert` | Vertex shader dengan UV |
| `shaders/lava.frag` | Emissive animated lava + additive blend |

### LavaFlow — Ribbon Mesh

Mengikuti lereng gunung dari kawah ke bawah:

```
  ╔══ kawah (r=20)
  ║
  ║  ← ribbon mesh melebar ke bawah
  ║
  ╚══ kaki gunung (r=80-100)
```

- **Path:** sampling `terrain.get_height_at()` di setiap titik
- **Width:** narrow (2u) di atas → wide (5-8u) di bawah
- **Curve:** sine-based untuk aliran natural
- **Y-offset:** +0.15 untuk hindari z-fighting

### Lava Fragment Shader

```glsl
// 3 komponen warna
vec3 hot_core = vec3(1.0, 0.7, 0.05);   // pusat terang
vec3 mid      = vec3(0.9, 0.35, 0.02);  // tengah
vec3 edge     = vec3(0.5, 0.08, 0.01);  // tepi gelap

// Edge factor: 0 (pinggir) → 1 (tengah)
float edge = 1.0 - abs(TexCoord.x - 0.5) * 2.0;

// Flow animation: UV.y + time * 0.4
float flow = TexCoord.y * 2.0 + time * 0.4;

// Vein pattern: sin(x*12 + flow*1.5)
float vein = pow(sin(TexCoord.x * 12.0 + flow * 1.5) * 0.5 + 0.5, 4.0);

// Pulse: 0.85-1.15
float pulse = 0.85 + 0.15 * sin(time * 2.0);
```

**Additive blend:** `gl.blendFunc(SRC_ALPHA, ONE)` — warna lava glowing tanpa gelapkan background.

### 3 Lava Streams

Di `main.py`, 3 aliran dengan angle berbeda:

| Stream | Angle | Start R | End R | Width |
|--------|-------|---------|-------|-------|
| 1 | -45° (ke kamera) | 20 | 80 | 2→5 |
| 2 | 135° | 20 | 90 | 2.5→7 |
| 3 | 20° | 20 | 100 | 3→9 |

### Render order

```
1. clear(0.55, 0.7, 0.95)
2. render_sky()
3. render_terrain()
4. render_lava() + render_glow()    ← additive blend
5. render_objects()
6. render_lightning()                ← additive blend
7. render_particles()
```

---

## Phase 3 — Atmospheric Effects

### Files

| File | Isi |
|------|-----|
| `effects/lightning.py` | `Lightning` — bolt generator dengan branching |
| `objects/ground_glow.py` | `GroundGlow` — decal circle radial gradient |
| `shaders/unlit.vert/.frag` | Passthrough colored shader (pos+color → RGB) |
| `shaders/glow.vert/.frag` | Radial gradient shader (UV-based) |

### Volcanic Lightning

Bolt acak di atas plume, dengan branch.

```python
class Lightning:
    def update(self, dt):
        # Random interval 0.5-3s between flashes
        # Generate 7-segment jagged bolt core
        # 40% chance: branch bolt (5 segments)
        # Life: 0.1-0.25s (flash duration)
```

**Bolt generation:** Setiap bolt adalah polyline acak:
- Core line: white-blue `(1.0, 0.9, 1.0)` — 2 vertices per segment
- Glow line: blue-tinted `(0.4, 0.3, 0.8)` — 2 vertices per segment
- Jitter: strongest at midpoint, zero at ends (natural look)

**Rendering:**
```python
# Unlit shader: pos(3f) + color(3f) rendered as GL_LINES
self.ctx.blend_func = SRC_ALPHA, ONE  # additive
```

### Ground Glow

Decal lingkaran di terrain sekitar kawah menggunakan radial gradient.

```glsl
// glow.frag — radial gradient
float dist = length(TexCoord - 0.5) * 2.0;
float edge = 1.0 - smoothstep(0.0, 1.0, dist);
float glow = edge * edge;
float pulse = 0.85 + 0.15 * sin(time * 2.0);
FragColor = vec4(glow_color * glow * pulse, glow * 0.4);
```

**Decal placement:**
- 1 large glow at crater center (r=25, intensity=1.2)
- 4 small glows at cardinal directions (r=12, intensity=0.8)
- Y-offset: +1.0 above terrain to avoid z-fighting

### Embers (Particles)

Partikel ke-5 di VolcanoEmitter:

| Property | Value |
|----------|-------|
| Ratio | 15% |
| Color | `(1.0, 0.6, 0.05)` → `(0.8, 0.15, 0.0)` |
| Life | 3–8s |
| Scale | 2–6 (very small) |
| Vy | 25% normal speed (float upward) |
| Drift | ±4 units horizontal |

### Render order (updated)

```
1. clear(0.55, 0.7, 0.95)
2. render_sky()
3. render_terrain()
4. render_lava() + render glow decals    ← additive blend
5. render_objects()
6. render_lightning()                     ← additive blend
7. render_particles() (incl. embers)
```

---

## Cara Menambah Objek Baru

1. Buat `objects/burung.py`
2. Turunkan dari `GameObject`
3. Implement `_generate()` → return `(vertices, indices)` numpy
4. Format: `[x, y, z, nx, ny, nz, r, g, b]` (9 float)
5. Pastikan winding **CCW** dari luar
6. Di `main.py`: instance → `set_position/rotation/scale` → `renderer.add_object()`

```python
class Burung(GameObject):
    def __init__(self, ctx, program):
        verts, idxs = self._generate()
        super().__init__(ctx, program, verts, idxs)

    def _generate(self):
        verts, idxs = [], []
        # ... vertex generation ...
        return np.array(verts, 'f4'), np.array(idxs, 'i4')
```
