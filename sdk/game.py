import dataclasses
import struct
import time
from memory.memory import Memory
from sdk import offsets
import sdk.object as obj
import enum
from sdk.utils import float_from_buffer, int_from_buffer

from sdk.utils import benchmark, multiple_square_matrix
from utils.logger import Logger

SMITE_RANGE = 625


class SummonerSpell(enum.Enum):
    SMITE = ["SummonerSmite", "S5_SummonerSmite"]
    FLASH = "SummonerFlash"


@dataclasses.dataclass
class Render:
    width: int
    height: int
    view_matrix: tuple
    proj_matrix: tuple
    view_proj_matrix: list


class FastRender:
    def __init__(self):
        self.last_render: Render = Render(0, 0, (), (), [])

    def calculate_matrices_thread(self):
        while True:
            try:
                render_ptr = Memory.process.read_int(Memory.process.base_address + offsets.renderer)

                width = Memory.process.read_int(render_ptr + offsets.renderer_width)
                height = Memory.process.read_int(render_ptr + offsets.renderer_height)
                view_matrix = Memory.process.read_bytes(render_ptr + offsets.view_matrix, 64)
                view_matrix_unp = struct.unpack("16f", view_matrix)
                proj_view_matrix = Memory.process.read_bytes(render_ptr + offsets.proj_matrix, 64)
                proj_view_matrix_unp = struct.unpack("16f", proj_view_matrix)

                view_proj_matrix = multiple_square_matrix(view_matrix_unp, proj_view_matrix_unp, 4)

                self.last_render = Render(width, height, view_matrix_unp, proj_view_matrix_unp, view_proj_matrix)
                time.sleep(0.0001)
            except Exception as e:
                Logger.error(e)
                continue

    def get_render(self):
        return self.last_render


class Game:

    @classmethod
    async def time(cls):
        return await Memory().read(Memory.process.base_address + offsets.game_time, "float")

    @classmethod
    async def under_mouse_obj(cls):
        under_mouse_ptr = await Memory().read(Memory.process.base_address + offsets.under_mouse_obj, "int")
        if under_mouse_ptr != 0:
            obj_under_mouse = await Memory().read(under_mouse_ptr + 0x0C, "int")
            if obj_under_mouse != 0:
                return obj_under_mouse
            else:
                return None
        else:
            return None

    @classmethod
    async def render(cls):
        render_ptr = await Memory().read(Memory.process.base_address + offsets.renderer, "int")
        render = await Memory().read_bytes(render_ptr, offsets.RENDER_SIZE)

        width = int_from_buffer(render, offsets.renderer_width)
        height = int_from_buffer(render, offsets.renderer_height)

        view_matrix = struct.unpack("16f", await Memory().read_bytes(render_ptr + offsets.view_matrix, 64))
        proj_matrix = struct.unpack("16f", await Memory().read_bytes(render_ptr + offsets.proj_matrix, 64))
        view_proj_matrix = multiple_square_matrix(view_matrix, proj_matrix, 4)

        return Render(width, height, view_matrix, proj_matrix, view_proj_matrix)
