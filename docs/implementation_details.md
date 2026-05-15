# Dokumentasi Implementasi Fitur-Fitur Utama

## Daftar Isi

1. [Implementasi Lingkungan dan Medan 3D](#implementasi-lingkungan-dan-medan-3d)
2. [Implementasi Sistem Partikel Erupsi](#implementasi-sistem-partikel-erupsi)
3. [Implementasi Pencahayaan dan Efek Atmosfer](#implementasi-pencahayaan-dan-efek-atmosfer)

---

## Implementasi Lingkungan dan Medan 3D

### 3.1 Generasi Terrain Prosedural

**File Terkait:** `terrain/generator.py`

#### Deskripsi

Gunung berapi 3D dihasilkan secara prosedural menggunakan kombinasi:

- **Perlin Noise 3D** untuk base terrain dengan natural variation
- **Cone-shaped Mathematical Functions** untuk membentuk vulkano shape
- **Multiple Mountain Approach** untuk menambah kompleksitas medan

#### Implementasi Detail

##### 1. Base Terrain Generation

```python
# Perlin Noise dengan 4 octaves
h_base = noise.pnoise3(x, z, 0.0, octaves=4, persistence=0.5, lacunarity=2.0) * 22.0
```

- Menghasilkan elevasi random yang natural
- Persistence = 0.5 mengontrol amplitudo dari octaves
- Lacunarity = 2.0 mengontrol frekuensi

##### 2. Volcano Shape Formation

```python
# Fungsi parabolic: (1 - t²)²
t = dist / m_radius  # normalized distance (0 to 1)
shape = (1.0 - (t ** 2)) ** 2
h_current = shape * m_height
```

- Membuat smooth cone shape yang natural
- Multiple mountains dengan radius berbeda menciptakan relief yang kompleks

##### 3. Crater Formation

```python
if m_crater > 0 and dist < m_crater:
    h_current -= (m_crater - dist) * 2.5
```

- Depresi circular di tengah puncak gunung
- Menambah depth untuk kawah tempat lava mengalir

##### 4. Normal Calculation

```python
# Central Differences untuk smooth shading
dx = (h_x+ - h_x-) / (2.0 * scale)
dz = (h_z+ - h_z-) / (2.0 * scale)
normal = normalize([-dx, 1, -dz])
```

### 3.2 Texture Mapping dan Blending

**File Terkait:** `main.py` (texture generation), `shaders/terrain.frag` (blending)

#### Texture Generation dengan FBM (Fractional Brownian Motion)

Tekstur dibuat secara prosedural menggunakan layered noise:

##### Grass Texture

- **Base Color:** RGB(20, 100, 20) - Hijau gelap
- **Detail Color:** RGB(100, 180, 60) - Hijau terang
- **Scale:** 25.0, Layers: 7, Persistence: 0.55
- **Resolusi:** 512x512 untuk detail tinggi

##### Rock Texture

- **Base Color:** RGB(80, 80, 80) - Abu-abu gelap
- **Detail Color:** RGB(180, 175, 170) - Abu-abu terang
- **Scale:** 18.0, Layers: 8, Persistence: 0.6
- Menciptakan cracks dan irregular surface

##### Lava Texture

- **Base Color:** RGB(200, 40, 0) - Merah tua
- **Detail Color:** RGB(255, 150, 0) - Oranye terang
- **Scale:** 12.0, Layers: 6, Persistence: 0.58
- **Extra Crack Pattern:** Noise treshold untuk realistic crack appearance

#### Texture Blending Strategy

**Height-Based Blending:**

```glsl
float grass_rock_mix = smoothstep(15.0, 35.0, h);
base_color = mix(color_grass, color_rock, grass_rock_mix);
```

- Transisi smooth antara grassland (h < 15) → rocky area (h > 35)

**Slope-Based Blending:**

```glsl
float slope = 1.0 - norm.y;  // 0 = flat, 1 = vertical
float slope_factor = smoothstep(0.4, 0.8, slope);
base_color = mix(base_color, color_rock * 0.8, slope_factor);
```

- Area curam (slope > 0.8) menunjukkan rock texture
- Menciptakan realism: exposed rock di cliff faces

**Lava Zone (Crater Top):**

```glsl
if (h > 75.0) {
    float lava_factor = smoothstep(75.0, 95.0, h);
    base_color = mix(base_color, glowing_lava, lava_factor);
}
```

- Zone lava di top crater (75 - 95 units)
- Glowing effect dengan dynamic flickering

---

## Implementasi Sistem Partikel Erupsi

**File Terkait:**

- `particle/system.py` - Core physics engine
- `particle/emitter.py` - Eruption behavior
- `shaders/particle.vert` dan `particle.frag` - Rendering

### 3.3 Particle Physics Simulation

#### Physics Equations

**Untuk Lava Particles (Heavy):**

1. **Gravitational Force:**

   ```
   gravity = 15.0 m/s² (downward)
   v_y += gravity * dt
   ```

2. **Air Resistance (Drag):**

   ```
   v *= 0.98  (quadratic approximation)
   ```

   - Mengurangi kecepatan seiring perjalanan
   - Realistic deceleration

3. **Collision & Splash:**
   ```
   if (height <= crater_height && distance_to_center < radius):
       bounce_energy = 0.4 * magnitude(velocity)
       v_y = magnitude(v_y) * 0.35 + bounce_energy * 0.2
       v_x += random(-8, 8)  // Splatter effect
       v_z += random(-8, 8)
   ```

   - Energy-based bounce: tidak semua energi hilang
   - Splatter: partikel menyebar ke samping saat impact
   - Natural dissipation: bounce semakin kecil di bounce kedua, ketiga, dst.

**Untuk Smoke Particles (Light):**

1. **Buoyancy Force:**

   ```
   buoyancy = 25.0 m/s² (upward)
   v_y += buoyancy * dt
   ```

2. **Turbulence (Swirl Motion):**

   ```
   swirl_speed = pnoise2(pos.x, pos.z) * 4.0
   angle = lifetime * 3.0
   v_x += sin(angle) * swirl_speed * dt * 0.5
   v_z += cos(angle) * swirl_speed * dt * 0.5
   ```

   - Menciptakan natural smoke column twist
   - Perlin noise untuk variation

3. **Air Damping:**
   ```
   v *= 0.995  (lighter damping than lava)
   ```

### 3.4 Particle Types dan Emission

**Emitter Configuration:** `particle/emitter.py`

#### Dynamic Eruption Intensity

```python
def get_eruption_intensity(time):
    base = 0.7 + 0.3 * sin(time * 0.3)      # Slow 20-second pulse
    secondary = 0.5 + 0.5 * sin(time * 1.2) # 5-second oscillation
    return base * secondary
```

- Menghasilkan realistic eruption pattern
- Intensity affects: emission rate, particle speed, spawn radius

#### Particle Types

| Tipe       | %   | Karakteristik                | Lifetime  | Ukuran   |
| ---------- | --- | ---------------------------- | --------- | -------- |
| **Lava**   | 35% | Merah-oranye, heavy, bounces | 1.2-4.0s  | 12-40px  |
| **Smoke**  | 35% | Gray, rises, disperses       | 7.0-18.0s | 35-110px |
| **Ash**    | 20% | Gray-brown, disperses more   | 5.0-12.0s | 8-25px   |
| **Debris** | 10% | Dark gray, launches far      | 2.0-3.5s  | 4-15px   |

#### Emission Rate

```python
base_emit_rate = 350 particles/second
current_rate = base_rate * eruption_intensity
```

### 3.5 Particle Rendering

**Point Sprite Technique:**

```glsl
// Fragment Shader
vec2 circ_coord = 2.0 * gl_PointCoord - 1.0;
float alpha = 1.0 - length(circ_coord);
if (alpha <= 0.0) discard;
```

- GPU-efficient rendering sebagai GL_POINTS
- Soft circular edges untuk natural look
- Single draw call untuk semua particles

---

## Implementasi Pencahayaan dan Efek Atmosfer

**File Terkait:**

- `shaders/terrain.frag` - Terrain lighting
- `shaders/sky.frag` - Sky rendering
- `effects/lighting.py` - Lighting configuration

### 3.6 Advanced Blinn-Phong Lighting Model

#### Components

**1. Directional Light (Sun)**

```glsl
vec3 sun_dir = normalize(vec3(0.6, 1.0, 0.4));
float diff_sun = max(dot(norm, sun_dir), 0.0);
vec3 halfway_sun = normalize(sun_dir + view_dir);
float spec_sun = pow(max(dot(norm, halfway_sun), 0.0), 32.0);
```

- Specular power: 32.0 untuk sharp highlights
- Kontribusi: 75% diffuse + 25% specular

**2. Point Light (Lava Glow)**

```glsl
vec3 l_dir = normalize(light_pos - FragPos);
float attenuation = 1.0 / (1.0 + 0.005 * dist + 0.0002 * dist²);
```

- Inverse square law untuk realistic falloff
- Dynamic flickering dengan 3 frequency sine waves

**3. Ambient Occlusion (Approximation)**

```glsl
float ao = mix(0.4, 1.0, smoothstep(-20.0, 30.0, h));
ao *= mix(0.6, 1.0, smoothstep(0.3, 0.8, 1.0 - slope));
```

- Height-based: valleys lebih gelap
- Slope-based: vertical areas lebih gelap

**4. Rim Lighting (Lava Halo)**

```glsl
float rim = 1.0 - max(dot(view_dir, norm), 0.0);
rim = pow(rim, 3.0);
if (h > 70.0) {
    lighting += rim * rim_color * 0.6;
}
```

- Creates backlit glow effect
- Terutama di tepi lava area

### 3.7 Dynamic Flickering Effect

```glsl
// Main flicker dari cahaya lava
float flicker = 0.7 + 0.3 * sin(time * 4.0) + 0.15 * sin(time * 2.7);

// Diterapkan pada lava_light
vec3 lava_light = vec3(1.0, 0.35, 0.05) * flicker * 3.0;
```

- Frequency 1: 4.0 Hz (dominant flicker)
- Frequency 2: 2.7 Hz (secondary variation)
- Menghasilkan natural, non-repetitive flickering

### 3.8 Sky Rendering dan Fog

**File:** `shaders/sky.frag`

#### Sky Gradient

```glsl
vec3 sky_zenith = vec3(0.15, 0.35, 0.85);    // Blue at top
vec3 sky_mid = vec3(0.4, 0.6, 0.95);         // Light blue middle
vec3 sky_horizon = vec3(1.0, 0.8, 0.6);      // Orange-yellow at horizon
```

- Multi-layer gradient untuk depth
- Realistic atmospheric scattering simulation

#### Cloud Rendering

```glsl
float cloud_noise = fbm(cloud_uv * 3.0);
float cloud_pattern = smoothstep(0.3, 0.7, cloud_noise);
```

- FBM dengan 6 octaves untuk detail
- Time-based animation untuk moving clouds

#### Sun Disk

```glsl
float sun_dist = distance(TexCoord / 10.0, sun_pos);
float sun_core = smoothstep(0.12, 0.08, sun_dist);
float sun_glow = smoothstep(0.25, 0.1, sun_dist) * 0.6;
vec3 sun_color = vec3(1.0, 0.9, 0.5) * (sun_core + sun_glow);
```

- Realistic sun appearance
- Core + glow untuk depth

#### Fog Effect

```glsl
float dist_cam = length(cam_pos - FragPos);
float fog_factor = exp(-pow((dist_cam * fog_density), 2.0));
vec3 final_color = mix(fog_color, lighting, fog_factor);
```

- Exponential fog untuk realistic distance fading
- fog_density = 0.003 (adjustable)
- Fog color matches sky horizon untuk cohesion

### 3.9 Tone Mapping

```glsl
sky_color = sky_color / (sky_color + vec3(1.0));
```

- Mencegah overexposure
- Realistic brightness preservation

---

## Performa dan Optimisasi

### GPU Efficiency

- **Particle Rendering:** Point sprites (single draw call)
- **Texture Tiling:** 40x tiling pada grass/rock untuk detail tanpa high-res textures
- **Shader Optimization:** Minimal branching, efficient math operations

### Quality Settings

- **Max Particles:** 5000 (configurable)
- **Emission Rate:** 350 base particles/second
- **Terrain Resolution:** 400x400 heightmap
- **Texture Resolution:** 512x512

---

## Hasil Visual Deskripsi

### Daytime Appearance

1. **Terrain:** Multi-layered texture blending creating natural slopes
2. **Lava:** Glowing pulsing light from crater
3. **Smoke:** Towering white columns rising from volcano
4. **Sky:** Gradient dari horizon oranye ke biru zenith dengan cloud shadows
5. **Lighting:** Sun illumination dengan subtle specular highlights

### Dynamic Elements

- **Eruption Cycles:** Intensity fluctuates naturally
- **Particle Physics:** Lava bounces, smoke swirls, debris scatters
- **Light Flickering:** Lava glow pulses in natural rhythm
- **Cloud Movement:** Animated cloud patterns drift across sky

---

## Troubleshooting & Future Enhancements

### Possible Improvements

1. **Normal Mapping:** Untuk extra surface detail tanpa geometry
2. **Parallax Occlusion Mapping:** Untuk kawah walls depth
3. **Advanced Particle Sorting:** Untuk back-to-front transparency blending
4. **Weather Effects:** Rain/snow particles layered with eruption
5. **Dynamic Mesh Deformation:** Crater shape changes during eruption

### Known Limitations

- Particles are 2D sprites (not 3D meshes)
- Terrain is static (not dynamic during simulation)
- Single light pass (no shadow mapping)
- Fog is simplified exponential formula
