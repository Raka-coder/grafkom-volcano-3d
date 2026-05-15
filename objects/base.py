import numpy as np

class GameObject:
    def __init__(self, ctx, program, vertices, indices):
        self.ctx = ctx
        self.program = program
        self.index_count = len(indices)

        self.vbo = ctx.buffer(vertices.tobytes())
        self.ibo = ctx.buffer(indices.tobytes())
        self.vao = ctx.vertex_array(
            program,
            [(self.vbo, '3f 3f 3f', 'in_position', 'in_normal', 'in_color')],
            index_buffer=self.ibo
        )

        self._pos = [0.0, 0.0, 0.0]
        self._rot = [0.0, 0.0, 0.0]
        self._scale = 1.0
        self.model_matrix = np.identity(4, dtype='f4')

    def _build_matrix(self):
        cx, cy, cz = self._pos
        rx, ry, rz = np.radians(self._rot[0]), np.radians(self._rot[1]), np.radians(self._rot[2])
        s = self._scale

        cxr, sxr = np.cos(rx), np.sin(rx)
        cyr, syr = np.cos(ry), np.sin(ry)
        czr, szr = np.cos(rz), np.sin(rz)

        m = np.identity(4, dtype='f4')

        m00 = cyr*czr + syr*sxr*szr
        m01 = -cyr*szr + syr*sxr*czr
        m02 = syr*cxr
        m10 = cxr*szr
        m11 = cxr*czr
        m12 = -sxr
        m20 = -syr*czr + cyr*sxr*szr
        m21 = syr*szr + cyr*sxr*czr
        m22 = cyr*cxr

        m[0, 0] = m00 * s
        m[0, 1] = m01 * s
        m[0, 2] = m02 * s
        m[0, 3] = cx
        m[1, 0] = m10 * s
        m[1, 1] = m11 * s
        m[1, 2] = m12 * s
        m[1, 3] = cy
        m[2, 0] = m20 * s
        m[2, 1] = m21 * s
        m[2, 2] = m22 * s
        m[2, 3] = cz

        self.model_matrix = m

    def set_position(self, x, y, z):
        self._pos = [x, y, z]
        self._build_matrix()

    def set_rotation(self, x_deg=0, y_deg=0, z_deg=0):
        self._rot = [x_deg, y_deg, z_deg]
        self._build_matrix()

    def set_rotation_y(self, deg):
        self._rot[1] = deg
        self._build_matrix()

    def set_scale(self, s):
        self._scale = s
        self._build_matrix()

    def render(self):
        self.vao.render(mode=self.ctx.TRIANGLES)
