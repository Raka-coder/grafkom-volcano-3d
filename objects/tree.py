import math
import random
import numpy as np
from .base import GameObject

class PineTree(GameObject):
    def __init__(self, ctx, program, height=10.0, segments=10, seed=0):
        verts, idxs = self._generate(height, segments, seed)
        super().__init__(ctx, program, verts, idxs)
        self.height = height

    def _generate(self, height, segs, seed):
        verts = []
        idxs = []
        rng = random.Random(seed)
        vc = 0

        trunk_h = height * rng.uniform(0.30, 0.40)
        trunk_r = height * rng.uniform(0.030, 0.045)
        crown_base_r = height * rng.uniform(0.18, 0.26)

        # --- Trunk with slight curve ---
        trunk_color = (0.32, 0.18, 0.07)
        bend_x = rng.uniform(-0.15, 0.15)
        bend_z = rng.uniform(-0.15, 0.15)

        for i in range(segs):
            a1 = 2 * math.pi * i / segs
            a2 = 2 * math.pi * ((i + 1) % segs) / segs
            c1, s1 = math.cos(a1), math.sin(a1)
            c2, s2 = math.cos(a2), math.sin(a2)

            r_off1 = trunk_r * rng.uniform(0.85, 1.15)
            r_off2 = trunk_r * rng.uniform(0.85, 1.15)

            bx1 = c1 * r_off1
            bz1 = s1 * r_off1
            bx2 = c2 * r_off2
            bz2 = s2 * r_off2

            tx1 = c1 * r_off1 + bend_x * trunk_h
            tz1 = s1 * r_off1 + bend_z * trunk_h
            tx2 = c2 * r_off2 + bend_x * trunk_h
            tz2 = s2 * r_off2 + bend_z * trunk_h

            verts.extend([bx1, 0, bz1,  c1, 0, s1, *trunk_color])
            verts.extend([bx2, 0, bz2,  c2, 0, s2, *trunk_color])
            verts.extend([tx1, trunk_h, tz1,  c1, 0, s1, *trunk_color])
            verts.extend([tx2, trunk_h, tz2,  c2, 0, s2, *trunk_color])

            idxs.extend([vc, vc + 2, vc + 1,  vc + 2, vc + 3, vc + 1])
            vc += 4

        # --- Crown: 4 uneven cone layers ---
        layers = [
            (trunk_h * 0.02, crown_base_r * rng.uniform(0.9, 1.1), trunk_h * 0.32, crown_base_r * rng.uniform(0.45, 0.60)),
            (trunk_h * 0.22, crown_base_r * rng.uniform(0.65, 0.80), trunk_h * 0.52, crown_base_r * rng.uniform(0.25, 0.40)),
            (trunk_h * 0.42, crown_base_r * rng.uniform(0.40, 0.55), trunk_h * 0.72, crown_base_r * rng.uniform(0.12, 0.25)),
            (trunk_h * 0.62, crown_base_r * rng.uniform(0.20, 0.35), trunk_h * 0.95, crown_base_r * 0.0),
        ]

        for y1, r1, y2, r2 in layers:
            y_off = trunk_h
            dr = r1 - r2
            dy = y2 - y1
            length = math.hypot(dr, dy) or 1
            ny = dy / length

            for i in range(segs):
                a1 = 2 * math.pi * i / segs
                a2 = 2 * math.pi * ((i + 1) % segs) / segs
                c1, s1 = math.cos(a1), math.sin(a1)
                c2, s2 = math.cos(a2), math.sin(a2)

                n_mag = dr / length
                nx1 = n_mag * c1
                nz1 = n_mag * s1
                nx2 = n_mag * c2
                nz2 = n_mag * s2

                rr1 = r1 * rng.uniform(0.9, 1.1)
                rr2 = r2 * rng.uniform(0.9, 1.1)
                t = i / segs
                gc_b = (0.06 + t * 0.12, 0.25 + t * 0.30, 0.05 + t * 0.08)
                gc_t = (0.06 + t * 0.12, 0.25 + t * 0.30, 0.05 + t * 0.08)

                verts.extend([c1 * rr1, y1 + y_off, s1 * rr1,  nx1, ny, nz1, *gc_b])
                verts.extend([c2 * rr1, y1 + y_off, s2 * rr1,  nx2, ny, nz2, *gc_b])
                verts.extend([c1 * rr2, y2 + y_off, s1 * rr2,  nx1, ny, nz1, *gc_t])
                verts.extend([c2 * rr2, y2 + y_off, s2 * rr2,  nx2, ny, nz2, *gc_t])

                idxs.extend([vc, vc + 2, vc + 1,  vc + 2, vc + 3, vc + 1])
                vc += 4

        return np.array(verts, dtype='f4'), np.array(idxs, dtype='i4')
