import os
import numpy as np
from PIL import Image
import moderngl

from core.window import Window
from core.camera import Camera
from terrain.generator import TerrainGenerator
from terrain.mesh import TerrainMesh
from rendering.renderer import Renderer
from particle.system import ParticleSystem
from particle.emitter import VolcanoEmitter
from effects.lighting import LightingConfig

from noise import pnoise2

def create_procedural_textures():
    """Membuat tekstur sederhana (Grass, Rock, Lava) secara prosedural menggunakan Numpy dan Pillow."""
    os.makedirs('assets/textures', exist_ok=True)
    
    # Fungsi bantu untuk generate noise map
    def generate_noise_texture(size, base_color, noise_color, scale=10.0, octaves=4):
        arr = np.zeros((size, size, 3), dtype=np.uint8)
        for i in range(size):
            for j in range(size):
                n = pnoise2(i / scale, j / scale, octaves=octaves)
                n = (n + 1.0) / 2.0  # normalize 0 to 1
                r = int(base_color[0] * (1-n) + noise_color[0] * n)
                g = int(base_color[1] * (1-n) + noise_color[1] * n)
                b = int(base_color[2] * (1-n) + noise_color[2] * n)
                arr[i, j] = [min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))]
        return arr

    if not os.path.exists('assets/textures/grass.png'):
        arr = generate_noise_texture(256, [34, 139, 34], [85, 107, 47], scale=20.0)
        Image.fromarray(arr).save('assets/textures/grass.png')
        
    if not os.path.exists('assets/textures/rock.png'):
        arr = generate_noise_texture(256, [105, 105, 105], [169, 169, 169], scale=15.0)
        Image.fromarray(arr).save('assets/textures/rock.png')
        
    if not os.path.exists('assets/textures/lava.png'):
        # Lava with orange/red fiery noise
        arr = generate_noise_texture(256, [255, 69, 0], [255, 140, 0], scale=10.0)
        Image.fromarray(arr).save('assets/textures/lava.png')

def load_texture(ctx, path):
    """Membaca file gambar dan mengirimkannya sebagai tekstur 2D ke memori GPU."""
    img = Image.open(path).convert('RGB')
    texture = ctx.texture(img.size, 3, img.tobytes())
    texture.build_mipmaps()
    # Linear filtering agar tekstur halus saat diperbesar/diperkecil
    texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    return texture

def main():
    # 1. Setup Resource/Tekstur
    print("[1/5] Menghasilkan tekstur prosedural...")
    create_procedural_textures()

    # 2. Inisialisasi Window dan Konteks ModernGL
    print("[2/5] Inisialisasi Window...")
    win = Window(1280, 720, "3D Volcano Eruption Simulation")
    
    # Izinkan shader mengatur ukuran titik partikel (gl_PointSize)
    win.ctx.enable(moderngl.PROGRAM_POINT_SIZE)
    
    # 3. Setup Shaders dan Rendering Pipeline
    print("[3/5] Kompilasi Shader...")
    renderer = Renderer(win.ctx)
    renderer.init_shaders()
    
    # 4. Generate Terrain
    print("[4/5] Membangun procedural terrain (Perlin Noise)...")
    t_gen = TerrainGenerator(size=200, scale=1.0)
    t_gen.generate()
    vertices, indices = t_gen.get_vertex_data()
    terrain_mesh = TerrainMesh(win.ctx, renderer.terrain_shader.program, vertices, indices)
    
    # Load Texture ke GPU
    tex_grass = load_texture(win.ctx, 'assets/textures/grass.png')
    tex_rock = load_texture(win.ctx, 'assets/textures/rock.png')
    tex_lava = load_texture(win.ctx, 'assets/textures/lava.png')
    
    # Assign texture unit ke variabel uniform shader
    renderer.terrain_shader.program['tex_grass'].value = 0
    renderer.terrain_shader.program['tex_rock'].value = 1
    renderer.terrain_shader.program['tex_lava'].value = 2
    
    # 5. Setup Sistem Animasi (Partikel, Kamera, Lighting)
    print("[5/5] Inisialisasi sistem dinamik...")
    p_system = ParticleSystem(win.ctx, renderer.particle_shader.program, max_particles=5000)
    emitter = VolcanoEmitter(p_system, center=(0.0, 100.0, 0.0))
    camera = Camera(position=(0.0, 100.0, 150.0), pitch=-15.0)
    light_cfg = LightingConfig()
    
    last_time = win.get_time()
    
    print("\n--- SIMULASI BERJALAN ---")
    print("Gunakan WASD untuk bergerak dan Mouse untuk mengubah arah pandang.")
    print("Tekan ESC untuk keluar.")
    
    # --- MAIN LOOP ---
    while win.is_running():
        # Menghitung delta time (waktu antar frame)
        current_time = win.get_time()
        dt = current_time - last_time
        last_time = current_time
        
        # Poll input event
        win.poll_events()
        
        # Update logic Kamera (dengan collision detection)
        camera.process_keyboard(win.keys, dt, t_gen)
        if win.mouse_dx != 0.0 or win.mouse_dy != 0.0:
            camera.process_mouse(win.mouse_dx, win.mouse_dy)
            
        # Update Animasi
        emitter.update(dt)
        p_system.update(dt)
        
        # Render Frame
        # Warna background disamakan dengan warna kabut (fog)
        win.ctx.clear(0.5, 0.6, 0.7) 
        
        # Bind tekstur ke slot masing-masing
        tex_grass.use(location=0)
        tex_rock.use(location=1)
        tex_lava.use(location=2)
        
        # Render Terrain, Langit & Partikel
        renderer.render_sky(camera, current_time)
        renderer.render_terrain(terrain_mesh, camera, light_cfg.lava_pos, current_time)
        renderer.render_particles(p_system, camera)
        
        # Swap Double Buffer
        win.swap_buffers()
        
    win.terminate()

if __name__ == '__main__':
    main()
