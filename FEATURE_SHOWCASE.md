# 🌋 FEATURE SHOWCASE GUIDE - Tempat Lihat Setiap Fitur

## Saat Program Running (python main.py)

### STARTUP VIEW

Program starts dengan camera focused pada crater area:

```
Camera Position: (80, 110, 80)
Pitch: -20°
View Direction: Ke arah crater gunung
```

---

## ✅ FITUR #1: Texture Quality (FBM Grass, Rock, Lava)

### 🎯 DI MANA LIHAT

**Default View:** Sudah bisa lihat dari startup!

### HOW TO SEE CLEARLY

1. **Press W banyak kali** untuk zoom IN ke mountain base
2. Tunggu sampai camera VERY CLOSE ke terrain (~10-20 units)
3. Lihat bagian bawah mountain yang hijau (grass area)

### 📍 EXPECTED VISUAL

- ✓ Grass texture: Natural pattern dengan organic variation
  - Warna hijau dengan dark/light spots random
  - Tidak smooth/plain seperti simple noise
  - Ada texture detail yang terlihat
- ✓ Rock texture: Cracks dan depth
  - Warna abu-abu dengan crevices
  - Rough surface appearance
  - Detail yang berbeda dari grass

- ✓ Lava texture: Glowing dengan cracks
  - Top crater puncak punya warna orange
  - Dynamic appearance (bukan statis)

### 🔧 JIKA TIDAK TERLIHAT BERBEDA

- **Zoom lebih dekat lagi** (Press W lebih banyak)
- **Camera harus very close** untuk lihat detail texture
- Texture tiling 40× berarti harus dekat untuk see individual pixels

---

## ✅ FITUR #2: Rim Lighting (Orange Halo di Crater Edge)

### 🎯 DI MANA LIHAT

**Crater top area** - particularly di EDGES

### HOW TO SEE CLEARLY

1. **From startup position:** Camera sudah semi-dekat, tapi perlu lihat dari SIDE
2. **Press D** untuk move ke kanan
3. **Hold mouse + drag UP** untuk tilt camera angle sampai melihat crater dari side
4. Lihat tepi crater (rim) yang menghadap AWAY dari sun

### 📍 EXPECTED VISUAL

- ✓ Orange/reddish HALO di around crater edge
- ✓ Terang di areas yang rim-facing (silhouette-like)
- ✓ Pulsing slowly (dim → bright → dim) dalam 3 detik
- ✓ Effect strongest di crater walls

### 🔧 JIKA TIDAK TERLIHAT

- **Check camera angle:** Must be side-view, bukan top-down
- **Check distance:** Harus cukup dekat (< 100 units)
- **Wait for pulsing:** Effect tidak static, tunggu 3-5 detik untuk lihat variation
- **Lihat area orange glow:** Bukan di center crater, tapi di EDGES

---

## ✅ FITUR #3: Dynamic Light Flickering (Lava Glow Pulse)

### 🎯 DI MANA LIHAT

**Crater center** - watch the orange light intensity

### HOW TO SEE CLEARLY

1. **From current position, press W** untuk move CLOSER ke crater
2. Camera should be ~30-50 units away from crater center
3. Look at the TOP of crater (lava surface area)
4. Watch untuk perubahan brightness dalam cahaya oranye

### 📍 EXPECTED VISUAL

- ✓ Orange glow intensity CHANGES SMOOTHLY (tidak like on/off)
- ✓ Pattern: Bright → Dim → Bright (dalam ~2-3 detik per cycle)
- ✓ NOT repetitive (perubahan frequency berbeda-beda karena multiple sine waves)
- ✓ Surrounding terrain di-illuminate oleh light ini

### 🔧 JIKA TIDAK TERLIHAT

- **Duration:** Watch for 10+ detik, jangan hanya 1-2 detik
- **Distance:** Harus dekat cukup untuk see light influence
- **Lighting:** Flicker subtle, bukan dramatic flash
- **Check if static:** Jika perfectly constant, shader mungkin tidak execute flickering

---

## ✅ FITUR #4: Sky Gradient & Clouds & Sun Disk

### 🎯 DI MANA LIHAT

**SKY** - melihat ke atas

### HOW TO SEE CLEARLY

1. **Hold Mouse + drag UP** untuk tilt camera ke atas (look up)
2. OR **Press Space** (jika implemented) untuk instant look up
3. Lihat background di atas mountain

