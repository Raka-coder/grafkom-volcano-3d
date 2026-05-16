import os
import random
import math
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
from objects.tree import PineTree
from objects.lava_flow import LavaFlow
from objects.ground_glow import GroundGlow
from objects.fumarole import Fumarole, FumaroleSteamEmitter
from objects.mist import MistEmitter
from effects.lightning import Lightning
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

    print("[4.5/5] Inisialisasi shadow map...")
    renderer.init_shadow(terrain_mesh.vbo, terrain_mesh.ibo, size=2048)
    light_dir = np.array([0.6, 1.0, 0.4], dtype='f4')
    light_dir = light_dir / np.linalg.norm(light_dir)
    renderer.shadow_map.compute_light_matrix(
        light_dir=light_dir,
        scene_center=(0.0, 50.0, 0.0),
        scene_radius=250.0
    )
    print(f"  ✓ Shadow map {2048}x{2048} created")

    # 5. Setup Sistem Animasi (Partikel, Kamera, Lighting)
    print("[5/5] Inisialisasi sistem dinamik...")
    p_system = ParticleSystem(win.ctx, renderer.particle_shader.program, max_particles=20000)
    emitter = VolcanoEmitter(p_system, center=(0.0, 100.0, 0.0))
    
    print("[5.5/5] Menempatkan objek (pohon, batu, rumput)...")
    random.seed(42)
    placed_trees = 0
    tree_positions = []

    def try_place_tree(base_wx, base_wz, i):
        nonlocal placed_trees
        wx = base_wx + random.uniform(-8, 8)
        wz = base_wz + random.uniform(-8, 8)
        dist = math.hypot(wx, wz)
        h = t_gen.get_height_at(wx, wz)
        steep = t_gen.get_steepness_at(wx, wz)
        if 2.0 < h < 40.0 and steep < 2.0 and dist > 20.0 and placed_trees < 50:
            height = random.uniform(5.0, 16.0)
            tree = PineTree(win.ctx, renderer.object_shader.program,
                            height=height, segments=10, seed=i * 10 + placed_trees)
            tree.set_position(wx, h - 0.4, wz)
            tree.set_rotation(random.uniform(-3, 3), random.uniform(0, 360), 0)
            renderer.add_object(tree)
            tree_positions.append((wx, wz))
            placed_trees += 1
            return True
        return False

    for i in range(60):
        wx = random.uniform(-140.0, 140.0)
        wz = random.uniform(-140.0, 140.0)
        try_place_tree(wx, wz, i)

    for wx, wz in tree_positions[:20]:
        for j in range(random.randint(1, 3)):
            try_place_tree(wx, wz, int(wx * 10 + j))

    print(f"  ✓ {placed_trees} trees placed")

    print("[5.75/5] Membuat aliran lava...")
    lava_angles = [math.radians(-45), math.radians(135), math.radians(20)]
    for i, angle in enumerate(lava_angles):
        lava = LavaFlow(win.ctx, renderer.lava_shader.program, t_gen,
                        center=(0.0, 0.0), angle=angle,
                        start_r=20, end_r=80 + i * 10,
                        segments=40, width_start=2.0 + i * 0.5,
                        width_end=5.0 + i * 2.0, curve=0.3 + i * 0.15)
        renderer.add_lava(lava)
    print(f"  ✓ {len(lava_angles)} lava flows created")

    print("[5.8/5] Membuat efek atmosferik...")
    glow_crater = GroundGlow(win.ctx, renderer.glow_shader.program,
                              center=(0.0, t_gen.get_height_at(0, 0) + 1.0, 0.0),
                              radius=25.0, color=(1.0, 0.4, 0.05), intensity=1.2)
    renderer.add_glow(glow_crater)
    for angle in [0, 90, 180, 270]:
        ox = math.cos(math.radians(angle)) * 22
        oz = math.sin(math.radians(angle)) * 22
        h = t_gen.get_height_at(ox, oz)
        if h > 80:
            small = GroundGlow(win.ctx, renderer.glow_shader.program,
                                center=(ox, h + 1.0, oz),
                                radius=12.0, color=(1.0, 0.5, 0.1), intensity=0.8)
            renderer.add_glow(small)

    lightning = Lightning(win.ctx, renderer.unlit_shader.program,
                          center=(0.0, 150.0, 0.0), spread=25.0,
                          height_range=(120, 250))
    renderer.set_lightning(lightning)
    print("  ✓ Crater glow + volcanic lightning created")

    print("[5.85/5] Menempatkan fumarol + uap...")
    random.seed(123)
    fumarole_emitters = []
    for _ in range(14):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(16.0, 55.0)
        wx = math.cos(angle) * r
        wz = math.sin(angle) * r
        h = t_gen.get_height_at(wx, wz)
        if 25.0 < h < 85.0:
            fum = Fumarole(win.ctx, renderer.object_shader.program, (wx, h, wz),
                           inner_radius=random.uniform(0.5, 1.0),
                           outer_radius=random.uniform(1.2, 2.2))
            renderer.add_object(fum)
            em = FumaroleSteamEmitter(p_system, center=(wx, h, wz),
                                      rate=random.randint(15, 28))
            fumarole_emitters.append(em)
    print(f"  ✓ {len(fumarole_emitters)} fumaroles with steam placed")

    print("[5.9/5] Membuat lapisan kabut (mist/low clouds)...")
    mist_emitter = MistEmitter(p_system, t_gen, center=(0.0, 0.0, 0.0),
                               ring_inner=25.0, ring_outer=90.0,
                               height_base=25.0, height_range=35.0,
                               rate=25)
    print("  ✓ Mist emitter initialized")

    renderer.ash_intensity = 0.55
    renderer.ash_radius = 55.0
    print("  ✓ Ash layer enabled (intensity=0.55, radius=55)")

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
        for fem in fumarole_emitters:
            fem.update(dt)
        mist_emitter.update(dt)
        p_system.update(dt)
        lightning.update(dt)

        renderer.ash_intensity = 0.3 + 0.25 * emitter.get_eruption_intensity(current_time)
        
        # Render Frame
        # Warna background disamakan dengan warna kabut (fog)
        win.ctx.clear(0.55, 0.7, 0.95) 

        renderer.render_shadow_map()

        # Bind tekstur ke slot masing-masing
        tex_grass.use(location=0)
        tex_rock.use(location=1)
        tex_lava.use(location=2)
        
        renderer.render_sky(camera, current_time)
        renderer.render_terrain(terrain_mesh, camera, light_cfg.lava_pos, current_time)
        renderer.render_lava(camera, current_time)
        renderer.render_objects(camera)
        renderer.render_lightning(camera)
        renderer.render_particles(p_system, camera, current_time)
        
        # Swap Double Buffer
        win.swap_buffers()
        
    win.terminate()

if __name__ == '__main__':
    main()
