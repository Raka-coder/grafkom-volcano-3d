import math
import random
import numpy as np
from .base import GameObject

class Rock(GameObject):
    def __init__(self, ctx, program, radius=2.0, segments=8, rings=5, seed=0):
        verts, idxs = self._generate(radius, segments, rings, seed)
        super().__init__(ctx, program, verts, idxs)
        self.radius = radius

    def _jitter(self, x, y, z):
        h = math.sin(x * 12.989 + y * 78.233 + z * 45.164) * 43758.5453
        return h - math.floor(h)

    def _generate(self, radius, segs, rings, seed):
        verts = []
        idxs = []
        rng = random.Random(seed)

        base = rng.uniform(0.25, 0.45)
        var = rng.uniform(0.10, 0.20)

        vc = 0
        for ring in range(rings + 1):
            theta = math.pi * ring / rings
            for seg in range(segs):
                phi = 2 * math.pi * seg / segs

                x = math.sin(theta) * math.cos(phi)
                y = math.cos(theta)
                z = math.sin(theta) * math.sin(phi)

                j1 = self._jitter(x * 3.7 + seed * 1.3, y * 5.1 + seed * 2.7, z * 4.3 + seed * 0.9)
                j2 = self._jitter(x * 2.1 + seed * 4.7, y * 3.3 + seed * 8.1, z * 5.7 + seed * 2.3)
                r = radius * (0.55 + 0.25 * j1 + 0.20 * j2)

                jg = self._jitter(x * 7.1 + 10, y * 9.3 + 10, z * 6.7 + 10)
                c = base + (jg - 0.5) * var * 2
                warm = 1.0 + (jg - 0.5) * 0.15

                verts.extend([x * r, y * r, z * r,  x, y, z,  c * warm, c * warm * 0.88, c * 0.75])
                vc += 1

        for ring in range(rings):
            for seg in range(segs):
                nxt = (seg + 1) % segs
                bl = ring * segs + seg
                br = ring * segs + nxt
                tl = (ring + 1) * segs + seg
                tr = (ring + 1) * segs + nxt

                if ring > 0:
                    idxs.extend([bl, br, tl,  tl, br, tr])

        return np.array(verts, dtype='f4'), np.array(idxs, dtype='i4')
