import math

class LightingConfig:
    """
    Menyimpan parameter konfigurasi untuk pencahayaan advanced.
    Mendukung multiple light sources: Directional Light (Matahari), Point Light (Lava Glow),
    dan ambient lighting yang dapat dikonfigurasi.
    """
    def __init__(self):
        # Directional Light (Sun) - Cahaya utama dari langit
        self.sun_dir = [0.5, 1.0, 0.3]
        self.sun_color = [1.0, 0.95, 0.85]
        self.sun_intensity = 1.0
        
        # Point Light (Lava Glow) - Cahaya dari kawah
        self.lava_pos = [0.0, 100.0, 0.0]
        self.lava_radius = 200.0  # Radius of light influence
        
        # Ambient Lighting - Cahaya ambient untuk shadow filling
        self.ambient_color = [0.3, 0.35, 0.4]
        self.ambient_intensity = 0.25
        
        # Fog configuration
        self.fog_color = [0.5, 0.6, 0.7]
        self.fog_density = 0.003
        
    def get_dynamic_lava_color(self, time):
        """
        Membuat efek kelap-kelip dinamis cahaya magma berdasarkan waktu.
        Menggunakan kombinasi sine waves untuk natural flickering.
        """
        # Multiple frequencies untuk natural flicker
        main_flicker = 0.8 + 0.2 * math.sin(time * 3.5)
        secondary_flicker = 1.0 + 0.15 * math.sin(time * 7.2 + 1.5)
        tertiary_flicker = 1.0 + 0.1 * math.sin(time * 2.1 + 3.0)
        
        combined_flicker = main_flicker * secondary_flicker * tertiary_flicker
        combined_flicker = max(0.4, min(1.2, combined_flicker))  # Clamp to reasonable values
        
        # Warna lava dengan intensity modulation
        return [
            1.0 * combined_flicker,      # Red channel
            0.4 * combined_flicker * 0.9,  # Green channel (reduced)
            0.0                           # Blue channel (no blue light from lava)
        ]
    
    def get_lava_light_intensity(self, distance):
        """
        Menghitung atenuasi cahaya berdasarkan jarak dari sumber lava.
        Menggunakan inverse square law dengan smooth falloff.
        """
        # Normalized distance
        normalized_dist = distance / self.lava_radius
        
        if normalized_dist > 1.0:
            return 0.0
        
        # Smooth falloff using smoothstep
        falloff = 1.0 - (normalized_dist * normalized_dist)
        return falloff * falloff  # Quadratic falloff for natural attenuation
    
    def update_for_time(self, time):
        """Update dynamic properties based on time"""
        # Lava position could move if we wanted dynamic eruption center
        # For now, it stays fixed at the crater center
        pass
