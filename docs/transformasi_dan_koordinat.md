# Transformasi (Translasi, Scaling, Rotasi) & Sistem Koordinat

## 1. Matriks Transformasi Model (TRS)

**Lokasi:** `objects/base.py:22-56` — metode `_build_matrix()`

Matriks model (`M_model`) menggabungkan tiga transformasi dasar: **Translasi (T)**, **Rotasi (R)**, dan **Scaling (S)** dalam satu matriks 4×4. Urutan penerapannya adalah **Scale → Rotate → Translate** (SRT), yang berarti vertex mengalami:

```
V_world = T × R × S × V_local
```

### a. Scaling (S)

Faktor skala `s` diterapkan dengan mengalikan komponen rotasi di kolom 0-2 baris 0-2:

```python
# objects/base.py:43-45
m[0, 0] = m00 * s
m[0, 1] = m01 * s
m[0, 2] = m02 * s
m[1, 0] = m10 * s
m[1, 1] = m11 * s
m[1, 2] = m12 * s
m[2, 0] = m20 * s
m[2, 1] = m21 * s
m[2, 2] = m22 * s
```

Dalam notasi matriks, ini ekuivalen dengan mengalikan matriks rotasi dengan matriks scaling:

```
S × R  =  [ s×R00  s×R01  s×R02  0 ]
           [ s×R10  s×R11  s×R12  0 ]
           [ s×R20  s×R21  s×R22  0 ]
           [   0      0      0     1 ]
```

Faktor skala diset melalui `set_scale(s)` (`objects/base.py:70-72`) dan default 1.0.

### b. Rotasi (R) — Euler Angles

Rotasi menggunakan sudut Euler sumbu **X (pitch), Y (yaw), Z (roll)** dalam derajat, dikonversi ke radian:

```python
# objects/base.py:24
rx, ry, rz = np.radians(self._rot[0]), np.radians(self._rot[1]), np.radians(self._rot[2])
```

Matriks rotasi gabungan `R = Ry × Rx × Rz` (Y-X-Z order) dihitung manual menggunakan identitas trigonometri:

```python
# objects/base.py:33-41
m00 = cyr*czr + syr*sxr*szr    # cosY·cosZ + sinY·sinX·sinZ
m01 = -cyr*szr + syr*sxr*czr   # -cosY·sinZ + sinY·sinX·cosZ
m02 = syr*cxr                  # sinY·cosX
m10 = cxr*szr                  # cosX·sinZ
m11 = cxr*czr                  # cosX·cosZ
m12 = -sxr                     # -sinX
m20 = -syr*czr + cyr*sxr*szr   # -sinY·cosZ + cosY·sinX·sinZ
m21 = syr*szr + cyr*sxr*czr    # sinY·sinZ + cosY·sinX·cosZ
m22 = cyr*cxr                  # cosY·cosX
```

Ini adalah matriks rotasi 3×3 penuh hasil perkalian:

```
R = Ry(yaw) × Rx(pitch) × Rz(roll)
```

Setiap rotasi sumbu individual:

```
Rx(θ) = [ 1     0       0   ]     Ry(θ) = [ cosθ  0  sinθ ]     Rz(θ) = [ cosθ -sinθ  0 ]
        [ 0   cosθ  -sinθ ]             [   0    1   0   ]             [ sinθ  cosθ  0 ]
        [ 0   sinθ   cosθ ]             [-sinθ  0  cosθ ]             [   0    0    1 ]
```

Rotasi diset melalui `set_rotation(x_deg, y_deg, z_deg)` (`objects/base.py:62-64`) atau `set_rotation_y(deg)` (`objects/base.py:66-68`).

### c. Translasi (T)

Translasi disimpan di kolom ke-3 (indeks 3) dari matriks 4×4:

```python
# objects/base.py:46-54
m[0, 3] = cx   # Translation X
m[1, 3] = cy   # Translation Y
m[2, 3] = cz   # Translation Z
```

Karena translasi adalah operasi terakhir dalam SRT, vektor translasi `(cx, cy, cz)` langsung ditempatkan di kolom terakhir tanpa terpengaruh rotasi/scaling.

Posisi diset melalui `set_position(x, y, z)` (`objects/base.py:58-60`).

### d. Matriks Model Lengkap

Hasil akhir matriks model 4×4 berbentuk:

```
     [ s×R00  s×R01  s×R02  cx ]
M =  [ s×R10  s×R11  s×R12  cy ]
     [ s×R20  s×R21  s×R22  cz ]
     [   0      0      0     1  ]
```

### e. Matriks Model Non-GameObject

Beberapa objek tidak menggunakan kelas `GameObject` dan membuat matriks modelnya sendiri:

- **Terrain** (`rendering/renderer.py:99-100`): matriks identitas — terrain sudah dalam world coordinates
- **GroundGlow** (`objects/ground_glow.py:20-23`): translasi langsung di `m[3,0:3]`
- **LavaFlow** (`objects/lava_flow.py`): tidak punya matriks model — vertex sudah dalam world space karena path di-generate langsung dengan koordinat dunia

---

## 2. Sistem Koordinat (Coordinate Spaces)

