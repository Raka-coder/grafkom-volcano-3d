import numpy as np
import noise
import math

class TerrainGenerator:
    """
    Kelas untuk menghasilkan procedural terrain 3D.
    Menggunakan algoritma perlin noise digabung dengan bentuk cone untuk membentuk gunung berapi.
    """
    def __init__(self, size=400, scale=1.5):
        self.size = size
        self.scale = scale
        self.heights = np.zeros((size, size), dtype=np.float32)
        self.normals = np.zeros((size, size, 3), dtype=np.float32)

    def generate(self):
        """Menjalankan seluruh pipeline generasi terrain."""
        self._generate_heights()
        self._calculate_normals()

    def _generate_heights(self):
        """
        Membuat elevasi (ketinggian) terrain.
        Mendukung multiple gunung dan base terrain yang lebih luas.
        """
        # Konfigurasi gunung (pusat_x, pusat_z, tinggi, radius, radius_kawah)
        # Radius utama dikurangi sedikit agar tidak terlalu "tajam" dan lebih landai
        # Anak gunung dibuat jauh lebih kecil agar menyatu halus dengan badan utama
        center_x, center_z = self.size / 2.0, self.size / 2.0
        mountains = [
            (center_x, center_z, 105.0, self.size / 2.8, 18.0),    # Gunung Utama (Lebih Landai)
            (center_x + 40, center_z + 30, 25.0, self.size / 12.0, 0.0), # Anak Gunung 1 (Sangat Kecil)
            (center_x - 50, center_z - 20, 22.0, self.size / 14.0, 0.0), # Anak Gunung 2 (Sangat Kecil)
            (center_x + 15, center_z - 55, 20.0, self.size / 15.0, 0.0), # Anak Gunung 3 (Sangat Kecil)
            (center_x - 30, center_z + 50, 18.0, self.size / 16.0, 0.0), # Anak Gunung 4 (Sangat Kecil)
        ]

        for i in range(self.size):
            for j in range(self.size):
                # 1. Base terrain (Perlin Noise 3D - Dioptimalkan)
                # Mengurangi octaves agar lebih ringan di Python murni
                x, z = i * 0.02, j * 0.02
                h_base = noise.pnoise3(x, z, 0.0, octaves=4, persistence=0.5, lacunarity=2.0) * 22.0
                
                # 2. Akumulasi bentuk gunung
                h_volcano = 0.0
                for idx, (mx, mz, m_height, m_radius, m_crater) in enumerate(mountains):
                    dist = math.sqrt((i - mx)**2 + (j - mz)**2)
                    if dist < m_radius:
                        t = dist / m_radius
                        shape = (1.0 - (t ** 2)) ** 2 
                        h_current = shape * m_height
                        
                        # Variasi puncak (idx 0) - Dioptimalkan ke 3 octaves
                        if idx == 0:
                            peak_variation = noise.pnoise3(i * 0.07, j * 0.07, 0.5, octaves=3) * 14.0 * (shape ** 1.2)
                            h_current += peak_variation
                        
                        # Cekungan crater
                        if m_crater > 0 and dist < m_crater:
                            h_current -= (m_crater - dist) * 2.5
                        
                        h_volcano = max(h_volcano, h_current)
                        
                self.heights[i, j] = h_base + h_volcano

    def _calculate_normals(self):
        """
        Menghitung normal vector tiap vertex (untuk pencahayaan mulus/smooth shading).
        Menggunakan Central Differences untuk mendapat gradien kemiringan terrain.
        """
        for i in range(self.size):
            for j in range(self.size):
                hx_minus = self.heights[i-1, j] if i > 0 else self.heights[i, j]
                hx_plus = self.heights[i+1, j] if i < self.size-1 else self.heights[i, j]
                hz_minus = self.heights[i, j-1] if j > 0 else self.heights[i, j]
                hz_plus = self.heights[i, j+1] if j < self.size-1 else self.heights[i, j]

                dx = (hx_plus - hx_minus) / (2.0 * self.scale)
                dz = (hz_plus - hz_minus) / (2.0 * self.scale)
                
                normal = np.array([-dx, 1.0, -dz], dtype=np.float32)
                self.normals[i, j] = normal / np.linalg.norm(normal)

    def get_steepness_at(self, world_x, world_z):
        h = self.get_height_at(world_x, world_z)
        dx = self.get_height_at(world_x + 2, world_z) - h
        dz = self.get_height_at(world_x, world_z + 2) - h
        return math.sqrt(dx * dx + dz * dz)

    def get_height_at(self, world_x, world_z):
        """
        Mengambil ketinggian terrain pada koordinat world tertentu.
        Digunakan untuk collision detection kamera.
        """
        offset = self.size * self.scale / 2.0
        # Konversi world position kembali ke grid index
        grid_i = int((world_x + offset) / self.scale)
        grid_j = int((world_z + offset) / self.scale)
        
        # Clamp agar tidak index out of bounds
        grid_i = max(0, min(self.size - 1, grid_i))
        grid_j = max(0, min(self.size - 1, grid_j))
        
        return self.heights[grid_i, grid_j]

    def get_vertex_data(self):
        """
        Menyusun data vertex (posisi, normal, UV) ke format array linear.
        Membuat indeks untuk Index Buffer (EBO).
        """
        vertices = []
        indices = []
        
        offset = self.size * self.scale / 2.0 # Centering
        
        for i in range(self.size):
            for j in range(self.size):
                x = i * self.scale - offset
                z = j * self.scale - offset
                y = self.heights[i, j]
                
                nx, ny, nz = self.normals[i, j]
                
                # Texcoord UV (0.0 -> 1.0)
                u = i / (self.size - 1)
                v = j / (self.size - 1)
                
                vertices.extend([x, y, z, nx, ny, nz, u, v])
                
        for i in range(self.size - 1):
            for j in range(self.size - 1):
                top_left = i * self.size + j
                top_right = top_left + 1
                bottom_left = (i + 1) * self.size + j
                bottom_right = bottom_left + 1
                
                # 2 segitiga untuk 1 kotak grid (CCW Winding Order)
                indices.extend([top_left, top_right, bottom_left])
                indices.extend([bottom_left, top_right, bottom_right])
                
        return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.int32)
