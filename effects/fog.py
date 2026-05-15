class FogConfig:
    """Pengaturan untuk efek kabut lingkungan (Atmospheric scattering)"""
    def __init__(self, color=(0.7, 0.8, 0.95), density=0.003):
        self.color = color
        self.density = density
