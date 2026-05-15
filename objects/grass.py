import math
import random
import numpy as np
from .base import GameObject

class GrassPatch(GameObject):
    def __init__(self, ctx, program, width=3.0, height=4.0, seed=0):
        verts, idxs = self._generate(width, height, seed)
        super().__init__(ctx, program, verts, idxs)

    def _generate(self, width, height, seed):
        verts = []
        idxs = []
        random.seed(seed)

        green_dark = (0.15, 0.45, 0.08)
        green_light = (0.25, 0.60, 0.12)

        # Two perpendicular quads (cross shape)
        offsets = [
            (-width / 2, 0, 0),
            (width / 2, 0, 0),
            (-width / 2, height, 0),
            (width / 2, height, 0),
            (0, 0, -width / 2),
            (0, 0, width / 2),
            (0, height, -width / 2),
            (0, height, width / 2),
        ]

        normals = [
            (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),
            (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),
        ]

        vc = 0
        for i, ((ox, oy, oz), (nx, ny, nz)) in enumerate(zip(offsets, normals)):
            t = (i % 4) / 3
            gc = tuple(a + (b - a) * t for a, b in zip(green_dark, green_light))
            verts.extend([ox, oy, oz,  nx, ny, nz, *gc])
            vc += 1

        idxs.extend([0, 1, 2,  2, 1, 3])
        idxs.extend([4, 5, 6,  6, 5, 7])

        return np.array(verts, dtype='f4'), np.array(idxs, dtype='i4')
