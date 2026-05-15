# Deskripsi Visual Hasil Implementasi

## Daftar Isi

1. [Aspek Visual Medan & Tekstur](#aspek-visual-medan--tekstur)
2. [Aspek Visual Sistem Partikel](#aspek-visual-sistem-partikel)
3. [Aspek Visual Pencahayaan & Atmosfer](#aspek-visual-pencahayaan--atmosfer)
4. [Kombinasi Elemen Visual](#kombinasi-elemen-visual)

---

## Aspek Visual Medan & Tekstur

### 3.1.1 Bentuk Gunung Berapi

**Karakteristik Geometric:**

- **Profil:** Smooth cone shape dengan gentle slopes (~30° average gradient)
- **Puncak:** Elevated crater di center, surrounded by peak variation dari Perlin noise
- **Kawah:** Circular depression ~15 units radius, depth ~45 units
- **Satelit Mountains:** 4 smaller cones di surrounding area untuk natural landscape
- **Total Height:** ~105 units (crater floor di 102, peak varied ±3)

**Visual Impression:**

- Dari jauh: Iconic volcano silhouette
- Dari dekat: Natural rocky surface dengan no unnatural geometry
- Dari udara (bird's eye): Perfect circular crater dengan radiating ridges

### 3.1.2 Texture Distribution

**Grass Zone (Height 0-15 units)**

- **Color Palette:** Gradient hijau dari dark ($\approx$RGB 20,100,20) ke light (RGB 100,180,60)
- **Pattern:** FBM noise dengan 7 layers menciptakan organic variation
- **Coverage:** Lower slopes dari mountain
- **Visual:** Meadow-like appearance dengan natural color randomness
- **Tiling:** 40× untuk maintain detail di large areas

**Rock Zone (Height 15-35 units + Steep Slopes)**

- **Color Palette:** Abu-abu dari dark (RGB 80,80,80) ke light (RGB 180,175,170)
- **Pattern:** Crack-like patterns dari 8-layer FBM
- **Coverage:** Mid-elevation dan vertical cliff faces
- **Visual:** Jagged, weathered stone appearance
- **Slope Detection:** Areas dengan slope > 0.4 show more rock texture
- **Special Effect:** Rock darkened pada cliff faces (50% brightness reduction) untuk depth

**Lava Zone (Height 75-95 units)**

- **Color Palette:** Hot lava dari dark red (RGB 200,40,0) ke bright orange (RGB 255,150,0)
- **Pattern:** Animated texture dengan time-based UV offset
  - Formula: `TexCoord * 15.0 + vec2(time * 0.03)`
  - Speed: ~0.03 units per second (very slow, realistic)
- **Coverage:** Top crater area exclusively
- **Visual:** Glowing molten rock appearance
- **Animation:** Subtle surface "flow" without noticeable repetition

### 3.1.3 Texture Blending Mechanics

**Height-based Blending:**

```
Height < 15:        100% Grass
Height 15-35:       Gradient Grass → Rock
Height > 35:        100% Rock (unless lava zone)
Height 75-95:       Mix Rock + Lava glow
```

**Slope-based Blending:**

```
Slope < 0.4:        Base color (grass/rock)
Slope 0.4-0.8:      Increasingly more rock
Slope > 0.8:        Rock with darker tone (shadow effect)
```

**Visual Result:**

- Seamless color transitions tanpa hard boundaries
- Natural appearance sesuai real mountain weathering
- Rock appearance di exposed cliff faces
- Lava concentrated di crater region dengan natural glow

---

## Aspek Visual Sistem Partikel

### 3.2.1 Lava Particle Effects (35% dari emission)

**Appearance:**

- **Color Start:** Bright orange RGB(1.0, 0.35, 0.0) = Hot lava
- **Color End:** Dark red RGB(0.3, 0.05, 0.0) = Cooled lava
- **Transition:** Linear gradient over lifetime
- **Size Range:** 12-40 pixels (glowing spheres)
- **Opacity:** Starts opaque, fades at end of life

**Motion Pattern:**

1. **Initial Launch:** Cone-shaped velocity (upward + outward)
   - Vertical: 25-75 m/s
   - Horizontal: 5-25 m/s (varies with eruption intensity)
2. **Ballistic Arc:**
   - Gravity: 15 m/s² downward (realistic Earth gravity)
   - Peak height: typically 40-60 units above launch point
   - Time to impact: 2-4 seconds
3. **Impact & Bounce:**
   - First impact: 35% velocity retained (high energy splash)
   - Splatter: ±8 units random horizontal dispersion
   - Secondary bounces: progressively smaller (0.35× rule)
   - Final settle: lava accumulates di crater bottom

**Visual Impression:**

- Fiery orange arcs shooting upward
- Natural parabolic trajectories
- Realistic impact with splashing effect
- Multiple bounces creating "lava pool" effect

### 3.2.2 Smoke Particle Effects (35% dari emission)

**Appearance:**

- **Color Start:** Dark gray RGB(0.12-0.35, 0.12-0.35, 0.12-0.35) = Fresh smoke
- **Color End:** Almost black RGB(0.03, 0.03, 0.03) = Dispersed smoke
- **Transition:** Gradient fade over long lifetime
- **Size Range:** 35-110 pixels (large billowing clouds)
- **Opacity:** 85% opaque start, fades to 0% at end
- **Growth:** Expands 5-10× during lifetime (dispersal effect)

**Motion Pattern:**

1. **Upward Rise:** Constant buoyancy 25 m/s²
   - Significantly lighter than gravity (creates lift)
   - Light damping: 0.995 per frame (drifts slowly)
2. **Turbulent Swirl:**
   - Perlin noise-based turbulence
   - Sine/cosine oscillation: $\sin(t \times 3.0)$, $\cos(t \times 3.0)$
   - Creates natural tornado-like twist di smoke column
   - Swirl strength: 4.0 units (adjustable per Perlin sample)
3. **Dispersal:**
   - Smoke spreads horizontally as it rises
   - Width increases from 20 units (launch) → 80 units (final)
   - Creates realistic expanding plume

**Visual Impression:**

- Thick white smoke column rising high
- Natural swirling motion (tidak robotic)
- Gradual opacity fade creating height effect
- Realistic volcanic ash column aesthetic

### 3.2.3 Ash Particle Effects (20% dari emission)

**Appearance:**

- **Color Start:** Gray-brown RGB(0.25-0.45, gray×0.9, gray×0.8) = Warm ash
- **Color End:** Faded brown RGB(0.1, 0.08, 0.06) = Settling ash
- **Size Range:** 8-25 pixels (finer than smoke)
- **Opacity:** 70% start, fades gradually

**Motion Pattern:**

- Mix antara lava (downward) dan smoke (upward)
- Buoyancy: 20 m/s² (weaker than smoke, stronger than lava)
- Horizontal dispersal: ±3.0 units random drift
- Creates intermediate layer visual between lava and smoke

**Visual Impression:**

- Fine particles drifting outward
- Separate visual "layer" dari eruption

### 3.2.4 Debris Particle Effects (10% dari emission)

**Appearance:**

- **Color:** Dark gray throughout RGB(0.15 → 0.08)
- **Size Range:** 4-15 pixels (smallest particles)
- **Opacity:** Remains opaque (solid rock)

**Motion Pattern:**

- Heavy horizontal launch: 2× speed multiplier
- Minimal upward velocity
- Short lifetime: 2-3.5 seconds
- No lift forces (pure gravity + drag)
- Fast falloff: terrain impact after ~1-2 seconds

**Visual Impression:**

- Rapid projectiles launching outward
- Quick fallback to ground
- Scattered debris field around volcano

### 3.2.5 Dynamic Eruption Intensity

**Pulsing Pattern:**
$$I(t) = [0.7 + 0.3\sin(0.3t)] \times [0.5 + 0.5\sin(1.2t)]$$

**Visual Manifestation:**

- Peak eruptions: emission rate 350 → 525 particles/sec
- Low eruptions: emission rate 350 → 175 particles/sec
- Period: ~20 seconds main cycle + ~5 second secondary
- Non-repetitive due to beat frequency between components

**Effects of Intensity Variation:**
| Metric | Low | Peak |
|--------|-----|------|
| Particle count | 1500-2000 | 3500-4500 |
| Smoke column height | 150 units | 200+ units |
| Lava spread radius | 30 units | 60 units |
| Glow intensity | 1.0× | 1.3× |
| Splash effects | Minimal | Vigorous |

---

## Aspek Visual Pencahayaan & Atmosfer

### 3.3.1 Directional Sun Lighting

**Light Source Properties:**

- **Direction:** $(0.6, 1.0, 0.4)$ normalized = from NE, high angle
- **Color:** RGB(1.0, 0.95, 0.85) = warm natural daylight
- **Model:** Blinn-Phong dengan specular power = 32.0

**Terrain Illumination:**

```
Illumination = ambient_occlusion + diffuse + specular
             = 0.25×ao + 0.75×max(N·L, 0) + 0.2×(N·H)^32
```

**Visual Effects:**

- Grass areas: medium brightness, slight green color shift
- Rock areas: darker on shadow side, brighter on sun side
- Specular highlights: sharp bright spots on rocks (32.0 power)
- Natural shading: valleys slightly darkened, ridges brightened

### 3.3.2 Lava Point Light Glow

**Light Source Properties:**

- **Position:** Crater center (0, 100, 0) - fixed
- **Effective Range:** ~200 units (inverse square law)
- **Color:** Dynamic orange-red dengan flicker
- **Intensity:** Peaks 3.0× normal, minimum 0.4×

**Flickering Pattern:**

```
flicker = 0.7 + 0.3×sin(4.0t) + 0.15×sin(2.7t)
lava_light = RGB(1.0, 0.35, 0.05) × flicker × 3.0
```

**Attenuation Formula:**
$$\text{atten} = \frac{1}{1 + 0.005d + 0.0002d^2}$$

**Visual Effects:**

- Nearby terrain (d < 50): Strong orange illumination
- Medium range (d = 50-150): Warm orange tint
- Far range (d > 200): Minimal light contribution
- Flickering: Non-repetitive, natural variation
- Specular reflection: Sharp highlights on particles reflecting lava light

### 3.3.3 Rim Lighting (Halo Effect)

**Formula:**

```glsl
float rim = 1.0 - dot(view_dir, norm);
rim = pow(rim, 3.0);
if (h > 70.0) {
    rim_factor = smoothstep(70.0, 95.0, h);
    lighting += rim × rim_factor × rim_color × 0.6;
}
```

**Visual Manifestation:**

- Orange halo around lava crater edges
- Strongest when viewing crater from side (rim perpendicular to camera)
- Creates "backlit" appearance
- Enhances dramatic volcanic look
- Only visible in lava zone (h > 70)

### 3.3.4 Sky Gradient & Atmosphere

**Multi-layer Gradient:**

```
Horizon (0%):    RGB(1.0, 0.8, 0.6)  = Warm orange-yellow
Mid-sky (50%):   RGB(0.4, 0.6, 0.95) = Light blue
Zenith (100%):   RGB(0.15, 0.35, 0.85) = Deep saturated blue
```

**Gradient Transition:**

- Height 0-50%: Smooth interpolation horizon → mid-sky
- Height 50-100%: Smooth interpolation mid-sky → zenith
- Smooth step function mencegah banding artifacts

**Visual Impression:**

- Realistic atmospheric perspective
- Warm horizon consistent dengan sun position
- Cool blue zenith typical dari outdoor sky
- Natural color variation with altitude

### 3.3.5 Cloud Rendering

**Generation Method:** Fractal Brownian Motion (FBM)

```glsl
cloud_noise = fbm(cloud_uv * 3.0);
cloud_pattern = smoothstep(0.3, 0.7, cloud_noise);
```

**Animation:**

```
cloud_uv += time × 0.02  // ~25 pixels/second drift
```

**Cloud Appearance:**

- **Light clouds:** Bright white RGB(1.0, 0.95, 0.9)
- **Shadow regions:** Darker blue-gray RGB(0.5, 0.6, 0.8)
- **Coverage:** 40% of sky (sparse clouds)
- **Movement:** Slow, consistent westward drift

**Visual Effect:**

- Realistic cloud pattern variation
- Non-repetitive due to FBM nature
- Slow movement adds life to sky
- Shadow variations add depth

### 3.3.6 Sun Disk

**Rendering:**

```glsl
sun_dist = distance(TexCoord/10.0, sun_pos);
sun_core = smoothstep(0.12, 0.08, sun_dist);
sun_glow = smoothstep(0.25, 0.1, sun_dist) × 0.6;
sun_color = RGB(1.0, 0.9, 0.5) × (core + glow);
```

**Visual Properties:**

- **Core:** Bright yellow disk ~0.08 units radius
- **Glow:** Larger halo ~0.25 units with 60% brightness
- **Position:** Fixed in sky (0.3, 0.15) relative to sky plane
- **Color:** Warm yellow consistent dengan sun direction

**Visual Impression:**

- Realistic sun appearance (tidak photorealistic, artistic)
- Glow creates atmosphere depth
- Supports directional lighting from shader

### 3.3.7 Fog Effect

**Formula:**
$$F = e^{-(d \times \rho)^2}$$
where $d$ = distance, $\rho$ = 0.003 (density)

**Fog Properties:**

- **Color:** RGB(0.5, 0.6, 0.7) = matches sky mid-color
- **Density:** 0.003 (moderate visibility ~300 units)
- **Type:** Exponential squared (natural perspective)

**Visual Effects:**

- Distant terrain gradually fades into sky color
- No hard fog boundary line
- Far mountains become silhouettes
- Adds sense of scale and depth

---

## Kombinasi Elemen Visual

### 3.4.1 Daytime Appearance

**Complete Scene Composition:**

1. **Ground Layer**
   - Grass-covered plains di base mountain
   - Natural color variation dari grass texture
   - Gentle shadows dari height variation
2. **Mountain Structure**
   - Smooth green lower slopes blending to gray mid-slopes
   - Dark rock faces on steep areas
   - Orange-glowing crater at peak
3. **Eruption Effects**
   - Orange lava arcs shooting from crater (instant attention)
   - Thick white smoke column rising 200+ units
   - Fine ash dispersing horizontally
   - Occasional debris projectiles
4. **Lighting & Atmosphere**
   - Sun-lit terrain with natural shadows
   - Orange glow from lava illuminating nearby rock
   - Warm-to-blue sky gradient
   - Clouds casting subtle shadows
   - Sun disk visible in sky
   - Distant terrain fading into fog
5. **Overall Mood**
   - Dynamic and active (constant eruption)
   - Dramatic (fiery colors, bright contrasts)
   - Natural (realistic physics, organic patterns)
   - Immersive (scale, depth, detail)

### 3.4.2 Time-based Visual Changes

**Eruption Cycle (20-second period):**

**Phase 1: Building Eruption (0-5s)**

- Emission rate increases gradually
- More lava particles launching higher
- Smoke column thickens
- Glow intensity slowly rises

**Phase 2: Peak Eruption (5-10s)**

- Maximum particle count
- Vigorous splashing
- Thick smoke column at peak height
- Brightest glow flickering intensely

**Phase 3: Subsiding (10-15s)**

- Emission rate decreasing
- Smaller arcs, less splashing
- Smoke column thinning
- Glow dimming gradually

**Phase 4: Calm (15-20s)**

- Minimal new particles
- Existing particles settling
- Smoke dispersing upward
- Glow at baseline
- Then cycle repeats

### 3.4.3 Camera Movement Impact on Visuals

**Close-up View (< 30 units)**

- **Terrain:** Individual rock faces visible
- **Particles:** Large particle sprites with clear shape
- **Lighting:** Strong local shadows from particle glow
- **Texture:** High detail visible, tiling becomes apparent

**Mid-range View (30-100 units)**

- **Terrain:** Full mountain structure visible
- **Particles:** Particle streams clearly visible
- **Lighting:** Overall volcanic glow dominates
- **Scale:** Sense of volcanic activity apparent

**Far View (> 100 units)**

- **Terrain:** Full mountain silhouette
- **Eruption:** Complete smoke column visible
- **Lighting:** Sun lighting dominates, glow contributes warmth
- **Fog:** Distance creates atmospheric depth
- **Sky:** Full gradient visible

---

## Summary Keseluruhan Hasil Visual

**Dikembangkan menjadi:**

1. ✓ **Realistic terrain** dengan multi-texture blending mengikuti height & slope
2. ✓ **Dynamic eruption** dengan 4 jenis partikel dan natural physics
3. ✓ **Dramatic lighting** dari dual light sources dengan natural flickering
4. ✓ **Atmospheric depth** dari gradient sky, clouds, fog, dan sun disk
5. ✓ **Immersive environment** yang menggabungkan semua elemen menjadi cohesive scene

**Siap untuk dipresentasikan dalam laporan dengan visual deskripsi lengkap dan technical details.**
