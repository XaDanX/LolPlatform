import math
from functools import lru_cache

import pymem

import sdk.offsets as offsets
from memory.memory import Memory
from dataclasses import dataclass
import sdk.game as game
from sdk.utils import Vec3, w2s
from sdk.utils import float_from_buffer, int_from_buffer, bool_from_buffer, double_from_buffer
from typing import List


@dataclass
class Spell:
    ready_time: float
    level: int
    name: str
    spell_damage: float
    ready_at: float


@dataclass
class SpellBook:
    q_spell: Spell
    w_spell: Spell
    e_spell: Spell
    r_spell: Spell
    summoner_spell_1: Spell
    summoner_spell_2: Spell


@dataclass
class ObjectData:  # TODO: spellbook
    base: int
    health: float
    max_health: float
    team: int
    name: str
    alive: bool
    visible: bool
    attack_range: float
    armor: float
    attack_damage: float
    bonus_attack_damage: float
    crit_chance: float
    position: Vec3
    movement_speed: float
    prev_pos: Vec3
    is_moving: bool
    attack_speed_multiplier: float


class Object:

    def __init__(self, base):
        self.base = base
        self.object_data = None
        self.spell_book = None

    async def load_object(self):
        if self.object_data:
            if self.object_data:
                prev_pos = self.object_data.position
            else:
                if self.object_data.position:
                    prev_pos = self.object_data.position
                else:
                    prev_pos = Vec3(0, 0, 0)
        else:
            prev_pos = Vec3(0, 0, 0)
        obj = await Memory().read_bytes(self.base, offsets.OBJECT_SIZE)

        try:
            name_ptr = int_from_buffer(obj, offsets.obj_name)
            name = await Memory().read_string(name_ptr, 50)
        except (UnicodeDecodeError, pymem.exception.MemoryReadError):
            name = "Unknown"

        self.object_data = ObjectData(
            base=self.base,
            health=float_from_buffer(obj, offsets.obj_health),
            max_health=float_from_buffer(obj, offsets.obj_max_health),
            team=int_from_buffer(obj, offsets.obj_team),
            name=name,
            alive=bool_from_buffer(obj, offsets.obj_spawn_count),
            visible=bool_from_buffer(obj, offsets.obj_visibility),
            attack_range=float_from_buffer(obj, offsets.obj_attack_range),
            armor=float_from_buffer(obj, offsets.obj_armor),
            attack_damage=float_from_buffer(obj, offsets.obj_attack_damage),
            bonus_attack_damage=float_from_buffer(obj, offsets.obj_bonus_attack_damage),
            crit_chance=float_from_buffer(obj, offsets.obj_crit_chance),
            position=Vec3(float_from_buffer(obj, offsets.obj_pos + 0x00),
                          float_from_buffer(obj, offsets.obj_pos + 0x04),
                          float_from_buffer(obj, offsets.obj_pos + 0x08)),
            movement_speed=float_from_buffer(obj, offsets.obj_move_speed),
            prev_pos=prev_pos,
            is_moving=int_from_buffer(obj, offsets.obj_is_moving),
            attack_speed_multiplier=float_from_buffer(obj, offsets.obj_attack_speed_multi)

        )

        return self.object_data

    async def load_spell_book(self, deep_load=False):
        # [[<league of legends.exe> + 0x30F9BDC] + 0x2338 + 0x488 + (0x4*0)]
        spell_list = list[Spell]()

        game_time = await game.Game.time()

        for i in range(0, 6):
            spell_ptr = await Memory().read(self.base + offsets.obj_spellbook + 0x488 + (0x4 * i), "int")
            spell = await Memory().read_bytes(spell_ptr, offsets.SPELL_DATA_SIZE)
            name = ""
            if deep_load:
                spell_info = await Memory().read_bytes(int_from_buffer(spell, offsets.spell_info),
                                                       offsets.SPELL_DATA_SIZE)
                spell_data = await Memory().read_bytes(int_from_buffer(spell_info, offsets.spell_data),
                                                       offsets.SPELL_DATA_SIZE)
                name = await Memory().read_string(int_from_buffer(spell_data, offsets.spell_name), 16)

            ready_time = float_from_buffer(spell, offsets.spell_ready_at)
            level = int_from_buffer(spell, offsets.spell_level)
            spell_damage = float_from_buffer(spell, offsets.spell_true_damage)

            ready_at = (ready_time - game_time)
            if ready_at < 0:
                ready_at = 0

            current_spell = Spell(ready_time, level, name, spell_damage, int(round(ready_at)))

            spell_list.append(current_spell)

        self.spell_book = SpellBook(
            spell_list[0],
            spell_list[1],
            spell_list[2],
            spell_list[3],
            spell_list[4],
            spell_list[5]
        )
        return self.spell_book

    async def get_spell_by_slot(self, slot, deep_load=False):
        #  [[[[<league of legends.exe> + 0x30F5BBC] + 0x2338 + 0x488 + (0x4*0)] + 0x120] + 0x44]

        _spell = await Memory().read(self.base + offsets.obj_spellbook + offsets.spell_slot + (0x4 * slot), "int")
        spell = await Memory().read_bytes(_spell, offsets.SPELL_DATA_SIZE)
        name = ""
        if deep_load:
            spell_info = await Memory().read_bytes(int_from_buffer(spell, offsets.spell_info), offsets.SPELL_DATA_SIZE)
            spell_data = await Memory().read_bytes(int_from_buffer(spell_info, offsets.spell_data),
                                                   offsets.SPELL_DATA_SIZE)
            spell_name = await Memory().read_string(int_from_buffer(spell_data, offsets.spell_name), 16)

        ready_at = float_from_buffer(spell, offsets.spell_ready_at)
        level = int_from_buffer(spell, offsets.spell_level)
        spell_damage = float_from_buffer(spell, offsets.spell_true_damage)

        return Spell(ready_at, level, name, spell_damage)

    async def get_ai_manager(self):  # incorrect
        try:
            uVar2 = int()
            puVar3 = int()
            num1 = offsets.ai_manager
            uStack4 = await Memory().read(
                self.base + (num1 + 8) + (await Memory().read(self.base + (num1 + 4), "long long")) * 4, "int")
            puVar3 = self.base + num1
            uVar2 = await Memory().read(puVar3, "int")
            uStack4 ^= ~uVar2
            return await Memory().read(uStack4 + 8, "int")
        except:
            return 0

    @staticmethod
    def in_basic_attack_range(obj1, obj2):
        obj1_radius = 55
        obj2_radius = 55
        attk_range = obj1.object_data.attack_range
        dist_between = Object.distance_between(obj1.object_data.position, obj2.object_data.position)
        return dist_between - obj2_radius <= attk_range + obj1_radius

    @staticmethod
    def in_range(obj1, obj2, spell_range, obj_radius=55):  # TODO: get radius from obj
        dist_between = Object.distance_between(obj1, obj2)
        return dist_between - obj_radius <= spell_range + obj_radius

    @staticmethod
    def distance_between(object_position1, object_position2):
        return math.sqrt(
            (object_position1.x - object_position2.x) ** 2 + (object_position1.y - object_position2.y) ** 2)

    @staticmethod
    def distance_between_vec(vec1, vec2):
        return math.sqrt((vec1.x - vec2.x) ** 2 + (vec1.y - vec2.y) ** 2)

    @staticmethod
    def effective_damage(damage, armor):
        if armor >= 0:
            damage_w_armor = 100 / (100 + armor)
            damage_a_armor = damage * damage_w_armor

            return damage_a_armor
        return damage * (2 - (100 / (100 - armor)))


class LocalPlayer(Object):

    def __init__(self, base):
        super().__init__(base)
