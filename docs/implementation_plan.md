# Implementation Plan: 3D Volcano Simulation

This document outlines the step-by-step implementation plan for the 3D Volcano Simulation project using Python, PyOpenGL, and GLFW.

## Phase 1: Project Setup & Initialization
**Objective**: Set up the environment, project structure, and the main GLFW window with an active OpenGL context.

- [ ] **1.1. Create Project Structure**: Create the required directories as defined in the PRD (`core/`, `terrain/`, `particle/`, `renderer/`, `effects/`, `shaders/`).
- [ ] **1.2. Define Dependencies**: Create `requirements.txt` with `PyOpenGL`, `glfw`, `numpy`, `PyGLM`, and `noise` (if using Perlin/Simplex noise) or implement custom noise.
- [ ] **1.3. Window Management**: Implement `main.py` to initialize GLFW, create a window, set up the OpenGL context with depth testing, and establish the main render loop.

## Phase 2: Core Engine Components
**Objective**: Implement the fundamental modules needed for 3D rendering (Camera, Shaders, Mesh abstraction).

- [ ] **2.1. Shader Compiler (`core/shader.py`)**: Create a class to load, compile, and link Vertex and Fragment shaders, and handle uniform variable updates.
- [ ] **2.2. FPS Camera (`core/camera.py`)**: Implement an FPS camera using PyGLM. It should handle view matrix calculation, projection matrix, WASD keyboard movement, mouse look (yaw/pitch), and a reset function (Press 'R').
- [ ] **2.3. Mesh Renderer (`renderer/mesh.py`)**: Create an abstraction for OpenGL VAO, VBO, and EBO to easily render terrain arrays (vertices, normals, colors, indices) without repetitive boilerplate.

## Phase 3: Procedural Terrain Generation
**Objective**: Generate the 3D mesh of the volcano with a crater and color it based on elevation.

- [ ] **3.1. Terrain Shaders (`shaders/terrain.vert`, `shaders/terrain.frag`)**: Write basic shaders to pass vertex positions, normals, and colors to the screen.
- [ ] **3.2. Volcano Mesh Generation (`terrain/volcano.py`)**: 
    - Create a 2D grid using NumPy.
    - Apply mathematical functions (e.g., a cone function combined with distance-based exponential decay) to form a mountain.
    - Create a crater at the peak by modifying the height equation near the center.
    - Add noise to the heightmap for a realistic rocky look.
    - Calculate surface normals for lighting.
- [ ] **3.3. Terrain Coloring**: Determine vertex colors based on height and slope (e.g., green for base, brown for mid, gray/rocky for top, glowing red/orange for the crater base).

## Phase 4: Eruption Particle System
**Objective**: Create a visual eruption effect using instanced rendering or dynamic buffers for hundreds of particles.

- [ ] **4.1. Particle Shaders (`shaders/particle.vert`, `shaders/particle.frag`)**: Write shaders for rendering points or simple quads for particles.
- [ ] **4.2. Particle Data Structure (`particle/particle.py`)**: Define the properties of a particle (position, velocity, life, decay rate, color, type).
- [ ] **4.3. Particle System Manager (`particle/system.py`)**: 
    - Manage a pool of 200+ particles.
    - Spawn logic: Eject particles from the crater coordinate.
    - Update logic: Apply gravity to "batu", upward velocity + dispersion for "asap", and parabolic motion for "lava". Update lifetime and fade alpha.
    - Render logic: Update OpenGL buffers with new particle positions and draw them.

## Phase 5: Lighting & Effects
**Objective**: Implement realistic lighting, day/night cycles, and distance fog.

- [ ] **5.1. Directional & Point Lights (`effects/lighting.py` & Shaders)**: 
    - Implement a directional light (sun/moon) in the terrain fragment shader (ambient + diffuse).
    - Implement a point light located at the crater with a reddish hue.
    - Add a flicker effect to the point light by modifying its intensity over time (using `sin` or random noise).
- [ ] **5.2. Fog Effect (`effects/fog.py` & Shaders)**: 
    - Calculate distance from the camera to the fragment.
    - Mix the final fragment color with the fog color based on this distance (exponential or linear falloff).
- [ ] **5.3. Day/Night Cycle**: Add logic in `main.py` to toggle between day and night mode. Adjust directional light direction, color, ambient strength, and sky clear color accordingly.

## Phase 6: Integration, Polish & Submission
**Objective**: Wire all components, ensure 30+ FPS, and document code.

- [ ] **6.1. Main Loop Integration**: Ensure `main.py` updates the camera, particle system, and renders the terrain and particles in the correct order (terrain first, then transparent particles without depth writing).
- [ ] **6.2. Interaction & Controls**: Bind input callbacks for camera, Day/Night toggle, and resetting.
- [ ] **6.3. Optimization & Testing**: Check FPS, optimize NumPy mesh generation (precalculate if possible), and ensure particle updates are efficient.
- [ ] **6.4. Code Comments**: Review all modules and add comments explaining the graphics concepts (e.g., "Calculating view matrix", "Applying diffuse lighting") as requested.

Viewed requirements.txt:1-7
Viewed camera.py:1-110

Tentu saja, proyek ini menggunakan konsep **Transformasi Matriks** dan **Koreografi Grafika 3D** secara mendalam. Tanpa ini, kita tidak akan bisa melihat kedalaman (3D) di layar 2D.

Berikut adalah beberapa bagian di mana transformasi tersebut terjadi:

### 1. Transformasi Rotasi (Kamera)
Di dalam file `core/camera.py`, setiap kali Anda menggerakkan mouse, terjadi **Rotasi Euler**:
*   **Yaw (Rotasi Horizontal)** dan **Pitch (Rotasi Vertikal)** dihitung menggunakan fungsi trigonometri (`cos` dan `sin`) untuk menentukan arah pandang kamera (`Front`, `Right`, `Up`).
*   Lihat fungsi `update_vectors()` di baris 24-41.

### 2. Transformasi View & Projection (Matriks 4x4)
Ini adalah "jantung" dari grafika 3D:
*   **View Matrix**: Menggunakan operasi **Look-At** (baris 82-95) untuk mengubah koordinat dunia menjadi koordinat kamera. Ini secara teknis adalah kombinasi dari **Translasi** (posisi kamera) dan **Rotasi** (arah pandang).
*   **Projection Matrix**: Menggunakan **Perspective Projection** (baris 97-109) untuk menciptakan efek perspektif, di mana benda yang jauh terlihat lebih kecil daripada benda yang dekat.

### 3. Transformasi Translasi (Partikel)
Sistem partikel di `particle/system.py` menggunakan **Translasi** untuk menggerakkan partikel setiap detiknya:
*   `p['pos'] += p['vel'] * dt`
*   Ini adalah transformasi posisi titik berdasarkan vektor kecepatan.

### 4. Transformasi di Shader (Vertex Shader)
Jika Anda melihat file di folder `shaders/`, setiap titik (*vertex*) diproses menggunakan perkalian matriks standar industri:
```glsl
gl_Position = projection * view * model * vec4(in_position, 1.0);
```
*   **Model**: Mengatur posisi/skala objek di dunia.
*   **View**: Mengatur sudut pandang kamera.
*   **Projection**: Mengatur efek lensa kamera.

**Kesimpulannya**: Proyek ini adalah implementasi nyata dari matematika matriks. Anda bisa menyebutkan bahwa proyek ini menggunakan **Model-View-Projection (MVP) Matrix Pipeline** untuk menghasilkan visualisasi 3D yang akurat.