Pipeline rendering menggunakan **5 ruang koordinat** yang berurutan:

```
Local Space → World Space → View Space (Camera) → Clip Space → Screen Space
```

### a. Local Space (Object Space)

Vertex dalam koordinat lokal objek. Pusat objek di `(0,0,0)`. Contoh:

- **PineTree** (`objects/tree.py`): trunk dari y=0 sampai y=trunk_h, crown di atasnya
- **Rock** (`objects/rock.py:30-32`): sphere dengan radius ~2 unit, pusat di origin
- **GrassPatch** (`objects/grass.py:20-28`): cross-shaped billboard, pusat di origin
- **GroundGlow** (`objects/ground_glow.py:28`): disk dengan pusat di `(0,0,0)`

### b. World Space

Transformasi dari local ke world space:

```glsl
// Semua vertex shader (terrain, object, lava, glow)
vec4 world_pos = m_model * vec4(in_position, 1.0);
```

- **Terrain** menggunakan matriks identitas (`renderer.py:99`) — vertex terrain sudah dibangun di world space oleh `TerrainGenerator.get_vertex_data()` (`terrain/generator.py:119-121`)
- **Objects** (pohon, batu, fumarol) menggunakan `obj.model_matrix` individual (`renderer.py:128`)
- **Glow decals** menggunakan matriks model sendiri (`renderer.py:155`)
- **Particles** menggunakan posisi langsung dalam world space (tanpa M_model) — posisi diupdate oleh CPU di `system.py:110`
- **Lightning** juga world space langsung (`unlit.vert:12`)
- **Sky** (`sky.vert:14-16`) digeser mengikuti kamera horizontal

### c. View Space (Camera Space)

Transformasi dari world ke view space menggunakan **View Matrix** (LookAt):

```glsl
vec4 view_pos = m_view * vec4(world_pos, 1.0);
```

View matrix dibangun di `core/camera.py:82-95`:

```python
def _look_at(self, eye, target, up):
    f = normalize(target - eye)         # forward vector
    s = normalize(cross(f, up))         # right vector
    u = cross(s, f)                     # true up vector

    res = identity(4)
    res[0, 0:3] = s                     # basis X = right
    res[1, 0:3] = u                     # basis Y = up
    res[2, 0:3] = -f                    # basis Z = -forward
    res[0:3, 3] = [-dot(s,eye), -dot(u,eye), dot(f,eye)]  # translasi negated
```

Ini memindahkan dunia sehingga kamera berada di origin, menghadap -Z. Vektor front kamera dihitung dari spherical coordinates (yaw & pitch):

```python
# core/camera.py:30-32
front[0] = cos(yaw) × cos(pitch)
front[1] = sin(pitch)
front[2] = sin(yaw) × cos(pitch)
```

**Arah pandang kamera (front)** juga digunakan sebagai sumbu Z view matrix.

**Particle** dan **lightning** hanya punya `m_view` dan `m_proj` (tanpa `m_model`) karena partikel dan petir sudah dalam world space.

### d. Clip Space

Transformasi dari view ke clip space menggunakan **Projection Matrix**:

```glsl
gl_Position = m_proj * vec4(view_pos, 1.0);
```

Projection matrix adalah **perspective projection** (`core/camera.py:97-109`):

```python
f = 1 / tan(fov / 2)
res = [
    [f/aspect,   0,          0,                  0          ],
    [0,          f,          0,                  0          ],
    [0,          0,          (far+near)/(near-far), 2×far×near/(near-far)],
    [0,          0,         -1,                  0          ]
]
```

Setelah transformasi ini, koordinat dalam **Clip Space** (homogeneous). GPU melakukan **perspective division** (`gl_Position.xyz / gl_Position.w`) untuk masuk ke **NDC (Normalized Device Coordinates)**:

- NDC: x,y ∈ [-1, 1], z ∈ [-1, 1] (OpenGL convention)
- Benda dengan `|x|,|y|,|z| > w` sebelum division akan ter-clip (tidak terlihat)

### e. Screen Space (Viewport Transform)

GPU secara otomatis memetakan NDC ke koordinat layar (viewport):

```
screen_x = (ndc_x + 1) / 2 × viewport_width
screen_y = (ndc_y + 1) / 2 × viewport_height
```

Viewport diset di window (default 1280×720).

---

## 3. Penerapan di Setiap Shader

### terrain.vert — Transformasi Lengkap dengan Normal Matrix

```glsl
// shaders/terrain.vert:20-29
FragPos = vec3(m_model * vec4(in_position, 1.0));  // Local → World
Normal = mat3(transpose(inverse(m_model))) * in_normal;
gl_Position = m_proj * m_view * vec4(FragPos, 1.0); // World → Clip
```

Normal vector ditransformasi menggunakan **Normal Matrix** (`transpose(inverse(M_model))`) untuk memastikan normal tetap tegak lurus permukaan meskipun objek di-scale atau di-rotate.

### object.vert — Sama seperti terrain

```glsl
// shaders/object.vert:16-19
FragPos = vec3(m_model * vec4(in_position, 1.0));
Normal = mat3(transpose(inverse(m_model))) * in_normal;
gl_Position = m_proj * m_view * vec4(FragPos, 1.0);
```

