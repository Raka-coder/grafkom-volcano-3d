import numpy as np
import math
import noise

class ParticleSystem:
    """
    Sistem partikel GPU-friendly menggunakan dynamic buffer (VBO).
    Mensimulasikan gerakan partikel (lava, smoke, dll) berdasarkan physics sederhana.
    """
    def __init__(self, ctx, program, max_particles=5000):
        self.ctx = ctx
        self.program = program
        self.max_particles = max_particles
        self.particles = []
        
        # Buffer untuk menyimpan data setiap partikel.
        self.vbo_data = np.zeros(self.max_particles * 8, dtype=np.float32)
        
        # Buffer bersifat dynamic karena sering diupdate di tiap frame
        self.vbo = ctx.buffer(reserve=self.vbo_data.nbytes, dynamic=True)
        
        self.vao = ctx.vertex_array(
            self.program,
            [(self.vbo, '3f 4f 1f', 'in_position', 'in_color', 'in_scale')]
        )
        self.active_count = 0

    def emit(self, pos, vel, life, color_start, color_end, scale):
        """Mendaftarkan partikel baru ke sistem jika belum penuh."""
        if len(self.particles) < self.max_particles:
            self.particles.append({
                'pos': np.array(pos, dtype=np.float32),
                'vel': np.array(vel, dtype=np.float32),
                'life': life,
                'max_life': life,
                'color_start': np.array(color_start, dtype=np.float32),
                'color_end': np.array(color_end, dtype=np.float32),
                'scale': scale
            })

    def update(self, dt):
        """Memperbarui posisi dan warna seluruh partikel (Dioptimalkan untuk performa)."""
        gravity = np.array([0.0, -12.0, 0.0], dtype=np.float32) 
        new_particles = []
        
        idx = 0
        for p in self.particles:
            p['life'] -= dt
            if p['life'] > 0:
                is_smoke = p['vel'][1] > 0
                
                # 1. Physics & Forces
                force = gravity.copy()
                if is_smoke:
                    # Smoke: Gaya angkat + Pseudo-Curl (Cepat)
                    force += np.array([0.0, 20.0, 0.0])
                    # Gunakan sine wave + 1 noise sample (jauh lebih cepat dari 6x pnoise3)
                    swirl_speed = noise.pnoise2(p['pos'][0] * 0.05, p['pos'][2] * 0.05) * 3.0
                    p['vel'][0] += math.sin(p['life'] * 2.0) * swirl_speed * dt
                    p['vel'][2] += math.cos(p['life'] * 2.0) * swirl_speed * dt
                else:
                    # Lava: Deteksi benturan kawah (Splash)
                    if p['pos'][1] < 102.0:
                        p['pos'][1] = 102.0
                        p['vel'][1] *= -0.3
                        p['vel'][0] += (np.random.rand() - 0.5) * 5.0
                        p['vel'][2] += (np.random.rand() - 0.5) * 5.0
                
                p['vel'] += force * dt
                p['pos'] += p['vel'] * dt
                
                # 2. Interpolasi & Visual
                t = 1.0 - (p['life'] / p['max_life'])
                c = p['color_start'] * (1.0 - t) + p['color_end'] * t
                
                # Smoke membesar, lava mengecil
                dynamic_scale = p['scale'] * (1.0 + t * 4.0) if is_smoke else p['scale'] * (1.0 - t * 0.5)
                
                # Masukkan ke array VBO
                offset = idx * 8
                self.vbo_data[offset:offset+3] = p['pos']
                self.vbo_data[offset+3:offset+7] = c
                self.vbo_data[offset+7] = dynamic_scale
                
                new_particles.append(p)
                idx += 1
                
        self.particles = new_particles
        if idx > 0:
            self.vbo.write(self.vbo_data[:idx * 8].tobytes())
        self.active_count = idx

    def render(self):
        """Gambar seluruh partikel dalam 1 draw call."""
        if self.active_count > 0:
            # Render sebagai kumpulan titik GL_POINTS
            self.vao.render(mode=self.ctx.POINTS, vertices=self.active_count)
