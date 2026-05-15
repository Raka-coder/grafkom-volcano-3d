# Quick Start Guide - Menjalankan Volcano 3D dengan Fitur Baru

## Persyaratan

- **Python:** 3.10 atau lebih baru
- **OpenGL:** 3.3 atau lebih baru
- **Kartu Grafis:** Mendukung vertex/fragment shaders

## Instalasi Dependencies

```bash
# Buat virtual environment (optional tapi disarankan)
python -m venv venv

# Windows - activate venv
venv\Scripts\activate

# Linux/macOS - activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Packages yang diinstall:**

- `moderngl` - OpenGL wrapper
- `glfw` - Window & input management
- `numpy` - Matrix math
- `pillow` - Image processing
- `noise` - Perlin noise generation

## Running the Simulation

```bash
python main.py
```

**First Run:**

- Aplikasi akan generate texture files ke `assets/textures/`
  - `grass.png` (512×512) - ~5 detik
  - `rock.png` (512×512) - ~5 detik
  - `lava.png` (512×512) - ~5 detik

Proses generation ini hanya sekali. Run berikutnya akan instant.

## Controls

| Key       | Action                    |
| --------- | ------------------------- |
| **W**     | Move forward              |
| **A**     | Move left                 |
| **S**     | Move backward             |
| **D**     | Move right                |
| **Mouse** | Look around (free camera) |
| **ESC**   | Exit                      |

## Expected Visual Output

### Immediate Startup

1. ✓ Gunung berapi prosedural dengan tekstur blending
2. ✓ Kawah di puncak dengan orange glow
3. ✓ Langit gradient biru-oranye
4. ✓ Particle eruption dengan smoke column

### Camera Movement

- Zoom in ke crater untuk melihat lava glow detail
- Pan around untuk melihat texture variation di slopes
- Look up untuk cloud animation di sky

### Dynamic Features (Berjalan terus)

- Partikel smoke terus naik
- Lava particles bounce di crater floor
- Glow intensity flicker natural
- Cloud patterns drift slowly

## Troubleshooting

### Issue: "No module named 'moderngl'"

```bash
# Solution: pip install moderngl
pip install --upgrade moderngl glfw
```

### Issue: Textures tidak generate

```
- Check folder: assets/textures/ exists
- Solution: Manual creation
  mkdir assets/textures
  python main.py
```

### Issue: Crash dengan OpenGL error

```
- Requirement: OpenGL 3.3+ support
- Check GPU: Download GPU-Z, verify OpenGL version
- Fallback: Update graphics drivers
```

### Issue: Particles muncul di random places

```
- Normal behavior dalam 1-2 frame pertama
- Emitter center reset di frame 2
- Watch smoke column naik stabil
```

### Issue: Low FPS / Performance lag

```
- Reduce emission rate: particle/emitter.py line ~24
  self.base_emit_rate = 200  # from 350
- Reduce terrain resolution: terrain/generator.py line ~16
  size=200  # from 400
- Reduce max particles: particle/system.py line ~15
  max_particles=2000  # from 5000
```

## Verifying Features Are Working

### Feature 1: Terrain Texture Blending ✓

- **Check:** Zoom out view untuk melihat full mountain
- **Expect:**
  - Bottom (green): Grass texture
  - Middle (gray): Rock texture
  - Top (orange): Lava glow area
  - Cliffs: Darker rock showing slope-based blending

### Feature 2: Particle Physics ✓

- **Check:** Watch lava particles
- **Expect:**
  - Orange particles shoot up
  - Arc downward due to gravity
  - Hit crater floor: bounce & splatter
  - Secondary bounces: smaller each time
  - Smoke particles: rise steadily, twist/swirl
  - Debris: fast horizontal trajectories

### Feature 3: Dynamic Lighting ✓

- **Check:** Watch lava crater glow over time
- **Expect:**
  - Orange glow flickers naturally
  - Not robotic/repetitive pattern
  - Illuminates surrounding terrain
  - Stronger glow when eruption intensity peaks

### Feature 4: Sky & Fog ✓

- **Check:** Walk away from mountain (press D many times)
- **Expect:**
  - Distant terrain fades into fog
  - Sky gradient visible (blue zenith, orange horizon)
  - Clouds move slowly
  - Sun disk visible in sky

## Configuration (Optional Tweaks)

### Texture Quality

Edit `main.py`, `create_procedural_textures()`:

```python
arr = generate_fbm_texture(
    512,  # Change to 256 for faster generation, 1024 for higher quality
    ...
    layers=7,  # More layers = more detail (slower generation)
    persistence=0.55,
)
```

### Emission Rate

Edit `particle/emitter.py`:

```python
self.base_emit_rate = 350  # Particles per second
# Increase untuk lebih banyak particles, decrease untuk performance
```

### Lighting Intensity

Edit `shaders/terrain.frag`:

```glsl
lighting += spec_lava * 0.4 * lava_light * ...
// Change 0.4 untuk stronger/weaker specular dari lava light
```

### Fog Density

Edit `shaders/terrain.frag`:

```glsl
uniform float fog_density = 0.003;
// Decrease untuk melihat lebih jauh, increase untuk thicker fog
```

## Physics Tuning

### Lava Bounce Height

Edit `particle/system.py`:

```python
p['vel'][1] = abs(p['vel'][1]) * 0.35 + bounce_energy * 0.2
# First number (0.35): bounce coefficient
# Higher = bounces lebih tinggi
```

### Smoke Rise Speed

Edit `particle/system.py`:

```python
buoyancy = np.array([0.0, 25.0, 0.0])  # Y component
# Increase untuk smoke naik lebih cepat
```

### Air Resistance

Edit `particle/system.py`:

```python
p['vel'] *= drag_coeff  # drag_coeff = 0.98
# Higher (0.99) = particles travel farther
# Lower (0.95) = particles slow down quickly
```

## Performance Tips

1. **Reduce particle count:**
   - `particle/system.py`: max_particles = 2000
   - `particle/emitter.py`: base_emit_rate = 200

2. **Reduce terrain quality:**
   - `terrain/generator.py`: size = 200 (from 400)
   - Results in faster heightmap generation

3. **Lower texture resolution:**
   - `main.py`: 256x256 instead of 512x512
   - Faster texture generation, same visual quality at distance

4. **Disable fancy math:**
   - Remove rim lighting dari terrain.frag untuk simpler shader
   - Remove cloud animation dari sky.frag

## Expected Performance

| Hardware                  | FPS   | Max Particles |
| ------------------------- | ----- | ------------- |
| Integrated GPU (2019+)    | 30-45 | 2000          |
| Mid-range GPU (GTX 1050+) | 60+   | 5000          |
| High-end GPU (RTX 2060+)  | 144+  | 5000+         |

Settings diatas mengasumsikan:

- Terrain: 400×400
- Textures: 512×512
- Emission: 350 particles/second

---

## Next Steps untuk Development

### Potential Enhancements

1. **Normal Mapping:** Terrain.frag menggunakan normal map untuk extra detail
2. **Shadow Mapping:** Real-time shadows dari lava light
3. **Weather:** Rain/snow particles integrated dengan eruption
4. **Skybox Cubemap:** 6-sided environment mapping instead of plane
5. **Mesh Deformation:** Crater shape changes during eruption cycle
6. **Audio:** Eruption sound effects synchronized dengan intensity

### Code Structure Maintenance

- Keep shader files organized dalam `shaders/` folder
- Document any custom constants (crater height 102, etc.)
- Test performance scaling dengan larger terrains
- Consider CUDA/compute shaders untuk massive particle count
