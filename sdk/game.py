import dataclasses
import struct

from memory.memory import Memory
from sdk import offsets
import sdk.object as obj
import enum

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
                return obj.Object(obj_under_mouse)
            else:
                return None
        else:
            return None

    @classmethod
    def _multiple_square_matrix(cls, a, b, size: int):
        if len(a) != size * size or len(b) != size * size:
            raise Exception("input error")

        result = []
        for i in range(size):
            for j in range(size):
                c = 0
                for k in range(size):
                    c += a[(i * size) + k] * b[(k * size) + j]
                result.append(c)

        return result

    @classmethod
    async def render(cls):
        render_ptr = await Memory().read(Memory.process.base_address + offsets.renderer, "int")
        width = await Memory().read(render_ptr + offsets.renderer_width, "int")
        height = await Memory().read(render_ptr + offsets.renderer_height, "int")

        view_matrix = await Memory().read_bytes(render_ptr + offsets.view_matrix, 64)
        view_matrix_unp = struct.unpack("16f", view_matrix)
        proj_view_matrix = await Memory().read_bytes(render_ptr + offsets.proj_matrix, 64)
        proj_view_matrix_unp = struct.unpack("16f", proj_view_matrix)

        view_proj_matrix = cls._multiple_square_matrix(view_matrix_unp, proj_view_matrix_unp, 4)

        return Render(width, height, view_matrix_unp, proj_view_matrix_unp, view_proj_matrix)
