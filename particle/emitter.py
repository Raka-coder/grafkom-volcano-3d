import random
import math

class VolcanoEmitter:
    """
    Logika emitter (sumber semburan) gunung berapi.
    Memunculkan berbagai jenis partikel: Lava, Smoke (Asap), dan Debris (Bebatuan).
    """
    def __init__(self, system, center=(0.0, 80.0, 0.0)):
        self.system = system
        self.center = center
        self.time_accumulator = 0.0
        self.emit_rate = 400 # Jumlah partikel per detik ditingkatkan

    def update(self, dt):
        """Mengeksekusi siklus pancaran berdasarkan waktu (dt)"""
        self.time_accumulator += dt
        
        num_emit = int(self.time_accumulator * self.emit_rate)
        if num_emit > 0:
            self.time_accumulator -= num_emit / self.emit_rate
            
            for _ in range(num_emit):
                # Sedikit offset acak pada titik spawn agar tidak keluar dari 1 titik tajam
                spawn_pos = (
                    self.center[0] + random.uniform(-5, 5),
                    self.center[1] + random.uniform(-2, 2),
                    self.center[2] + random.uniform(-5, 5)
                )

                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(20.0, 70.0)
                
                vx = math.cos(angle) * random.uniform(0.0, 20.0)
                vy = speed
                vz = math.sin(angle) * random.uniform(0.0, 20.0)
                
                r = random.random()
                if r < 0.4: 
                    # --- Lava (Menyala, berumur pendek) ---
                    color_start = [1.0, 0.3, 0.0, 1.0]
                    color_end = [0.2, 0.0, 0.0, 0.0]
                    life = random.uniform(1.0, 3.5)
                    scale = random.uniform(15.0, 35.0)
                    
                elif r < 0.9: 
                    # --- Smoke (Asap tebal, bervolume, gelap & halus) ---
                    # Abu-abu sangat gelap (hampir hitam di dasar kawah)
                    gray = random.uniform(0.1, 0.25)
                    color_start = [gray, gray, gray, 0.9] # Lebih pekat
                    color_end = [0.05, 0.05, 0.05, 0.0]
                    life = random.uniform(6.0, 16.0) # Bertahan lebih lama
                    scale = random.uniform(40.0, 100.0) # Ukuran bervolume
                    vy *= 0.7 # Kecepatan naik yang pas
                    
                else: 
                    # --- Debris (Batuan berat) ---
                    color_start = [0.1, 0.1, 0.1, 1.0]
                    color_end = [0.05, 0.05, 0.05, 1.0]
                    life = random.uniform(1.5, 3.0)
                    scale = random.uniform(5.0, 12.0)
                    vx *= 2.5
                    vz *= 2.5
                    
                self.system.emit(
                    pos=spawn_pos,
                    vel=[vx, vy, vz],
                    life=life,
                    color_start=color_start,
                    color_end=color_end,
                    scale=scale
                )
