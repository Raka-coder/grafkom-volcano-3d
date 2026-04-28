import numpy as np
import math

# Pure Python Perlin Noise Implementation (2D & 3D)
# Based on Ken Perlin's reference implementation

class _PerlinNoise:
    def __init__(self, seed=42):
        np.random.seed(seed)
        p = np.arange(256, dtype=int)
        np.random.shuffle(p)
        self.p = np.concatenate([p, p])

    def _fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, t, a, b):
        return a + t * (b - a)

    def _grad(self, hash, x, y, z):
        h = hash & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def noise3(self, x, y, z):
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        Z = int(math.floor(z)) & 255
        
        x -= math.floor(x)
        y -= math.floor(y)
        z -= math.floor(z)
        
        u = self._fade(x)
        v = self._fade(y)
        w = self._fade(z)
        
        A = self.p[X] + Y
        AA = self.p[A] + Z
        AB = self.p[A + 1] + Z
        B = self.p[X + 1] + Y
        BA = self.p[B] + Z
        BB = self.p[B + 1] + Z
        
        return self._lerp(w, self._lerp(v, self._lerp(u, self._grad(self.p[AA], x, y, z),
                                                         self._grad(self.p[BA], x - 1, y, z)),
                                          self._lerp(u, self._grad(self.p[AB], x, y - 1, z),
                                                         self._grad(self.p[BB], x - 1, y - 1, z))),
                             self._lerp(v, self._lerp(u, self._grad(self.p[AA + 1], x, y, z - 1),
                                                         self._grad(self.p[BA + 1], x - 1, y, z - 1)),
                                          self._lerp(u, self._grad(self.p[AB + 1], x, y - 1, z - 1),
                                                         self._grad(self.p[BB + 1], x - 1, y - 1, z - 1))))

_instance = _PerlinNoise()

def pnoise2(x, y, octaves=1, persistence=0.5, lacunarity=2.0):
    return pnoise3(x, y, 0.0, octaves, persistence, lacunarity)

def pnoise3(x, y, z, octaves=1, persistence=0.5, lacunarity=2.0):
    total = 0.0
    frequency = 1.0
    amplitude = 1.0
    max_value = 0.0
    for _ in range(octaves):
        total += _instance.noise3(x * frequency, y * frequency, z * frequency) * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    return total / max_value
