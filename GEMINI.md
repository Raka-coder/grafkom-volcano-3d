# Volcano ModernGL Project Context

This project is a **Realistic 3D Volcano Eruption Simulation** built using Python and the **ModernGL** library (an OpenGL wrapper). It simulates a procedural volcanic landscape with dynamic eruption effects, atmospheric lighting, and a first-person exploration camera.

## 🚀 Project Overview

The simulation aims to deliver a visually engaging 3D environment featuring:
- **Procedural Terrain:** Generated using Perlin noise to create a realistic mountain and crater.
- **Dynamic Eruption:** A GPU-friendly particle system simulating lava, smoke, and debris.
- **Advanced Rendering:** Modern shader-based pipeline (GLSL) implementing Blinn-Phong lighting and exponential fog.
- **Interactive Exploration:** FPS-style camera for free navigation within the scene.

## 🛠️ Technology Stack

- **Language:** Python 3.10+
- **Graphics API:** ModernGL (targeting OpenGL 3.3 Core Profile)
- **Windowing & Input:** GLFW
- **Mathematics:** NumPy, PyGLM
- **Image Processing:** Pillow (for texture loading and procedural generation)
- **Noise:** Custom Perlin noise implementation (`noise.py`)

## 📂 Project Structure

- `main.py`: The main entry point. Handles resource initialization, the main loop, and component orchestration.
- `core/`:
  - `window.py`: GLFW window management and ModernGL context setup.
  - `camera.py`: First-person perspective camera with WASD and mouse controls.
- `terrain/`:
  - `generator.py`: Logic for heightmap generation using Perlin noise.
  - `mesh.py`: Abstraction for terrain VBO/VAO management.
- `particle/`:
  - `system.py`: Manages particle buffers and update logic on the GPU/CPU.
  - `emitter.py`: Logic for spawning particles from the volcano's crater.
- `rendering/`:
  - `shader.py`: Shader loading and uniform management.
  - `renderer.py`: High-level rendering calls for terrain, particles, and sky.
- `effects/`:
  - `lighting.py`: Configuration for sun and lava point lights.
  - `fog.py`: Atmospheric fog parameters.
- `shaders/`: GLSL source files for terrain, particles, and sky.
- `assets/`: Procedurally generated and static textures.

## 🏃 Building and Running

### Prerequisites
Ensure you have Python 3.10+ installed.

### Installation
Install the required dependencies using pip:
```bash
pip install -r requirements.txt
```

### Running the Simulation
Execute the main script:
```bash
python main.py
```

### Controls
- **WASD:** Move the camera.
- **Mouse:** Look around (pitch and yaw).
- **ESC:** Exit the simulation.

## 📜 Development Conventions

1. **Modular Architecture:** Keep logic separated into specialized directories (e.g., terrain logic in `terrain/`).
2. **Shader-Based:** All rendering should happen through ModernGL programs and GLSL shaders.
3. **Data Handling:** Use NumPy for efficient mesh and particle data manipulation.
4. **Procedural First:** Prefer procedural generation for textures and terrain to keep the repository lightweight.
5. **Documentation:** Refer to `docs/PRD.md` and `docs/implementation_plan.md` for architectural goals and roadmaps.

## 🧪 Testing

Currently, testing is performed manually by running `main.py` and verifying:
- **FPS Performance:** Target ≥ 30 FPS.
- **Visual Correctness:** Terrain blending, lighting highlights, and particle behavior.
- **Input Responsiveness:** Smooth camera movement and mouse look.
