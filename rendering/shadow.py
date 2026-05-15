import numpy as np
import math

class ShadowMap:
    def __init__(self, ctx, shadow_program, terrain_vbo, terrain_ibo, size=2048):
        self.ctx = ctx
        self.size = size

        self.depth_tex = ctx.depth_texture((size, size))
        self.depth_tex.repeat_x = False
        self.depth_tex.repeat_y = False
        self.depth_tex.filter = (ctx.NEAREST, ctx.NEAREST)

        self.fbo = ctx.framebuffer(depth_attachment=self.depth_tex)

        self.shadow_vao = ctx.vertex_array(
            shadow_program,
            [(terrain_vbo, '3f 5x', 'in_position')],
            index_buffer=terrain_ibo
        )
        self.index_count = terrain_ibo.size // 4

    def compute_light_matrix(self, light_dir, scene_center, scene_radius):
        light_dir = np.array(light_dir, dtype='f4')
        light_dir = light_dir / np.linalg.norm(light_dir)

        eye = np.array(scene_center, dtype='f4') - light_dir * scene_radius * 2.5
        target = np.array(scene_center, dtype='f4')
        world_up = np.array([0.0, 1.0, 0.0], dtype='f4')

        f = target - eye
        f = f / np.linalg.norm(f)
        s = np.cross(f, world_up)
        s = s / np.linalg.norm(s)
        u = np.cross(s, f)

        view = np.identity(4, dtype='f4')
        view[0, 0:3] = s
        view[1, 0:3] = u
        view[2, 0:3] = -f
        view[0:3, 3] = [-np.dot(s, eye), -np.dot(u, eye), np.dot(f, eye)]

        r = scene_radius
        proj = np.zeros((4, 4), dtype='f4')
        proj[0, 0] = 1.0 / r
        proj[1, 1] = 1.0 / r
        proj[2, 2] = -2.0 / (r * 4)
        proj[2, 3] = -(r * 4 + 0.0) / (r * 4)
        proj[3, 2] = -1.0

        bias = np.array([
            [0.5, 0, 0, 0.5],
            [0, 0.5, 0, 0.5],
            [0, 0, 0.5, 0.5],
            [0, 0, 0, 1]
        ], dtype='f4')

        self.light_matrix = bias @ proj @ view
        self.light_space_raw = proj @ view

    def render(self):
        old_viewport = self.ctx.viewport
        self.fbo.use()
        self.ctx.viewport = (0, 0, self.size, self.size)
        self.ctx.clear(depth=1.0)
        self.ctx.disable(self.ctx.BLEND)
        self.ctx.enable(self.ctx.DEPTH_TEST)
        self.ctx.disable(self.ctx.CULL_FACE)

        self.shadow_vao.render(mode=self.ctx.TRIANGLES)

        self.ctx.enable(self.ctx.CULL_FACE)
        self.ctx.viewport = old_viewport
