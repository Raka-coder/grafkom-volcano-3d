import moderngl
import numpy as np
from .shader import ShaderProgram
from .shadow import ShadowMap

class Renderer:
    def __init__(self, ctx):
        self.ctx = ctx
        self.terrain_shader = None
        self.particle_shader = None
        self.sky_shader = None
        self.object_shader = None
        self.lava_shader = None
        self.unlit_shader = None
        self.glow_shader = None
        self.sky_vao = None
        self.objects = []
        self.lava_flows = []
        self.glow_decals = []
        self.lightning = None
        self.ash_intensity = 0.0
        self.ash_radius = 60.0

    def init_shaders(self):
        self.terrain_shader = ShaderProgram(self.ctx, 'shaders/terrain.vert', 'shaders/terrain.frag')
        self.particle_shader = ShaderProgram(self.ctx, 'shaders/particle.vert', 'shaders/particle.frag')
        self.sky_shader = ShaderProgram(self.ctx, 'shaders/sky.vert', 'shaders/sky.frag')
        self.object_shader = ShaderProgram(self.ctx, 'shaders/object.vert', 'shaders/object.frag')
        self.lava_shader = ShaderProgram(self.ctx, 'shaders/lava.vert', 'shaders/lava.frag')
        self.unlit_shader = ShaderProgram(self.ctx, 'shaders/unlit.vert', 'shaders/unlit.frag')
        self.glow_shader = ShaderProgram(self.ctx, 'shaders/glow.vert', 'shaders/glow.frag')
        self.shadow_shader = ShaderProgram(self.ctx, 'shaders/shadow.vert', 'shaders/shadow.frag')

        sky_vertices = np.array([
            -2000.0, 300.0, -2000.0,  0.0, 0.0,
             2000.0, 300.0, -2000.0, 10.0, 0.0,
            -2000.0, 300.0,  2000.0,  0.0, 10.0,
             2000.0, 300.0,  2000.0, 10.0, 10.0,
        ], dtype='f4')
        self.sky_vbo = self.ctx.buffer(sky_vertices.tobytes())
        self.sky_vao = self.ctx.vertex_array(
            self.sky_shader.program,
            [(self.sky_vbo, '3f 2f', 'in_position', 'in_texcoord')]
        )

    def add_object(self, obj):
        self.objects.append(obj)

    def add_lava(self, lava_flow):
        self.lava_flows.append(lava_flow)

    def add_glow(self, decal):
        self.glow_decals.append(decal)

    def set_lightning(self, lightning):
        self.lightning = lightning

    def init_shadow(self, terrain_vbo, terrain_ibo, size=2048):
        self.shadow_map = ShadowMap(self.ctx, self.shadow_shader.program, terrain_vbo, terrain_ibo, size)

    def render_shadow_map(self):
        if not hasattr(self, 'shadow_map'):
            return
        old_fbo = self.ctx.detect_framebuffer()
        self.shadow_map.render()
        old_fbo.use()

    def set_shadow_uniforms(self, program):
        if hasattr(self, 'shadow_map'):
            program.set_uniform('shadow_map', 4)
            program.set_uniform('light_space', self.shadow_map.light_matrix.T.tobytes())
            program.set_uniform('shadows_enabled', True)

    def render_sky(self, camera, time):
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.disable(moderngl.CULL_FACE)

        prog = self.sky_shader
        prog.set_uniform('projection', camera.get_projection_matrix().astype('f4').T.tobytes())
        prog.set_uniform('view', camera.get_view_matrix().astype('f4').T.tobytes())
        prog.set_uniform('cam_pos', tuple(camera.position))
        prog.set_uniform('time', time)
        prog.set_uniform('fog_color', (0.7, 0.8, 0.95))

        self.sky_vao.render(moderngl.TRIANGLE_STRIP)
        self.ctx.enable(moderngl.CULL_FACE)
        self.ctx.enable(moderngl.DEPTH_TEST)

    def render_terrain(self, terrain_mesh, camera, light_pos, time):
        self.ctx.disable(moderngl.BLEND)
        if hasattr(self, 'shadow_map'):
            self.shadow_map.depth_tex.use(location=4)

        prog = self.terrain_shader

        prog.set_uniform('m_proj', camera.get_projection_matrix().astype('f4').T.tobytes())
        prog.set_uniform('m_view', camera.get_view_matrix().astype('f4').T.tobytes())

        m_model = np.identity(4, dtype='f4')
        prog.set_uniform('m_model', m_model.T.tobytes())

        prog.set_uniform('cam_pos', tuple(camera.position))
        prog.set_uniform('light_pos', tuple(light_pos))
        prog.set_uniform('time', time)
        prog.set_uniform('ash_intensity', self.ash_intensity)
        prog.set_uniform('ash_radius', self.ash_radius)

        self.set_shadow_uniforms(prog)

        terrain_mesh.render()

    def render_objects(self, camera):
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.disable(moderngl.BLEND)
        if hasattr(self, 'shadow_map'):
            self.shadow_map.depth_tex.use(location=4)

        prog = self.object_shader
        proj = camera.get_projection_matrix().astype('f4').T.tobytes()
        view = camera.get_view_matrix().astype('f4').T.tobytes()
        prog.set_uniform('m_proj', proj)
        prog.set_uniform('m_view', view)
        prog.set_uniform('cam_pos', tuple(camera.position))

        self.set_shadow_uniforms(prog)

        for obj in self.objects:
            prog.set_uniform('m_model', obj.model_matrix.T.tobytes())
            obj.render()

    def render_lava(self, camera, time):
        if not self.lava_flows:
            return

        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE

        proj = camera.get_projection_matrix().astype('f4').T.tobytes()
        view = camera.get_view_matrix().astype('f4').T.tobytes()
        m_model = np.identity(4, dtype='f4')

        prog = self.lava_shader
        prog.set_uniform('m_proj', proj)
        prog.set_uniform('m_view', view)
        prog.set_uniform('m_model', m_model.T.tobytes())
        prog.set_uniform('time', time)
        for lava in self.lava_flows:
            lava.vao.render(mode=self.ctx.TRIANGLES)

        prog = self.glow_shader
        prog.set_uniform('m_proj', proj)
        prog.set_uniform('m_view', view)
        prog.set_uniform('time', time)
        for decal in self.glow_decals:
            prog.set_uniform('m_model', decal.model_matrix.T.tobytes())
            prog.set_uniform('glow_color', decal.color)
            prog.set_uniform('intensity', decal.intensity)
            decal.vao.render(mode=self.ctx.TRIANGLES)

        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    def render_lightning(self, camera):
        if not self.lightning:
            return

        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE

        self.unlit_shader.set_uniform('m_proj', camera.get_projection_matrix().astype('f4').T.tobytes())
        self.unlit_shader.set_uniform('m_view', camera.get_view_matrix().astype('f4').T.tobytes())
        self.unlit_shader.set_uniform('alpha', 1.0)

        self.lightning.render()

        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    def render_particles(self, particle_system, camera, time=0.0):
        self.ctx.enable(moderngl.BLEND)

        prog = self.particle_shader
        prog.set_uniform('m_proj', camera.get_projection_matrix().astype('f4').T.tobytes())
        prog.set_uniform('m_view', camera.get_view_matrix().astype('f4').T.tobytes())
        prog.set_uniform('time', time)

        particle_system.render()
