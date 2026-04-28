import moderngl
import numpy as np
from .shader import ShaderProgram

class Renderer:
    """
    Kelas utama rendering pipeline yang mengorkestrasi shader dan mesh.
    Mengatur proses render terrain dan partikel di setiap frame.
    """
    def __init__(self, ctx):
        self.ctx = ctx
        self.terrain_shader = None
        self.particle_shader = None
        self.sky_shader = None
        self.sky_vao = None

    def init_shaders(self):
        """Kompilasi semua shader utama."""
        self.terrain_shader = ShaderProgram(self.ctx, 'shaders/terrain.vert', 'shaders/terrain.frag')
        self.particle_shader = ShaderProgram(self.ctx, 'shaders/particle.vert', 'shaders/particle.frag')
        self.sky_shader = ShaderProgram(self.ctx, 'shaders/sky.vert', 'shaders/sky.frag')
        
        # Plane horizontal raksasa untuk langit di atas kepala
        # Format: pos_x, pos_y, pos_z, uv_u, uv_v
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

    def render_sky(self, camera, time):
        """Render langit dengan awan prosedural."""
        self.ctx.disable(moderngl.DEPTH_TEST) # Langit selalu di belakang
        
        prog = self.sky_shader
        prog.set_uniform('projection', camera.get_projection_matrix().astype('f4').T.tobytes())
        prog.set_uniform('view', camera.get_view_matrix().astype('f4').T.tobytes())
        prog.set_uniform('cam_pos', tuple(camera.position))
        prog.set_uniform('time', time)
        prog.set_uniform('fog_color', (0.5, 0.6, 0.7))
        
        self.sky_vao.render(moderngl.TRIANGLE_STRIP)
        self.ctx.enable(moderngl.DEPTH_TEST)

    def render_terrain(self, terrain_mesh, camera, light_pos, time):
        """Render terrain dengan passing matrix dan data lighting."""
        self.ctx.disable(moderngl.BLEND)
        
        prog = self.terrain_shader
        
        # Transpose matrix menjadi column-major (format OpenGL) dan jadikan bytes
        prog.set_uniform('m_proj', camera.get_projection_matrix().astype('f4').T.tobytes())
        prog.set_uniform('m_view', camera.get_view_matrix().astype('f4').T.tobytes())
        
        m_model = np.identity(4, dtype='f4')
        prog.set_uniform('m_model', m_model.T.tobytes())
        
        prog.set_uniform('cam_pos', tuple(camera.position))
        prog.set_uniform('light_pos', tuple(light_pos))
        prog.set_uniform('time', time)
        
        terrain_mesh.render()

    def render_particles(self, particle_system, camera):
        """Render particle system dengan point sprite (GL_POINTS)."""
        self.ctx.enable(moderngl.BLEND)
        
        prog = self.particle_shader
        prog.set_uniform('m_proj', camera.get_projection_matrix().astype('f4').T.tobytes())
        prog.set_uniform('m_view', camera.get_view_matrix().astype('f4').T.tobytes())
        
        particle_system.render()
