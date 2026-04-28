class FogConfig:
    """Pengaturan untuk efek kabut lingkungan (Atmospheric scattering)"""
    def __init__(self, color=(0.5, 0.6, 0.7), density=0.003):
        self.color = color
        self.density = density
