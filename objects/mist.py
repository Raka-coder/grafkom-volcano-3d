import random
import math
import numpy as np

class MistEmitter:
    def __init__(self, system, terrain, center=(0.0, 0.0, 0.0),
                 ring_inner=20.0, ring_outer=100.0,
                 height_base=20.0, height_range=40.0, rate=40):
        self.system = system
        self.terrain = terrain
        self.center = center
        self.ring_inner = ring_inner
        self.ring_outer = ring_outer
        self.height_base = height_base
        self.height_range = height_range
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
        r = random.uniform(self.ring_inner, self.ring_outer)
        wx = self.center[0] + math.cos(angle) * r
        wz = self.center[2] + math.sin(angle) * r
        h = self.terrain.get_height_at(wx, wz)
        y = h + random.uniform(self.height_base, self.height_base + self.height_range)

        white = random.uniform(0.75, 0.95)
        self.system.emit(
            pos=(wx, y, wz),
            vel=(random.uniform(-2.0, 2.0), random.uniform(-0.3, 0.3), random.uniform(-2.0, 2.0)),
            life=random.uniform(30.0, 60.0),
            color_start=[white, white, white, 0.07],
            color_end=[white, white, white, 0.0],
            scale=random.uniform(100.0, 250.0),
            is_mist=True,
        )
