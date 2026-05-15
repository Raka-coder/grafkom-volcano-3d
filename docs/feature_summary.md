# Ringkasan Fitur untuk Laporan (Summary Features)

## 3.1 Implementasi Lingkungan dan Medan (Terrain) 3D

### Visualisasi Gunung Prosedural

Gunung berapi berhasil divisualisasikan secara prosedural menggunakan kombinasi teknik:

1. **Perlin Noise Base Terrain**
   - Menggunakan `noise.pnoise3()` dengan 4 octaves untuk elevasi random yang natural
   - Amplitudo base: ±22 units untuk variasi medan

2. **Volcano Shape Formation**
   - Fungsi parabolic: $(1 - t^2)^2$ untuk smooth cone shape
   - Gunung utama: tinggi 105 units, radius 70 units (gentle slope)
   - 4 gunung pendamping untuk kompleksitas visual

3. **Crater Generation**
   - Depresi circular di tengah puncak (radius 18 units, depth 45 units)
   - Menciptakan visual focus point untuk erupsi

### Texture Blending - Mencampur Grass, Rock, dan Lava

**Tekstur Grass** (Area Rendah)

- Warna hijau natural dengan detail noise
- Resolusi 512×512 dengan FBM 7 layers
- Smooth transition pada ketinggian 15-35 units

**Tekstur Rock** (Area Menengah)

- Warna abu-abu dengan crack patterns
- 8 layers FBM untuk irregular surface
- Muncul di area curam (slope > 0.4) dan ketinggian > 35 units

**Tekstur Lava** (Area Puncak)\*\*

- Warna oranye-merah dengan efek panas
- Dynamic tiling dengan time-based animation
- Visible di area crater (ketinggian > 75 units)

**Blending Strategy:**

- **Height-based:** Gradasi smooth menggunakan `smoothstep(15.0, 35.0, h)`
- **Slope-based:** Rock exposure di vertical surfaces dengan `1.0 - norm.y`
- **Lava zone:** Special glow effect di top crater area

---

## 3.2 Implementasi Sistem Partikel Erupsi

### Simulasi Partikel Dinamis

Eruption system mencakup 4 jenis partikel dengan physics yang akurat:

#### Type 1: Lava Particles (35%)

- **Visual:** Bright orange-red, gradually darkening
- **Physics:**
  - Gravitasi: 15.0 m/s² (downward)
  - Air drag: 0.98× per frame
  - Splashing behavior saat menyentuh crater
  - Energy-based bounce: 35% energy retained
- **Lifetime:** 1.2-4.0 detik
- **Size:** 12-40 pixels

#### Type 2: Smoke Particles (35%)

- **Visual:** Dark gray, fully transparent at death
- **Physics:**
  - Buoyancy: 25.0 m/s² (upward force)
  - Turbulent swirl menggunakan Perlin noise
  - Lighter damping: 0.995× per frame
- **Lifetime:** 7.0-18.0 detik (longest)
- **Size:** 35-110 pixels (grows while rising)

#### Type 3: Ash Particles (20%)

- **Visual:** Gray-brown dust, semi-transparent
- **Physics:** Mix of lava and smoke behaviors
- **Dispersal:** Random spreading (±3.0 units/frame)
- **Lifetime:** 5.0-12.0 detik
- **Size:** 8-25 pixels

#### Type 4: Debris/Rock Particles (10%)

- **Visual:** Dark gray, opaque throughout
- **Physics:** Heavy projectiles
- **Launch:** 2× horizontal velocity for distance
- **Lifetime:** 2.0-3.5 detik (fastest decay)
- **Size:** 4-15 pixels

### Dynamic Eruption Intensity

Erupsi tidak statis - menggunakan kombinasi sine waves:
$$I(t) = [0.7 + 0.3 \sin(0.3t)] \times [0.5 + 0.5 \sin(1.2t)]$$