### 📍 EXPECTED VISUAL

- ✓ Sky color gradient:
  - Bottom (horizon): Warm orange/yellow (RGB ~1.0, 0.8, 0.6)
  - Middle: Light blue
  - Top (zenith): Deep blue (RGB ~0.15, 0.35, 0.85)
- ✓ Cloud patterns:
  - Fluffy white clouds dengan shadows
  - Moving SLOWLY (drift west direction)
  - Changes pattern naturally (FBM pattern)
- ✓ Sun disk:
  - Yellow bright disk (somewhere in sky)
  - WITH glow halo around it
  - Positioned consistently

### 🔧 JIKA TIDAK TERLIHAT

- **Must look UP:** Gradient hanya visible saat lihat atas
- **Default view lihat mountain:** Sky hanya background kecil
- **Cloud animation:** Bergerak sangat pelan (~few pixels/sec)
- **Sun position:** Fixed di sky, cari yellow disk

---

## ✅ FITUR #5: Particle Physics (Eruption Effects)

### 🎯 DI MANA LIHAT

**CRATER AREA** - watch lava particles

### HOW TO SEE CLEARLY

1. **Look at crater center bottom** (lava pool area)
2. Watch orange particles (lava) yang:
   - Shooting up dari crater
   - Falling down in arcs
   - **BOUNCING** saat hit crater floor
3. Watch gray particles (smoke):
   - Rising up smoothly
   - Swirling/twisting (tidak straight up)
   - Growing larger saat naik

### 📍 EXPECTED VISUAL

- ✓ **Lava particles (orange):**
  - Launch dari center ~30-40 units height
  - Visible orange arcs
  - **BOUNCE multiple times** (decreasing height)
  - Splash effect saat impact
- ✓ **Smoke particles (gray):**
  - Rise much higher (100+ units)
  - Twist motion (counterclockwise spiral)
  - Disappear at top
- ✓ **Ash particles (brown):**
  - Intermediate height
  - Spread outward more
- ✓ **Debris (dark):**
  - Horizontal projectiles
  - Fast motion
  - Short lifetime

### 🔧 JIKA TIDAK TERLIHAT JELAS

- **Zoom in very close** untuk lihat particle details
- **Focus pada crater center** untuk see bouncing
- **Wait for eruption cycles:** Intensity varies (20-second main cycle)
  - Sometimes less particles (calm phase)
  - Sometimes more particles (peak phase)

---

## 📋 COMPREHENSIVE CAMERA MOVEMENT GUIDE

### Standard View Navigation

```
W    → Move forward
A    → Move left
S    → Move backward
D    → Move right
Mouse Drag → Look around (rotate camera)
ESC  → Quit
```

### RECOMMENDED EXPLORATION SEQUENCE

**Phase 1: Texture Detail (3 minutes)**

- Press W repeatedly to zoom IN to grass base
- Walk around mountain perimeter
- See detail variation in textures

**Phase 2: Crater Glow (2 minutes)**

- From zoom-in position, press W few more times
- Move closer to crater (20-30 units away)
- Use mouse to look from different angles (side, bottom)
- Watch rim lighting pulsing

**Phase 3: Flicker Intensity (2 minutes)**

- Stay close to crater
- Watch orange glow brightness change
- Observe for 10+ seconds untuk see non-repetitive pattern

**Phase 4: Sky Features (2 minutes)**

- Move away from crater (press S multiple times)
- Look UP with mouse (drag up)
- Observe sky gradient, clouds, sun

**Phase 5: Particle Behavior (3 minutes)**

- Return close to crater
- Focus pada particles
- Watch bouncing, swirling, and dispersal patterns
- Observe eruption cycle variations

**Total observation time: ~12 minutes untuk lihat semua features**

---

## 🎯 QUICK SANITY CHECKS

### ✓ Program berjalan lancar

```
[1/5] Menghasilkan tekstur prosedural... ← DONE
[2/5] Inisialisasi Window...             ← DONE
[3/5] Kompilasi Shader...                ← DONE
[4/5] Membangun procedural terrain...    ← DONE
[5/5] Inisialisasi sistem dinamik...     ← DONE
--- SIMULASI BERJALAN ---                ← SUCCESS
```

### ✓ Textures ter-load

```
✓ Grass texture loaded
✓ Rock texture loaded
✓ Lava texture loaded
```

### ✓ Visual elements visible

