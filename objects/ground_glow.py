import math
import numpy as np

class GroundGlow:
    def __init__(self, ctx, program, center=(0.0, 100.0, 0.0), radius=30.0,
                 color=(1.0, 0.4, 0.05), intensity=1.0, segments=32):
        verts, idxs = self._generate(radius, segments)
        self.index_count = len(idxs)
        self.color = color
        self.intensity = intensity

        self.vbo = ctx.buffer(verts.tobytes())
        self.ibo = ctx.buffer(idxs.tobytes())
        self.vao = ctx.vertex_array(
            program,
            [(self.vbo, '3f 2f', 'in_position', 'in_texcoord')],
            index_buffer=self.ibo
        )

        self.model_matrix = np.identity(4, dtype='f4')
        self.model_matrix[3, 0] = center[0]
        self.model_matrix[3, 1] = center[1]
        self.model_matrix[3, 2] = center[2]

    def _generate(self, radius, segs):
        verts = []
        idxs = []
        verts.extend([0.0, 0.0, 0.0, 0.5, 0.5])

        for i in range(segs):
            a = 2 * math.pi * i / segs
            x = math.cos(a) * radius
            z = math.sin(a) * radius
            u = 0.5 + math.cos(a) * 0.5
            v = 0.5 + math.sin(a) * 0.5
            verts.extend([x, 0.0, z, u, v])

        for i in range(1, segs):
            idxs.extend([0, i, i + 1])
        idxs.extend([0, segs, 1])

        return np.array(verts, dtype='f4'), np.array(idxs, dtype='i4')
