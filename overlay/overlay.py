import asyncio
import dataclasses
import imgui
import arrow
from glfw import *
from imgui.integrations.glfw import GlfwRenderer
from win32api import *
from win32con import *
from win32gui import *
from OpenGL.GL import *

import sdk.sdk as sdk
from memory.memory import Memory


@dataclasses.dataclass
class Result:
    width: int
    height: int
    mid_x: int
    mid_y: int


def rgb_to_float(data):
    result = []
    for _ in data:
        result.append(int(_) / 255)

    return result


def setup_style():
    style = imgui.get_style()

    style.scrollbar_rounding = 0
    style.frame_border_size = 0
    style.window_rounding = 0
    style.frame_rounding = 0
    style.frame_padding = (8, 6)
    style.window_title_align = (0.5, 0.5)
    style.alpha = 0.95
    # style.window_min_size = (400, 500)

    style.colors[imgui.COLOR_TITLE_BACKGROUND] = rgb_to_float([227, 0, 0, 255])
    style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = rgb_to_float([227, 0, 0, 255])

    style.colors[imgui.COLOR_WINDOW_BACKGROUND] = rgb_to_float([12, 12, 12, 240])

    style.colors[imgui.COLOR_BUTTON] = rgb_to_float([12, 12, 12, 255])
    style.colors[imgui.COLOR_BUTTON_ACTIVE] = rgb_to_float([190, 12, 12, 255])
    style.colors[imgui.COLOR_BUTTON_HOVERED] = rgb_to_float([90, 12, 12, 255])

    style.colors[imgui.COLOR_CHECK_MARK] = rgb_to_float([255, 255, 255, 255])

    style.colors[imgui.COLOR_FRAME_BACKGROUND] = rgb_to_float([36, 37, 36, 255])
    style.colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = rgb_to_float([36, 37, 36, 255])
    style.colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = rgb_to_float([36, 37, 36, 255])

    style.colors[imgui.COLOR_HEADER] = rgb_to_float([24, 24, 24, 255])
    style.colors[imgui.COLOR_HEADER_ACTIVE] = rgb_to_float([54, 53, 55, 255])
    style.colors[imgui.COLOR_HEADER_HOVERED] = rgb_to_float([24, 24, 24, 100])

    style.colors[imgui.COLOR_RESIZE_GRIP] = rgb_to_float([51, 49, 50, 255])
    style.colors[imgui.COLOR_RESIZE_GRIP_ACTIVE] = rgb_to_float([164, 22, 22, 255])
    style.colors[imgui.COLOR_RESIZE_GRIP_HOVERED] = rgb_to_float([160, 22, 22, 255])

    style.colors[imgui.COLOR_SLIDER_GRAB] = rgb_to_float([249, 79, 49, 255])
    style.colors[imgui.COLOR_SLIDER_GRAB_ACTIVE] = rgb_to_float([249, 79, 49, 255])

    style.colors[imgui.COLOR_BORDER] = rgb_to_float([54, 54, 54, 255])
    style.colors[imgui.COLOR_SEPARATOR] = rgb_to_float([54, 54, 54, 255])
    style.colors[imgui.COLOR_SEPARATOR_ACTIVE] = rgb_to_float([54, 54, 54, 255])
    style.colors[imgui.COLOR_SEPARATOR_HOVERED] = rgb_to_float([54, 54, 54, 255])


