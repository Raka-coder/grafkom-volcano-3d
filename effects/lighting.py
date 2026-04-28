import math

class LightingConfig:
    """
    Menyimpan parameter konfigurasi untuk Blinn-Phong lighting.
    Mendukung sumber cahaya utama (Matahari) dan point light (Glow Lava).
    """
    def __init__(self):
        # Directional Light (Sun)
        self.sun_dir = [0.5, 1.0, 0.3]
        self.sun_color = [1.0, 0.9, 0.8]
        
        # Point Light (Lava)
        self.lava_pos = [0.0, 100.0, 0.0]
        
    def get_dynamic_lava_color(self, time):
        """Membuat efek kelap-kelip dinamis cahaya magma berdasarkan waktu (intensitas dikurangi)."""
        intensity = 0.9 + 0.1 * math.sin(time * 3.0)
        return [1.0 * intensity, 0.4 * intensity, 0.0]
