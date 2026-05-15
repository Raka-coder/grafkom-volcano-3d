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
    """
    Membuat tekstur berkualitas tinggi (Grass, Rock, Lava) menggunakan FBM (Fractional Brownian Motion)
    dan multi-layer noise untuk detail yang lebih realistis.
    """
    os.makedirs('assets/textures', exist_ok=True)
    
    def generate_fbm_texture(size, base_color, detail_color, scale=10.0, layers=6, persistence=0.5):
        """Generate FBM noise untuk tekstur yang lebih detail dan natural"""
        arr = np.zeros((size, size, 3), dtype=np.uint8)
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        for i in range(size):
            for j in range(size):
                # FBM: Superpose multiple noise octaves dengan decreasing amplitude
                value = 0.0
                temp_amplitude = 1.0
                temp_frequency = 1.0
                for _ in range(layers):
                    n = pnoise2(
                        i / scale * temp_frequency,
                        j / scale * temp_frequency,
                        octaves=3,
                        persistence=persistence
                    )
                    value += n * temp_amplitude
                    temp_amplitude *= persistence
                    temp_frequency *= 2.0
                
                # Normalize value to 0-1
                n = (value / (2.0 - persistence)) + 0.5
                n = max(0.0, min(1.0, n))
                
                # Mix base color with detail color
                r = int(base_color[0] * (1-n) + detail_color[0] * n)
                g = int(base_color[1] * (1-n) + detail_color[1] * n)
                b = int(base_color[2] * (1-n) + detail_color[2] * n)
                arr[i, j] = [min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))]
        return arr
    
    # Grass texture dengan detail rumput dan variasi warna
    if not os.path.exists('assets/textures/grass.png'):
        arr = generate_fbm_texture(
            512,  # Resolution lebih tinggi untuk detail
            base_color=[20, 100, 20],      # Hijau gelap
            detail_color=[100, 180, 60],   # Hijau terang
            scale=25.0,
            layers=7,
            persistence=0.55
        )
        Image.fromarray(arr).save('assets/textures/grass.png')
        
    # Rock texture dengan karakteristik berbatu dan cracks
    if not os.path.exists('assets/textures/rock.png'):
        arr = generate_fbm_texture(
            512,
            base_color=[80, 80, 80],       # Abu-abu gelap
            detail_color=[180, 175, 170],  # Abu-abu terang
            scale=18.0,
            layers=8,
            persistence=0.6
        )
        Image.fromarray(arr).save('assets/textures/rock.png')
        
    # Lava texture dengan efek panas dan retakan (cracks)
    if not os.path.exists('assets/textures/lava.png'):
        arr = generate_fbm_texture(
            512,
            base_color=[200, 40, 0],       # Merah tua (lava dingin)
            detail_color=[255, 150, 0],    # Oranye (lava panas)
            scale=12.0,
            layers=6,
            persistence=0.58
        )
        # Tambah efek crack pattern
        for i in range(512):
            for j in range(512):
                crack = pnoise2(i * 0.1, j * 0.1, octaves=2)
                if crack > 0.6:  # Pattern untuk crack yang terlihat
                    arr[i, j] = [
                        int(min(255, int(arr[i, j][0]) + 30)), 
                        int(max(0, int(arr[i, j][1]) - 20)),
                        int(max(0, int(arr[i, j][2]) - 10))
                    ]
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
    t_gen = TerrainGenerator(size=400, scale=1.0)
    t_gen.generate()
    vertices, indices = t_gen.get_vertex_data()
    terrain_mesh = TerrainMesh(win.ctx, renderer.terrain_shader.program, vertices, indices)
    
    # Load Texture ke GPU
    print("[DEBUG] Loading textures...")
    tex_grass = load_texture(win.ctx, 'assets/textures/grass.png')
    print(f"  ✓ Grass texture loaded: {tex_grass}")
    tex_rock = load_texture(win.ctx, 'assets/textures/rock.png')
    print(f"  ✓ Rock texture loaded: {tex_rock}")
    tex_lava = load_texture(win.ctx, 'assets/textures/lava.png')
    print(f"  ✓ Lava texture loaded: {tex_lava}")
    
    # Assign texture unit ke variabel uniform shader
    renderer.terrain_shader.program['tex_grass'].value = 0
    renderer.terrain_shader.program['tex_rock'].value = 1
    renderer.terrain_shader.program['tex_lava'].value = 2
    print("[DEBUG] Texture units assigned to shader")
    
    # 5. Setup Sistem Animasi (Partikel, Kamera, Lighting)
    print("[5/5] Inisialisasi sistem dinamik...")
    p_system = ParticleSystem(win.ctx, renderer.particle_shader.program, max_particles=5000)
    emitter = VolcanoEmitter(p_system, center=(0.0, 100.0, 0.0))
    
    # Camera positioning untuk showcase features
    # Posisi default: dekat ke crater untuk showcase rim lighting & lava glow
    camera = Camera(position=(80.0, 110.0, 80.0), pitch=-20.0)
    
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