### particle.vert — Hanya View & Projection

```glsl
// shaders/particle.vert:14
gl_Position = m_proj * m_view * vec4(in_position, 1.0);
```

Partikel sudah dalam world space (posisi diupdate CPU), tidak perlu M_model.

### sky.vert — Translasi Manual + View & Projection

```glsl
// shaders/sky.vert:14-18
vec3 pos = in_position;
pos.x += cam_pos.x;
pos.z += cam_pos.z;
gl_Position = projection * view * vec4(pos, 1.0);
```

Sky plane (4000×4000) digeser mengikuti kamera horizontal agar langit selalu mengelilingi kamera.

### lava.vert — Sama seperti terrain

```glsl
// shaders/lava.vert:13-14
vec4 world = m_model * vec4(in_position, 1.0);
gl_Position = m_proj * m_view * world;
```

### glow.vert — Sama seperti terrain

```glsl
// shaders/glow.vert:13
gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
```

### unlit.vert — Hanya View & Projection

```glsl
// shaders/unlit.vert:12
gl_Position = m_proj * m_view * vec4(in_position, 1.0);
```

### shadow.vert — Light Space (untuk Shadow Map)

```glsl
// shaders/shadow.vert:9
gl_Position = light_space * m_model * vec4(in_position, 1.0);
```

Transformasi ke **Light Space** (dari perspektif matahari) untuk di-render ke depth texture shadow map.

---

## 4. Pengiriman Matriks ke GPU

**Lokasi:** `rendering/renderer.py`

Semua matriks dikirim ke shader dalam format **column-major** (konvensi OpenGL) dengan `.astype('f4').T.tobytes()`:

```python
# renderer.py:96-97
prog.set_uniform('m_proj', camera.get_projection_matrix().astype('f4').T.tobytes())
prog.set_uniform('m_view', camera.get_view_matrix().astype('f4').T.tobytes())
```

- **proj + view** dikirim sekali per frame (sama untuk semua objek)
- **m_model** dikirim per-objek di render loop (`renderer.py:128`)
- Normal matrix (`transpose(inverse(M_model))`) dihitung di vertex shader, bukan CPU

---

## 5. Tabel Ringkasan Transformasi per Entity

| Entity | Local → World | World → View | View → Clip | File Referensi |
|--------|--------------|-------------|-------------|----------------|
| Terrain | identity (langsung world) | `m_view` | `m_proj` | `terrain.vert`, `renderer.py:96-100` |
| Objects (tree, rock, dll) | `m_model` per objek | `m_view` | `m_proj` | `object.vert`, `renderer.py:119-129` |
| Lava Flow | identity (langsung world) | `m_view` | `m_proj` | `lava.vert`, `renderer.py:138-146` |
| Glow Decal | `m_model` per decal | `m_view` | `m_proj` | `glow.vert`, `renderer.py:151-158` |
| Particles | CPU (world langsung) | `m_view` | `m_proj` | `particle.vert`, `renderer.py:181-182` |
| Lightning | CPU (world langsung) | `m_view` | `m_proj` | `unlit.vert`, `renderer.py:169-170` |
| Sky Dome | shift horizontal CPU | `view` | `projection` | `sky.vert`, `renderer.py:79-80` |
| Shadow Map | `m_model` (identity) | `light_space` | — | `shadow.vert`, `shadow.py:58` |

---

## 6. Contoh Aliran Data Transformasi (PineTree)

1. **Local Space:** Vertex tree di-generate di `tree.py` dengan trunk di y=0 hingga y=trunk_h
2. **set_position(wx, h-0.4, wz)** → `_build_matrix()` menyusun `M_model = T × R × S`
3. **set_rotation(…)** → memperbarui komponen rotasi di matriks
4. Di vertex shader: `world = M_model × local` → tree muncul di posisi (wx, h-0.4, wz) di world
5. `view = M_view × world` → dilihat dari posisi kamera
6. `clip = M_proj × view` → diproyeksikan dengan perspective
7. GPU: clip → NDC → screen → pixel di layar

---

## 7. Light Space (Shadow Mapping)

**Lokasi:** `rendering/shadow.py:23-59`

Shadow map menggunakan transformasi tambahan: **Light Space** adalah world space yang dilihat dari posisi matahari.

```
light_view = lookAt(light_pos, scene_center, world_up)
light_proj = orthographic(scene_radius)  // atau frustum seragam
light_matrix = bias × light_proj × light_view
```

Matriks bias memetakan NDC [-1,1] ke UV [0,1]:

```
bias = [ 0.5  0   0   0.5 ]
       [  0  0.5  0   0.5 ]
       [  0   0  0.5  0.5 ]
       [  0   0   0    1  ]
```

Di fragment shader, world position dikonversi ke light space untuk men-sampling depth texture:

```glsl
// terrain.frag:30-31
vec4 proj = light_space * vec4(world_pos, 1.0);
vec3 ndc = proj.xyz / proj.w;  // uv.xy = shadow map coordinate, uv.z = depth from light
```
