class TerrainMesh:
    """
    Mengelola buffer data terrain (VBO, IBO) dan membungkusnya dalam Vertex Array Object (VAO)
    agar bisa dirender efisien oleh GPU.
    """
    def __init__(self, ctx, program, vertices, indices):
        self.ctx = ctx
        self.num_indices = len(indices)
        
        # Buffer untuk data vertex (pos, normal, texcoord)
        self.vbo = ctx.buffer(vertices.tobytes())
        # Buffer untuk indeks segitiga
        self.ibo = ctx.buffer(indices.tobytes())
        
        # Vertex Array Object: mengatur bagaimana buffer dibaca shader
        # '3f 3f 2f' artinya setiap titik ada 3 float (pos), 3 float (normal), 2 float (uv)
        self.vao = ctx.vertex_array(
            program,
            [(self.vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_texcoord')],
            index_buffer=self.ibo
        )

    def render(self):
        """Memanggil OpenGL draw call untuk VAO ini."""
        self.vao.render(mode=self.ctx.TRIANGLES)
