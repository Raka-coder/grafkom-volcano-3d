import glfw
import moderngl
import sys

class Window:
    """
    Kelas untuk mengatur window dan context OpenGL menggunakan GLFW.
    Mengelola input (keyboard, mouse) dan main loop.
    """
    def __init__(self, width=1280, height=720, title="Volcano Simulation"):
        self.width = width
        self.height = height
        
        # Inisialisasi GLFW
        if not glfw.init():
            sys.exit(1)
            
        # Konfigurasi versi OpenGL 3.3 Core Profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        
        # Membuat window
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            sys.exit(1)
            
        glfw.make_context_current(self.window)
        
        # Membuat ModernGL context
        self.ctx = moderngl.create_context()
        
        # Mengaktifkan Depth Test (Z-Buffer) agar objek depan menutupi belakang
        # Mengaktifkan Cull Face (menghilangkan render sisi belakang polygon)
        # Mengaktifkan Blend untuk alpha blending pada particle system
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE | moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Setup Input
        self.keys = {}
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_cursor_pos_callback(self.window, self.mouse_callback)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        
        self.mouse_dx = 0.0
        self.mouse_dy = 0.0
        self.last_mouse_x = width / 2.0
        self.last_mouse_y = height / 2.0
        self.first_mouse = True

        # Fullscreen state
        self._fullscreen = False
        self._fullscreen_requested = False
        self._windowed_x = 50
        self._windowed_y = 50
        self._windowed_w = width
        self._windowed_h = height

        glfw.set_framebuffer_size_callback(self.window, self._resize_callback)

    def _resize_callback(self, window, w, h):
        self.width = w
        self.height = h
        self.ctx.viewport = (0, 0, w, h)

    def _toggle_fullscreen(self):
        if not self._fullscreen:
            self._windowed_x, self._windowed_y = glfw.get_window_pos(self.window)
            self._windowed_w, self._windowed_h = self.width, self.height
            monitor = glfw.get_primary_monitor()
            mode = glfw.get_video_mode(monitor)
            glfw.set_window_monitor(
                self.window, monitor, 0, 0,
                mode.size.width, mode.size.height, mode.refresh_rate
            )
        else:
            glfw.set_window_monitor(
                self.window, None,
                self._windowed_x, self._windowed_y,
                self._windowed_w, self._windowed_h, 0
            )
        self._fullscreen = not self._fullscreen

    def key_callback(self, window, key, scancode, action, mods):
        """Callback saat tombol keyboard ditekan/dilepas"""
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)
        if key == glfw.KEY_F and action == glfw.PRESS:
            self._fullscreen_requested = True
        if action == glfw.PRESS:
            self.keys[key] = True
        elif action == glfw.RELEASE:
            self.keys[key] = False

    def mouse_callback(self, window, xpos, ypos):
        """Callback untuk melacak pergerakan mouse (pitch & yaw camera)"""
        if self.first_mouse:
            self.last_mouse_x = xpos
            self.last_mouse_y = ypos
            self.first_mouse = False
            
        self.mouse_dx = xpos - self.last_mouse_x
        # y-coordinates go from bottom to top
        self.mouse_dy = self.last_mouse_y - ypos 
        
        self.last_mouse_x = xpos
        self.last_mouse_y = ypos

    def is_running(self):
        """Mengecek apakah window masih terbuka"""
        return not glfw.window_should_close(self.window)

    def swap_buffers(self):
        """Menukar front/back buffer (Double Buffering)"""
        glfw.swap_buffers(self.window)

    def poll_events(self):
        """Memproses antrian event glfw"""
        if self._fullscreen_requested:
            self._toggle_fullscreen()
            self._fullscreen_requested = False
        self.mouse_dx = 0.0
        self.mouse_dy = 0.0
        glfw.poll_events()
        
    def get_time(self):
        """Mengambil waktu berjalan aplikasi (detik)"""
        return glfw.get_time()

    def terminate(self):
        """Menutup aplikasi dengan aman"""
        glfw.terminate()