- Main frequency (0.3 Hz): slow ~20-second pulsing
- Secondary frequency (1.2 Hz): ~5-second oscillation
- Affects: emission rate, particle velocity, spawn radius

### Collision & Splashing

**Crater Impact:**

```
- Deteksi height <= 102 units AND distance < 20 units
- Bounce calculation: v_new = |v_old| × 0.35 + bonus × 0.2
- Splatter: ±8 units random horizontal velocity
- Result: realistic "lava pool" effect
```

---

## 3.3 Implementasi Pencahayaan dan Efek Atmosfer

### Pencahayaan Dinamis - Blinn-Phong Model

#### Component 1: Directional Light (Sun)

$$L_{sun} = k_d \times \max(N \cdot L, 0) + k_s \times (N \cdot H)^{32}$$

- Direction: $(0.6, 1.0, 0.4)$ (from NE, top)
- Color: $(1.0, 0.95, 0.85)$ warm white
- Contribution: 75% diffuse + 25% specular

#### Component 2: Point Light (Lava Glow)

$$L_{lava} = \frac{I}{1 + 0.005d + 0.0002d^2} \times \text{flicker}$$

- Position: Crater center (0, 100, 0)
- Color: Dynamic orange-red dengan flicker
- Range: ~200 units (inverse square law)

#### Component 3: Ambient Occlusion (Fake)

- Height-based: Valleys (low h) lebih gelap
- Slope-based: Vertical surfaces (high slope) lebih gelap
- Result: subtle depth cues

#### Component 4: Rim Lighting

- Tepi objects yang backlighting mendapat orange halo
- Intensitas naik dengan height (strongest di lava area)
- Creates visual drama pada erupsi

### Dynamic Flickering

Lava light flicker menggunakan 3 sine waves:
$$F(t) = 0.7 + 0.3 \sin(4t) + 0.15 \sin(2.7t)$$

- Frequency 1 (4.0 Hz): dominant flicker
- Frequency 2 (2.7 Hz): secondary variation
- Frequency 3 (4.0 Hz): base intensity
- Result: natural, non-repetitive glow

### Efek Kabut (Fog)

Exponential fog formula:
$$F = e^{-(d \times \rho)^2}$$

- Density ρ = 0.003 (adjustable)
- Color: $(0.5, 0.6, 0.7)$ (sky-matched)
- Effect: distant terrain fades naturally

### Warna Langit & Skybox

**Gradient Approach:**

```
Height 0% (Horizon):   RGB(1.0, 0.8, 0.6)  // Orange-yellow
Height 50% (Mid):      RGB(0.4, 0.6, 0.95) // Light blue
Height 100% (Zenith):  RGB(0.15, 0.35, 0.85) // Deep blue
```

**Cloud Rendering:**

- FBM dengan 6 octaves untuk natural pattern
- Real-time animation (cloud_uv += time × 0.02)
- Shadow regions untuk depth

**Sun Disk:**

- Core disk dengan sharp edge
- Glow halo untuk bloom effect
- Color: warm yellow $(1.0, 0.9, 0.5)$

---

## Hasil Visual Deskripsi

### Siang Hari (Well-Lit)

1. ✓ Gunung dengan texture blending: grass slopes → rock cliffs → lava crater
2. ✓ Kawah glowing dengan orange pulsing light
3. ✓ Smoke column putih tebal naik tinggi
4. ✓ Langit gradient dari horizon oranye ke biru zenith
5. ✓ Cloud shadows bergerak pelan

### Dinamis Elements

- **Eruption Cycles:** Semburan intensitas meningkat/menurun natural
- **Lava Physics:** Bounces di crater, splatter effects
- **Smoke Swirls:** Turbulent rising dengan twist motion
- **Light Flickering:** Natural pulsing dari kawah glow
- **Particle Fadeout:** Smooth opacity transition

### Performance

- 5000 max active particles
- Single draw call per frame (point sprites)
- 512×512 textures dengan tiling
- Runs smoothly pada target hardware (OpenGL 3.3+)
