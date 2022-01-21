
import glfw

import ovr
from ovr.triangle_drawer_compatibility import TriangleDrawerCompatibility
from ovr.rift_gl_renderer_compatibility import RiftGLRendererCompatibility


class GlfwApp(object):

    @ovr.LogCallback
    def log_callback(userData, level, message):
        if (message is not None):
            print(message.decode("utf-8"))

    def key_callback(self, window, key, scancode, action, mods):
        "press ESCAPE to quit the application"
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

    def run(self):
        params = ovr.InitParams()
        params.Flags = ovr.Init_Debug | ovr.Init_RequestVersion | ovr.Init_FocusAware
        params.LogCallback = self.log_callback
        params.UserData = None
        params.RequestedMinorVersion = ovr.MINOR_VERSION
        params.ConnectionTimeoutMS = 0

        renderer = RiftGLRendererCompatibility(params)

        # Initialize the library
        if not glfw.init():
            return

        # Create a windowed mode window and its OpenGL context
        windowSize = ovr.Sizei();
        windowSize.w = int(renderer.rift.get_resolution().w / 2)
        windowSize.h = int(renderer.rift.get_resolution().h / 2)
        self.window = glfw.create_window(windowSize.w, windowSize.h, "Hello World", None, None)
        if not self.window:
            glfw.terminate()
            return
    
        renderer.append(TriangleDrawerCompatibility())
    
        # Make the window's context current
        glfw.make_context_current(self.window)
    
        # Initialize Oculus Rift
        renderer.init_gl(windowSize)
        renderer.rift.recenter_pose()
        
        glfw.set_key_callback(self.window, self.key_callback)
    
        # Loop until the user closes the window
        while not glfw.window_should_close(self.window):
            # Render here, e.g. using pyOpenGL
            renderer.display_rift_gl(windowSize.w, windowSize.h)
    
            # Swap front and back buffers
            glfw.swap_buffers(self.window)
    
            # Poll for and process events
            glfw.poll_events()

        renderer.dispose_gl()

        glfw.terminate()

if __name__ == "__main__":
    GlfwApp().run()
