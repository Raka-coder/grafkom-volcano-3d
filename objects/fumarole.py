import math
import random
import numpy as np
from .base import GameObject

class Fumarole(GameObject):
    def __init__(self, ctx, program, pos, inner_radius=0.8, outer_radius=1.8, segments=12):
        verts, idxs = self._generate(inner_radius, outer_radius, segments)
        super().__init__(ctx, program, verts, idxs)
        self.set_position(pos[0], pos[1], pos[2])

    def _generate(self, inner_r, outer_r, segs):
        verts = []
        idxs = []
        inner_color = (0.9, 0.6, 0.1)
        outer_color = (0.2, 0.18, 0.15)

        for seg in range(segs + 1):
            a = 2 * math.pi * seg / segs
            ca, sa = math.cos(a), math.sin(a)
            t = seg / segs
            ring_color = tuple(
                inner_color[k] + (outer_color[k] - inner_color[k]) * t
                for k in range(3)
            )
            verts.extend([inner_r * ca, 0.1, inner_r * sa,  0.0, 1.0, 0.0, *ring_color])
            verts.extend([outer_r * ca, 0.0, outer_r * sa,  0.0, 1.0, 0.0, *outer_color])

        stride = (segs + 1) * 2
        for seg in range(segs):
            i0 = seg * 2
            i1 = seg * 2 + 1
            i2 = (seg + 1) * 2
            i3 = (seg + 1) * 2 + 1
            idxs.extend([i0, i1, i2,  i1, i3, i2])

        return np.array(verts, dtype='f4'), np.array(idxs, dtype='i4')


class FumaroleSteamEmitter:
    def __init__(self, system, center=(0.0, 0.0, 0.0), rate=18):
        self.system = system
        self.center = center
        self.rate = rate
        self.time_accum = 0.0

    def update(self, dt):
        self.time_accum += dt
        count = int(self.time_accum * self.rate)
        if count > 0:
            self.time_accum -= count / self.rate
            for _ in range(count):
                self._emit_one()

    def _emit_one(self):
        angle = random.uniform(0, 2 * math.pi)
        rad = random.uniform(0, 1.0)
        pos = (
            self.center[0] + math.cos(angle) * rad,
            self.center[1] + 0.2,
            self.center[2] + math.sin(angle) * rad
        )
        gray = random.uniform(0.7, 0.95)
        vel = (
            random.uniform(-2.0, 2.0),
            random.uniform(6.0, 14.0),
            random.uniform(-2.0, 2.0)
        )
        self.system.emit(
            pos=pos, vel=vel,
            life=random.uniform(5.0, 10.0),
            color_start=[gray, gray, gray, 0.25],
            color_end=[gray * 0.3, gray * 0.3, gray * 0.3, 0.0],
            scale=random.uniform(8.0, 20.0),
        )
