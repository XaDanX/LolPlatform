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
class Spell:
    ready_time: float
    level: int
    name: str
    spell_true_damage: float
    cool_down: float


class Object:

    def __init__(self, base):
        self.base = base
        self._name = ""

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
        if self._name == "":
            try:
                name_ptr = await Memory().read(self.base + offsets.obj_name, "int")
                name = await Memory().read_string(name_ptr, 16)
            except (UnicodeDecodeError, pymem.exception.MemoryReadError):
                name = ""
            self._name = name if name != "" else "LObject"

        return self._name

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
        _spell = await Memory().read(self.base + offsets.obj_spellbook + 0x488 + (0x4 * slot), "int")
        spell = await Memory().read_bytes(_spell, offsets.SPELL_DATA_SIZE)
        spell_info = await Memory().read_bytes(int_from_buffer(spell, offsets.spell_info), offsets.SPELL_DATA_SIZE)
        spell_data = await Memory().read_bytes(int_from_buffer(spell_info, offsets.spell_data), offsets.SPELL_DATA_SIZE)

        ready_at = float_from_buffer(spell, offsets.spell_ready_at)
        level = int_from_buffer(spell, offsets.spell_level)
        spell_true_damage = float_from_buffer(spell, offsets.spell_true_damage)
        spell_name = await Memory().read_string(int_from_buffer(spell_data, offsets.spell_name), 16)

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

    async def pos(self):
        pos = await Memory().read_bytes(self.base + offsets.obj_pos, 16)
        x = float_from_buffer(pos, 0x0)
        y = float_from_buffer(pos, 0x4)
        z = float_from_buffer(pos, 0x8)
        return Vec3(x, y, z)

    async def hp_bar_pos(self):
        pos = await self.pos()
        pos.y += 140
        render = await game.Game.render()

        screen_pos = w2s(pos, render.view_proj_matrix)
        if screen_pos:
            screen_pos.y -= (render.height * 0.00083333335 * 140)
            return screen_pos
        return None

    async def is_visible(self):
        visibility = await Memory().read(self.base + offsets.obj_visibility, "short")

        if visibility >= 257:
            return True
        else:
            return False

    async def attack_speed_multi(self):
        return await Memory().read(self.base + offsets.obj_attack_speed_multi, "float")

    async def armor(self):
        return await Memory().read(self.base + offsets.obj_armor, "float")

    async def attack_damage(self):
        return await Memory().read(self.base + offsets.obj_attack_damage, "float")

    async def bonus_attack_damage(self):
        return await Memory().read(self.base + offsets.obj_bonus_attack_damage, "float")

    async def crit_chance(self):
        return await Memory().read(self.base + offsets.obj_crit_chance, "float")

    @staticmethod
    async def in_basic_attack_range(obj1, obj2):
        obj1_radius = 55
        obj2_radius = 55
        attk_range = await obj1.attack_range()
        dist_between = await Object.distance_between(obj1, obj2)
        return dist_between - obj2_radius <= attk_range + obj1_radius

    @staticmethod
    async def in_range(obj1, obj2, spell_range, obj_radius=55):  # TODO: get radius from obj
        dist_between = await Object.distance_between(obj1, obj2)
        return dist_between - obj_radius <= spell_range + obj_radius

    @staticmethod
    async def distance_between(obj1, obj2):
        obj1_pos = await obj1.pos()
        obj2_pos = await obj2.pos()
        return math.sqrt((obj1_pos.x - obj2_pos.x) ** 2 + (obj1_pos.y - obj2_pos.y) ** 2)

    @staticmethod
    def distance_between_vec(vec1, vec2):
        return math.sqrt((vec1.x - vec2.x) ** 2 + (vec1.y - vec2.y) ** 2)

    @staticmethod
    def in_range_vec(vec1, vec2, spell_range, obj_radius=0):
        dist_between = Object.distance_between_vec(vec1, vec2)
        return dist_between + obj_radius <= spell_range + obj_radius

    @staticmethod
    def effective_damage(damage, armor):
        if armor >= 0:
            return damage * 100 / (100 + armor)
        return damage * (2 - (100 / (100 - armor)))


class LocalPlayer(Object):

    def __init__(self, base):
        super().__init__(base)