class Overlay:
    def __init__(self, target, overlay_name="Overlay"):
        init()

        self.show_menu = False

        self.is_visible = True

        imgui.create_context()

        window_hint(FLOATING, True)
        window_hint(RESIZABLE, False)
        window_hint(DECORATED, False)
        window_hint(TRANSPARENT_FRAMEBUFFER, True)
        window_hint(SAMPLES, 8)
        self.target = target
        self.hwnd = FindWindow(None, target)
        self.rect = GetWindowRect(self.hwnd)
        width = self.rect[2]
        height = self.rect[3]
        mid_x = width / 2
        mid_y = height / 2
        self.result = Result(width - self.rect[0], height - self.rect[1], mid_x, mid_y)

        self.window = create_window(width - 1,
                                    height - 1, overlay_name, None, None)

        self.window_handle = FindWindow(None, overlay_name)

        # set_input_mode(self.window, CURSOR, CURSOR_DISABLED)
        make_context_current(self.window)
        swap_interval(0)

        exstyle = GetWindowLong(self.window_handle, GWL_EXSTYLE)
        exstyle |= WS_EX_LAYERED
        exstyle |= WS_EX_TRANSPARENT
        SetWindowLong(self.window_handle, GWL_EXSTYLE, exstyle)
        SetWindowLong(self.window_handle, GWL_EXSTYLE,
                      exstyle | WS_EX_LAYERED)

        self.glInit()
        self.io = imgui.get_io()

        setup_style()

        self.select_index = 0

    def craft_font(self, size):
        font = self.io.fonts.add_font_from_file_ttf(
            "Ruda-Bold.ttf", size,
        )
        self.impl.refresh_font_texture()
        return font

    def hide(self):
        ShowWindow(self.window_handle, SW_HIDE)

    def show(self):
        ShowWindow(self.window_handle, SW_SHOW)

    def glInit(self):
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.result.width, self.result.height, 0, 1, -1)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        SetWindowPos(self.window_handle, -1, self.rect[0], self.rect[1], 0, 0, 0x0001)

        self.impl = GlfwRenderer(self.window)

    async def update(self):
        """
            drawings here
        """
        poll_events()
        self.impl.process_inputs()

        keystate = GetAsyncKeyState(0x2D) & 0x0001
        if keystate > 0:
            winlong = GetWindowLong(self.window_handle, GWL_EXSTYLE)

            if not self.show_menu:
                if winlong != WS_EX_LAYERED | WS_EX_TOPMOST:
                    SetWindowLong(self.window_handle, GWL_EXSTYLE, WS_EX_LAYERED | WS_EX_TOPMOST)

            if self.show_menu:
                if winlong != WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TRANSPARENT:
                    SetWindowLong(self.window_handle, GWL_EXSTYLE, WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TRANSPARENT)

            self.show_menu = not self.show_menu

        #  Draw benchmark

        start = arrow.utcnow()
        try:
            if self.show_menu:
                imgui.begin("Benchmark")
                imgui.text(f"Total: {sdk.Sdk.BenchmarkData.total_time:.6f}ms")
                imgui.text(f"Render: {sdk.Sdk.BenchmarkData.render_time:.6f}ms")
                imgui.text(f"Script: {sdk.Sdk.BenchmarkData.script_update_time:.6f}ms")
                imgui.text(f"Object: {sdk.Sdk.BenchmarkData.object_manager_update_time:.6f}ms")
                imgui.text(f"Serial: {sdk.Sdk.BenchmarkData.object_manager_serialization_time:.6f}ms")
                imgui.text(f"Memory: {sdk.Sdk.BenchmarkData.memory_time:.6f}ms")
                imgui.text(f"MemCalls: {sdk.Sdk.BenchmarkData.memory_calls}")
                changed, sdk.Sdk.Internal.loop_update_rate = imgui.slider_int(
                    "ObjUpdateRate", sdk.Sdk.Internal.loop_update_rate, 1, 400
                )
                imgui.end()

                imgui.begin("Script Manager")
                items = [i for i in sdk.Sdk.Internal.script_manager.script_files.values()]
                item_names = [i.name for i in items]
                if out := imgui.combo("Script", self.select_index, item_names):
                    if out[0]:
                        self.select_index = out[1]

                    if imgui.button("Load"):
                        await sdk.Sdk.Internal.script_manager.load(items[self.select_index].load_path)
                    imgui.same_line()
                    if imgui.button("Unload"):
                        await sdk.Sdk.Internal.script_manager.unload(items[self.select_index].name)

                imgui.end()

            imgui.render()
            self.impl.render(imgui.get_draw_data())
        except:
            pass

        swap_buffers(self.window)
        glClear(GL_COLOR_BUFFER_BIT)
        sdk.Sdk.BenchmarkData.render_time = (arrow.utcnow() - start).total_seconds() * 1000
        await asyncio.sleep(0)

    def close(self):
        destroy_window(self.window)