```
- Mountain visible dengan color blending
- Orange glow di crater area
- White smoke column naik
- Sky gradient background
- Particles bouncing/swirling
```

---

## ⚠️ TROUBLESHOOTING

### Problem: "Texture masih terlihat sama seperti sebelum enhancement"

**Solution:**

1. **Must zoom IN very close** untuk lihat texture detail
   - Default view: texture terjadi scaled down, detail tidak visible
   - Solution: Press W banyak kali sampai very close
2. **FBM pattern beda dari noise pattern**
   - Old: Simple 4-octave noise (flat-ish)
   - New: 6-8 octave FBM (more complex organic pattern)
   - Need close inspection untuk see difference
3. **Check texture file sizes**
   ```
   grass.png: 254 KB (✓ correct - FBM generated)
   rock.png:  409 KB (✓ correct - largest due to 8 octaves)
   lava.png:  314 KB (✓ correct - with crack pattern)
   ```

### Problem: "Rim lighting tidak terlihat"

**Solution:**

1. **Must view dari SIDE** (tidak top-down)
2. **Harus close cukup** (< 100 units)
3. **Check lighting math:**
   ```glsl
   if (h > 70.0) {  // Only in lava zone
       rim = 1.0 - dot(view_dir, norm);  // Rim effect
       rim = pow(rim, 3.0);
   }
   ```
4. **Effect pulsing:** NOT constant, wait 3+ seconds

### Problem: "Flicker tidak terlihat atau terlalu subtle"

**Solution:**

1. **Watch lava light influence** (tidak just crater surface)
2. **Observe 10+ seconds** untuk notice variation
3. **Standing position matters:** Close to crater untuk strong effect
4. **Flicker formula:**
   ```glsl
   flicker = 0.7 + 0.3*sin(4t) + 0.15*sin(2.7t)
   ```
   Multiple frequencies → non-repetitive pattern

### Problem: "Sky masih terlihat sama"

**Solution:**

1. **MUST look UP** - default view shows mountain foreground
2. **Sky di background:** Small portion jika look forward
3. **Tilt camera dengan mouse** untuk see full sky
4. **Cloud drift very slow:** Perlu watch 30+ seconds untuk see movement

---

## 📸 WHAT YOU SHOULD SEE (Description)

### Screenshot 1: Crater Closeup (Rim Lighting + Flicker)

```
- Orange glowing crater center
- Brighter edges (rim lighting)
- Pulsing intensity (darker/brighter cycles)
- Surrounding rock illuminated by warm light
```

### Screenshot 2: Texture Detail (Zoom In)

```
- Grass: Organic pattern, natural color variation
- Rock: Cracks, weathered appearance
- Clear difference dari old simple noise textures
```

### Screenshot 3: Sky View (Looking Up)

```
- Gradient from orange (horizon) to blue (top)
- Cloud patterns dengan shadows
- Yellow sun disk somewhere in sky
```

### Screenshot 4: Full Eruption (Mid-Distance)

```
- Smoke column rising tall
- Orange particles launching
- Particles bouncing dalam crater
- Orange glow illuminating terrain
```

---

## 🎓 UNDERSTANDING THE IMPROVEMENTS

### Texture (FBM vs Simple Noise)

| Aspect       | Simple Noise | FBM                  |
| ------------ | ------------ | -------------------- |
| Octaves      | 4            | 6-8                  |
| Pattern      | Uniform      | Organic, multi-scale |
| Detail       | Low          | High                 |
| Natural Look | Fair         | Excellent            |

### Lighting (New Features)

- **Before:** Basic Blinn-Phong + fog
- **After:** + Rim lighting + dynamic flicker + specular

### Particles (Physics)

- **Before:** Simple gravity + bounce
- **After:** + Air resistance + splash + buoyancy + turbulence

### Sky (Atmosphere)

- **Before:** Simple gradient
- **After:** + FBM clouds + sun disk + tone mapping

---

## ✨ FINAL TIPS

1. **Take your time exploring** - 15 minutes recommended untuk full appreciation
2. **Different angles reveal different things** - walk around mountain
3. **Watch for subtle changes** - some effects are not dramatic but visible
4. **Eruption cycles vary** - wait for intensity peaks untuk see fulleffect
5. **Close observation needed** - zoom in untuk texture, close-up untuk glow

**Now run: `python main.py` and explore!**

🌋✨
