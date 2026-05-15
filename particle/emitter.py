import random
import math

class VolcanoEmitter:
    """
    Logika emitter (sumber semburan) gunung berapi yang canggih.
    Memunculkan berbagai jenis partikel: Lava, Smoke, Ash, dan Debris (Bebatuan).
    Dengan erupsi cycle yang dinamis untuk simulasi yang lebih realistis.
    """
    def __init__(self, system, center=(0.0, 80.0, 0.0)):
        self.system = system
        self.center = center
        self.time_accumulator = 0.0
        self.base_emit_rate = 350  # Particles per second
        self.eruption_phase = 0.0  # Untuk dynamic eruption intensity
        
    def get_eruption_intensity(self, time):
        """
        Menghitung intensitas erupsi berdasarkan waktu.
        Menghasilkan pola erupsi yang lebih natural dengan peaks dan valleys.
        """
        # Sine wave dengan multiple frequencies untuk natural eruption pattern
        base_intensity = 0.7 + 0.3 * math.sin(time * 0.3)  # Slow pulse
        secondary = 0.5 + 0.5 * math.sin(time * 1.2)       # Medium pulse
        return base_intensity * secondary

    def update(self, dt):
        """Mengeksekusi siklus pancaran berdasarkan waktu (dt) dengan intensitas dinamis"""
        self.time_accumulator += dt
        
        # Dynamically adjust emission rate based on eruption intensity
        intensity = self.get_eruption_intensity(self.time_accumulator)
        current_emit_rate = self.base_emit_rate * intensity
        
        num_emit = int(self.time_accumulator * current_emit_rate)
        if num_emit > 0:
            self.time_accumulator -= num_emit / current_emit_rate
            
            for _ in range(num_emit):
                # Sedikit offset acak pada titik spawn agar tidak keluar dari 1 titik tajam
                spawn_radius = 6.0 * intensity  # Radius grows with eruption intensity
                spawn_pos = (
                    self.center[0] + random.uniform(-spawn_radius, spawn_radius),
                    self.center[1] + random.uniform(-3, 4),
                    self.center[2] + random.uniform(-spawn_radius, spawn_radius)
                )

                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(25.0, 75.0) * (0.8 + intensity * 0.5)  # Speed varies with intensity
                
                # Cone-shaped velocity distribution
                horizontal_speed = random.uniform(5.0, 25.0) * intensity
                vx = math.cos(angle) * horizontal_speed
                vy = speed
                vz = math.sin(angle) * horizontal_speed
                
                # Particle type selection dengan probabilitas yang lebih beragam
                r = random.random()
                if r < 0.35:  # Lava particles (35%)
                    color_start = [1.0, 0.35, 0.0, 1.0]
                    color_end = [0.3, 0.05, 0.0, 0.1]
                    life = random.uniform(1.2, 4.0)
                    scale = random.uniform(12.0, 40.0)
                    
                elif r < 0.70:  # Smoke particles (35%)
                    # Varying gray levels untuk realism
                    gray = random.uniform(0.12, 0.35)
                    color_start = [gray, gray, gray, 0.85]
                    color_end = [0.03, 0.03, 0.03, 0.0]
                    life = random.uniform(7.0, 18.0)  # Longer lifetime
                    scale = random.uniform(35.0, 110.0)
                    vy *= 0.6
                    
                elif r < 0.90:  # Ash particles (20%)
                    gray = random.uniform(0.25, 0.45)
                    color_start = [gray, gray * 0.9, gray * 0.8, 0.7]  # Slight brown tint
                    color_end = [0.1, 0.08, 0.06, 0.0]
                    life = random.uniform(5.0, 12.0)
                    scale = random.uniform(8.0, 25.0)
                    vy *= 0.8
                    # Ash disperses more
                    vx += (random.random() - 0.5) * 3.0
                    vz += (random.random() - 0.5) * 3.0
                    
                else:  # Debris/Rock particles (10%)
                    color_start = [0.15, 0.15, 0.15, 1.0]
                    color_end = [0.08, 0.08, 0.08, 0.8]
                    life = random.uniform(2.0, 3.5)
                    scale = random.uniform(4.0, 15.0)
                    # Debris launches faster and farther
                    vx *= 2.0
                    vz *= 2.0
                    vy *= 0.9
                    
                self.system.emit(
                    pos=spawn_pos,
                    vel=[vx, vy, vz],
                    life=life,
                    color_start=color_start,
                    color_end=color_end,
                    scale=scale
                )
