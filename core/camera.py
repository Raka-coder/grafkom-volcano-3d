import numpy as np
import math
import glfw

class Camera:
    """
    Kelas untuk mengatur Camera FPS (First Person Shooter).
    Menghitung View Matrix dan Projection Matrix untuk rendering grafika 3D.
    """
    def __init__(self, position=(0.0, 50.0, 150.0), yaw=-90.0, pitch=-20.0, speed=50.0, sens=0.1):
        self.position = np.array(position, dtype=np.float32)
        self.front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.right = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        self.world_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        
        self.yaw = yaw
        self.pitch = pitch
        self.speed = speed
        self.sens = sens
        
        self.update_vectors()

    def update_vectors(self):
        """
        Menghitung ulang vektor arah kamera (Front, Right, Up)
        berdasarkan sudut rotasi Euler (Yaw dan Pitch).
        """
        front = np.zeros(3, dtype=np.float32)
        front[0] = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front[1] = math.sin(math.radians(self.pitch))
        front[2] = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.front = front / np.linalg.norm(front)
        
        # Cross product front dan world_up menghasilkan vektor right
        self.right = np.cross(self.front, self.world_up)
        self.right = self.right / np.linalg.norm(self.right)
        
        # Cross product right dan front menghasilkan vektor up
        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)

    def process_keyboard(self, keys, dt, terrain_gen=None):
        """Merespon input WASD untuk pergerakan kamera."""
        velocity = self.speed * dt
        if keys.get(glfw.KEY_W):
            self.position += self.front * velocity
        if keys.get(glfw.KEY_S):
            self.position -= self.front * velocity
        if keys.get(glfw.KEY_A):
            self.position -= self.right * velocity
        if keys.get(glfw.KEY_D):
            self.position += self.right * velocity
            
        # Collision Detection: Jangan biarkan kamera menembus tanah/gunung
        if terrain_gen:
            terrain_h = terrain_gen.get_height_at(self.position[0], self.position[2])
            min_y = terrain_h + 5.0 # Tinggi mata 5 unit dari permukaan
            if self.position[1] < min_y:
                self.position[1] = min_y
            
    def process_mouse(self, dx, dy):
        """Merespon input pergerakan mouse untuk merotasi pandangan kamera."""
        self.yaw += dx * self.sens
        self.pitch += dy * self.sens
        
        # Limit pitch agar kamera tidak flip
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
            
        self.update_vectors()

    def get_view_matrix(self):
        """
        Menghasilkan View Matrix menggunakan operasi look-at.
        View Matrix mentransformasi dari world space ke camera space.
        """
        return self._look_at(self.position, self.position + self.front, self.up)
        
    def _look_at(self, eye, target, up):
        """Manual lookAt matrix calculation untuk menghindari library external rumit."""
        f = (target - eye)
        f = f / np.linalg.norm(f)
        s = np.cross(f, up)
        s = s / np.linalg.norm(s)
        u = np.cross(s, f)

        res = np.identity(4, dtype=np.float32)
        res[0, 0:3] = s
        res[1, 0:3] = u
        res[2, 0:3] = -f
        res[0:3, 3] = [-np.dot(s, eye), -np.dot(u, eye), np.dot(f, eye)]
        return res

    def get_projection_matrix(self, fov=45.0, aspect=1280.0/720.0, near=0.1, far=1000.0):
        """
        Menghasilkan Perspective Projection Matrix.
        Memberikan efek depth (benda jauh terlihat kecil).
        """
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        res = np.zeros((4, 4), dtype=np.float32)
        res[0, 0] = f / aspect
        res[1, 1] = f
        res[2, 2] = (far + near) / (near - far)
        res[3, 2] = -1.0
        res[2, 3] = (2.0 * far * near) / (near - far)
        return res
