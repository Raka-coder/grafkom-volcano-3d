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

    def emit(self, pos, vel, life, color_start, color_end, scale, is_mist=False):
        if len(self.particles) < self.max_particles:
            self.particles.append({
                'pos': np.array(pos, dtype=np.float32),
                'vel': np.array(vel, dtype=np.float32),
                'life': life,
                'max_life': life,
                'color_start': np.array(color_start, dtype=np.float32),
                'color_end': np.array(color_end, dtype=np.float32),
                'scale': scale,
                'is_mist': is_mist,
            })

    def update(self, dt):
        gravity = np.array([0.0, -15.0, 0.0], dtype=np.float32)
        drag_coeff = 0.98
        new_particles = []
        
        idx = 0
        for p in self.particles:
            p['life'] -= dt
            if p['life'] > 0:
                is_mist = p.get('is_mist', False)
                
                if is_mist:
                    t = 1.0 - (p['life'] / p['max_life'])
                    freq = 0.02
                    curl = 3.0
                    p['vel'][0] += -math.sin(p['pos'][2] * freq + t * 0.6) * curl * dt
                    p['vel'][2] +=  math.cos(p['pos'][0] * freq + t * 0.6) * curl * dt
                    p['vel'][1] += math.sin(t * 1.2 + p['pos'][0] * 0.01) * 0.3 * dt
                    p['vel'] *= 0.99
                else:
                    is_smoke = p['vel'][1] > 5.0
                    
                    if is_smoke:
                        buoyancy = np.array([0.0, 28.0, 0.0], dtype=np.float32)
                        p['vel'] += buoyancy * dt
                        
                        t = 1.0 - (p['life'] / p['max_life'])
                        wind_drift = np.array([math.sin(t * 2.0) * 2.0, 0.0, math.cos(t * 1.5) * 2.0], dtype=np.float32)
                        p['vel'] += wind_drift * dt

                        freq = 0.03
                        curl_str = 3.0
                        p['vel'][0] += -math.sin(p['pos'][2] * freq + t * 1.5) * curl_str * dt
                        p['vel'][2] +=  math.cos(p['pos'][0] * freq + t * 1.5) * curl_str * dt
                        
                        p['vel'] *= 0.992
                    else:
                        # Lava: Realistic physics dengan gravity dan air resistance
                        p['vel'] += gravity * dt

                        # Air resistance (drag)
                        p['vel'] *= drag_coeff

                        # --- COLLISION DETECTION & SPLASH ---
                        # Detect benturan dengan kawah crater
                        crater_height = 102.0
                        crater_radius = 15.0
                        dist_to_center = math.sqrt(p['pos'][0]**2 + p['pos'][2]**2)

                        if p['pos'][1] <= crater_height and dist_to_center < crater_radius + 5.0:
                            # Hit the crater floor/walls
                            p['pos'][1] = crater_height

                            # Energy-based bounce
                            bounce_energy = 0.4 * math.sqrt(p['vel'][0]**2 + p['vel'][1]**2 + p['vel'][2]**2)
                            p['vel'][1] = abs(p['vel'][1]) * 0.35 + bounce_energy * 0.2

                            # Splatter effect: partikel tersebar ke samping
                            p['vel'][0] += (np.random.rand() - 0.5) * 8.0
                            p['vel'][2] += (np.random.rand() - 0.5) * 8.0

                            # Tambah sedikit lifetime jika terjadi splash
                            p['life'] = max(p['life'], 0.5)

                        # Detect hit dengan terrain di bawah crater
                        if p['pos'][1] < -5.0:
                            p['life'] = -1  # Kill particle
                
                # Update posisi
                p['pos'] += p['vel'] * dt
                
                # 2. Color Interpolation dengan gradient yang lebih smooth
                t = 1.0 - (p['life'] / p['max_life'])
                c = p['color_start'] * (1.0 - t) + p['color_end'] * t
                
                # Opacity falloff di akhir lifetime
                alpha_fade = max(0.0, 1.0 - (t - 0.7) / 0.3) if t > 0.7 else 1.0
                c[3] *= alpha_fade
                
                if is_mist:
                    dynamic_scale = p['scale'] * (1.0 + t * 1.5)
                elif is_smoke:
                    dynamic_scale = p['scale'] * (1.0 + t * 8.0) * (1.0 - t * 0.2)
                else:
                    dynamic_scale = p['scale'] * (1.0 - t * 0.6)
                
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
