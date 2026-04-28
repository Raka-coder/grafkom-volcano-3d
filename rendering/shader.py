class ShaderProgram:
    """
    Membaca kode GLSL, meng-compile, dan menyambungkan vertex dan fragment shader.
    Mengelola upload nilai variabel uniform ke GPU.
    """
    def __init__(self, ctx, vert_file, frag_file):
        with open(vert_file, 'r') as f:
            vertex_shader = f.read()
        with open(frag_file, 'r') as f:
            fragment_shader = f.read()
            
        try:
            self.program = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        except Exception as e:
            print(f"Error compiling shader {vert_file} / {frag_file}:\n{e}")
            raise e

    def set_uniform(self, name, value):
        """Mengirim data (matrix, float, dll) ke uniform shader yang aktif"""
        if name in self.program:
            # Jika buffer bytes (seperti matrix), gunakan method write()
            if isinstance(value, bytes):
                self.program[name].write(value)
            else:
                self.program[name].value = value
