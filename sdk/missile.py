import math
from functools import lru_cache

import pymem

import sdk.offsets as offsets
from memory.memory import Memory
from dataclasses import dataclass
import sdk.game as game
from sdk.utils import Vec3, w2s
from sdk.utils import float_from_buffer, int_from_buffer, bool_from_buffer, double_from_buffer


@dataclass
class MissileData:
    src_index: int
    dest_index: int
    start_pos: Vec3
    end_pos: Vec3
    name: str


class Missile:

    def __init__(self, base):
        self.base = base
        self.missile_data = None
        self._name = ""

    async def load_object(self):
        obj = await Memory().read_bytes(self.base, offsets.MISSILE_SIZE)

        data_ptr = int_from_buffer(obj, offsets.spell_info_spell_data)

        try:
            name_ptr = Memory.process.read_int(data_ptr + offsets.missile_name)
            name = Memory.process.read_string(name_ptr, 50)
        except:
            name = ""

        self.missile_data = MissileData(
            src_index=int_from_buffer(obj, offsets.missile_src_index),
            dest_index=int_from_buffer(obj, offsets.missile_dest_index),
            start_pos=Vec3(float_from_buffer(obj, offsets.missile_start_pos + 0x00),
                           float_from_buffer(obj, offsets.missile_start_pos + 0x04),
                           float_from_buffer(obj, offsets.missile_start_pos + 0x08)),
            end_pos=Vec3(float_from_buffer(obj, offsets.missile_end_pos + 0x00),
                         float_from_buffer(obj, offsets.missile_end_pos + 0x04),
                         float_from_buffer(obj, offsets.missile_end_pos + 0x08)),
            name=name
        )

        return self.missile_data
