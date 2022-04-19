import math
from functools import lru_cache

import pymem

import sdk.offsets as offsets
from memory.memory import Memory
from dataclasses import dataclass
import sdk.game as game
from sdk.utils import Vec3


@dataclass
class Spell:
    ready_time: float
    level: int
    name: str
    spell_true_damage: float
    cool_down: float


class Object:

    def __init__(self, base):
        self.base = base

    async def health(self):
        health = await Memory().read(self.base + offsets.obj_health, "float")
        return health

    async def max_health(self):
        max_health = await Memory().read(self.base + offsets.obj_max_health, "float")
        return max_health

    async def team(self):
        team = await Memory().read(self.base + offsets.obj_team, "short")
        return team

    async def name(self):
        try:
            name_ptr = await Memory().read(self.base + offsets.obj_name, "int")
            name = await Memory().read_string(name_ptr, 16)
        except (UnicodeDecodeError, pymem.exception.MemoryReadError):
            name = ""

        return name if name != "" else "LObject"

    async def is_alive(self):
        spawn_count = await Memory().read(self.base + offsets.obj_spawn_count, "int")
        return spawn_count % 2 == 0

    async def attack_range(self):
        attack_range = await Memory().read(self.base + offsets.obj_attack_range, "float")
        return attack_range

    """
        spell book
    """

    async def spell_book(self):
        spell_book = await Memory().read(self.base + offsets.obj_spellbook, "int")
        return spell_book

    async def get_spell_by_slot(self, slot):
        #  [[[[<league of legends.exe> + 0x30F5BBC] + 0x2338 + 0x488 + (0x4*0)] + 0x120] + 0x44]
        spell = await Memory().read(self.base + offsets.obj_spellbook + 0x488 + (0x4 * slot), "int")
        ready_at = await Memory().read(spell + offsets.spell_ready_at, "float")
        level = await Memory().read(spell + offsets.spell_level, "int")
        spell_true_damage = await Memory().read(spell + offsets.spell_true_damage, "float")

        spell_info = await Memory().read(spell + offsets.spell_info, "int")
        spell_data = await Memory().read(spell_info + offsets.spell_data, "int")

        spell_name_ptr = await Memory().read(spell_data + offsets.spell_name, "int")
        spell_name = await Memory().read_string(spell_name_ptr, 16)

        cool_down = ready_at - await game.Game.time()

        spell = Spell(ready_at, level, spell_name, spell_true_damage, cool_down if 0 < cool_down else 0)

        return spell

    async def is_spell_ready(self, slot):
        spell = await Memory().read(self.base + offsets.obj_spellbook + 0x488 + (0x4 * slot), "int")
        ready_at = await Memory().read(spell + offsets.spell_ready_at, "float")
        curr_time = await game.Game.time()
        if curr_time >= ready_at:
            return True
        else:
            return False

    async def spell_ready_in(self, slot):

        spell = await Memory().read(self.base + offsets.obj_spellbook + 0x488 + (0x4 * slot), "int")
        ready_at = await Memory().read(spell + offsets.spell_ready_at, "float")
        curr_time = await game.Game.time()
        if curr_time <= ready_at:
            return ready_at - curr_time
        else:
            return 0

    async def read_pos(self):
        x = await Memory().read(self.base + offsets.obj_pos, "float")
        y = await Memory().read(self.base + offsets.obj_pos + 0x4, "float")
        z = await Memory().read(self.base + offsets.obj_pos + 0x8, "float")
        return Vec3(x, y, z)

    async def is_visible(self):
        visibility = await Memory().read(self.base + offsets.obj_visibility, "int")
        if visibility >= 257:
            return True
        else:
            return False

    async def attack_speed_multi(self):
        return await Memory().read(self.base + offsets.obj_attack_speed_multi, "float")

    @staticmethod
    async def in_basic_attack_range(obj1, obj2):
        obj1_radius = 55
        obj2_radius = 55
        attk_range = await obj1.attack_range()
        dist_between = await Object.distance_between(obj1, obj2)
        return dist_between - obj2_radius <= attk_range + obj1_radius

    @staticmethod
    async def distance_between(obj1, obj2):
        obj1_pos = await obj1.read_pos()
        obj2_pos = await obj2.read_pos()
        return math.sqrt((obj1_pos.x - obj2_pos.x)**2 + (obj1_pos.y - obj2_pos.y)**2)


class LocalPlayer(Object):

    def __init__(self, base):
        super().__init__(base)
