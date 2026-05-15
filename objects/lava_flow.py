import math
import numpy as np

class LavaFlow:
    def __init__(self, ctx, program, terrain_gen, center=(0.0, 0.0),
                 angle=0.0, start_r=18, end_r=85, segments=40,
                 width_start=2.0, width_end=6.0, curve=0.4):
        path = []
        widths = []
        for i in range(segments + 1):
            t = i / segments
            r = start_r + (end_r - start_r) * t
            a = angle + t * curve
            x = center[0] + r * math.cos(a)
            z = center[1] + r * math.sin(a)
            h = terrain_gen.get_height_at(x, z)
            path.append((x, h + 0.15, z))
            widths.append(width_start + (width_end - width_start) * t)

        verts, idxs = self._generate_mesh(path, widths)
        self.index_count = len(idxs)

        self.vbo = ctx.buffer(verts.tobytes())
        self.ibo = ctx.buffer(idxs.tobytes())
        self.vao = ctx.vertex_array(
            program,
            [(self.vbo, '3f 2f', 'in_position', 'in_texcoord')],
            index_buffer=self.ibo
        )

    def _generate_mesh(self, path, widths):
        verts = []
        idxs = []
        n = len(path)

        for i in range(n):
            x, y, z = path[i]
            w = widths[i]

            if i < n - 1:
                dx = path[i + 1][0] - x
                dz = path[i + 1][2] - z
            else:
                dx = x - path[i - 1][0]
                dz = z - path[i - 1][2]

            length = math.hypot(dx, dz) or 1
            px = -dz / length * w * 0.5
            pz = dx / length * w * 0.5

            t = i / (n - 1)
            verts.extend([x + px, y, z + pz, 0.0, t])
            verts.extend([x - px, y, z - pz, 1.0, t])

        for i in range(n - 1):
            i0 = i * 2
            i1 = i * 2 + 1
            i2 = (i + 1) * 2
            i3 = (i + 1) * 2 + 1
            idxs.extend([i0, i2, i1,  i2, i3, i1])

        return np.array(verts, dtype='f4'), np.array(idxs, dtype='i4')
