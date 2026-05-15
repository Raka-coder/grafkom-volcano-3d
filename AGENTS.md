# AGENTS.md — volcano-moderngl

## Quick start
```
python -m venv venv && venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```
Requires Python 3.10+ and OpenGL 3.3+ GPU.

## Entrypoints
- `main.py` — app entrypoint
- `test_features.py` — non-functional print-only script (not a test suite; no test framework exists)

## Architecture
| Directory | Purpose |
|-----------|---------|
| `core/` | GLFW window + FPS camera |
| `terrain/` | Perlin-noise heightmap generator + mesh builder |
| `rendering/` | `Renderer` (orchestrates shaders/mesh) + `ShaderProgram` (loads GLSL) |
| `particle/` | GPU-friendly particle system + volcano emitter |
| `effects/` | `LightingConfig` (sun+lava glow+fog) |
| `objects/` | Procedural 3D objects (PineTree, Rock, GrassPatch) |
| `shaders/` | GLSL vertex/fragment shaders (terrain, particle, sky, object) |
| `noise.py` | **Local** pure-Python Perlin noise — shadows PyPI `noise` package |

All `__init__.py` files are empty. No CI/CD, no linter, no formatter, no type checker.

## Key quirks
- **Local `noise.py` overrides PyPI `noise`**: The `import noise` in source files resolves to the local module at `noise.py`, not the pip package. The local module exports `pnoise2` and `pnoise3`.
- **Textures are procedural + cached**: Generated at first run into `assets/textures/*.png` (512×512). Delete those files to force regeneration. They are `.gitignore`-d.
- **Matrix transposition**: All matrices are transposed to column-major (OpenGL convention) at render time via `.astype('f4').T.tobytes()`.
- **Mouse delta reset**: `Window.poll_events()` zeros `mouse_dx`/`mouse_dy` before calling `glfw.poll_events()`. Deltas are only valid between successive `poll_events()` calls.
- **Default camera**: position=(80, 110, 80), pitch=-20, speed=50, sens=0.1.
- **Controls**: WASD move, mouse look, ESC quit.

## Dependencies
`ModernGL`, `glfw`, `numpy`, `Pillow`, `noise` (PyPI, but effectively unused — local `noise.py` is what runs).

## Performance notes
- 8000 max particles, 512×512 textures, 400×400 terrain grid (~160K vertices).
- ~115 scene objects (trees) each with own VAO.
- Single GLFW event loop thread.
