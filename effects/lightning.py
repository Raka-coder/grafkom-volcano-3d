import math
import random
import numpy as np

class Lightning:
    def __init__(self, ctx, program, center=(0.0, 150.0, 0.0), spread=20.0, height_range=(120, 250)):
        self.ctx = ctx
        self.program = program
        self.center = center
        self.spread = spread
        self.height_range = height_range
        self.bolts = []
        self.time = 0.0
        self.next_flash = random.uniform(1.0, 4.0)

    def _generate_bolt(self, start, end, segments=7, jitter=4.0):
        verts = []
        sx, sy, sz = start
        ex, ey, ez = end
        dx, dy, dz = ex - sx, ey - sy, ez - sz

        points = [(sx, sy, sz)]
        rng = random.Random(int(sx * 100 + sy * 37 + sz * 53 + self.time * 10))
        for i in range(1, segments):
            t = i / segments
            j = (1 - abs(t - 0.5) * 2) * jitter * 3
            px = sx + dx * t + rng.uniform(-j, j)
            py = sy + dy * t + rng.uniform(-j * 0.5, j * 0.5)
            pz = sz + dz * t + rng.uniform(-j, j)
            points.append((px, py, pz))
        points.append((ex, ey, ez))

        brightness = random.uniform(0.7, 1.0)
        core = (brightness, brightness * 0.9, brightness)
        glow = (brightness * 0.4, brightness * 0.3, brightness * 0.8)

        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i + 1]
            verts.extend([*p0, *core, *p1, *core])
            off = 0.3 + (i / len(points)) * 0.5
            verts.extend([*p0, glow[0] * off, glow[1] * off, glow[2] * off])
            verts.extend([*p1, glow[0] * off, glow[1] * off, glow[2] * off])

        return np.array(verts, dtype='f4')

    def update(self, dt):
        self.time += dt

        for bolt in list(self.bolts):
            bolt['life'] -= dt
            if bolt['life'] <= 0:
                self.bolts.remove(bolt)

        if self.time >= self.next_flash:
            self.next_flash = self.time + random.uniform(0.5, 3.0)

            cx, cy, cz = self.center
            sx = cx + random.uniform(-self.spread, self.spread)
            sz = cz + random.uniform(-self.spread, self.spread)
            sy = cy + random.uniform(-20, 20)

            ex = sx + random.uniform(-self.spread * 0.5, self.spread * 0.5)
            ez = sz + random.uniform(-self.spread * 0.5, self.spread * 0.5)
            ey = random.uniform(self.height_range[0], self.height_range[1])

            verts = self._generate_bolt((sx, sy, sz), (ex, ey, ez))
            vbo = self.ctx.buffer(verts.tobytes())
            vao = self.ctx.vertex_array(
                self.program,
                [(vbo, '3f 3f', 'in_position', 'in_color')]
            )
            self.bolts.append({
                'vao': vao,
                'count': len(verts) // 6,
                'life': random.uniform(0.1, 0.25),
                'vbo': vbo
            })

            if random.random() < 0.4:
                branch_end = (ex + random.uniform(-10, 10), ey - random.uniform(10, 30), ez + random.uniform(-10, 10))
                bverts = self._generate_bolt((ex, ey, ez), branch_end, segments=4, jitter=2.0)
                bvbo = self.ctx.buffer(bverts.tobytes())
                bvao = self.ctx.vertex_array(
                    self.program,
                    [(bvbo, '3f 3f', 'in_position', 'in_color')]
                )
                self.bolts.append({
                    'vao': bvao,
                    'count': len(bverts) // 6,
                    'life': random.uniform(0.08, 0.15),
                    'vbo': bvbo
                })

    def render(self):
        for bolt in self.bolts:
            alpha = min(1.0, bolt['life'] * 8.0)
            if alpha > 0:
                bolt['vao'].render(mode=self.ctx.LINES)
