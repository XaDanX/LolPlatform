import asyncio
import time
from enum import Enum

import pymem
from pymem.exception import MemoryReadError
from recordclass import recordclass

from memory.memory import Memory
from sdk.object import Object
import sdk.offsets as offsets
from sdk.stats import ChampionStats, SpellData
import sdk.sdk as sdk

import arrow

from utils.logger import Logger

Node = recordclass('Node', 'address, next')


def linked_insert(current_node, next_address):
    next_node = Node(next_address, current_node.next)
    current_node.next = next_node


def int_from_buffer(data, offset):
    return int.from_bytes(data[offset:offset + 4], 'little')


# TODO: better obj manager..

class UnitData(Enum):
    TURRET = "Turret"
    ORDER_MINION = ["SRU_OrderMinionRanged", "SRU_OrderMinionMelee", "SRU_OrderMinionSiege"]
    CHAOS_MINION = ["SRU_ChaosMinionRanged", "SRU_ChaosMinionMelee", "SRU_ChaosMinionSiege"]
    JUNGLE_MONSTERS = ["SRU_Krug", "SRU_KrugMini", "SRU_Razorbeak", "SRU_RazorbeakMini",
                       "SRU_Murkwolf", "SRU_MurkwolfMini", "SRU_Gromp", "Sru_Crab", "SRU_Red", "SRU_Blue"]
    DRAGONS = ["SRU_Dragon_Air", "SRU_Dragon_Fire", "SRU_Dragon_Water", "SRU_Dragon_Earth", "SRU_Dragon_Elder"]


blacklist = ["PreSeason_Turret_Shield", "פ", "SRUAP_MageCrystal",
             "SRU_CampRespawnMarker", "SRUAP_Turret_Order5", "SRU_PlantRespawnMarker",
             "@|v"]  # TODO: Can cause compile error


class ObjectManager:

    def __init__(self):

        self.mem = None

        self.champions = {

        }
        self.order_minions = []
        self.chaos_minions = []
        self.missiles = []
        self.turrets = []
        self.jungle_monsters = []
        self.stats = ChampionStats()

        self.champions_names = self.stats.names()

        self.spell_data = SpellData()

        self.MAX_UNITS = 4096

        self.unit_read = 0
        self.visited_nodes = []
        self.unit_scan_pointers = []

    def get_champion_by_name(self, name) -> Object:
        champion = self.champions[name.lower()]
        return champion

    def get_all_champions(self):
        return list(self.champions.values())

    def scan_units(self, obj_manager):

        root_unit_address = self.mem.read_int(obj_manager + offsets.obj_map_root)
        if root_unit_address <= 0:
            return

        self.unit_read = 0
        self.order_minions.clear()
        self.chaos_minions.clear()
        self.visited_nodes.clear()
        self.turrets.clear()

        self.scan_unit(root_unit_address)

    def scan_unit(self, address):
        self.unit_read += 1

        if self.unit_read > self.MAX_UNITS or address <= 0 or address in self.visited_nodes:
            return

        self.visited_nodes.append(address)

        try:
            data = self.mem.read_bytes(address, 0x18)
        except MemoryReadError:
            return

        net_id = int_from_buffer(data, offsets.obj_map_node_net_id)

        if net_id >= 0x40000000:
            self.update_unit(net_id, int_from_buffer(data, offsets.obj_map_node_object))

        for x in range(0,3):
            self.scan_unit(int_from_buffer(data, (x*4)))
            self.scan_unit(int_from_buffer(data, (x*4)))
            self.scan_unit(int_from_buffer(data, (x*4)))

    def update_unit(self, net_id, address):
        if address <= 0:
            return

        if net_id <= 0:
            return

        try:
            name_ptr = self.mem.read_int(address + offsets.obj_name)
            name = self.mem.read_string(name_ptr, 50)
        except (UnicodeDecodeError, pymem.exception.MemoryReadError):
            return

        if name.strip() in blacklist:
            return
        if not name:
            return

        if name == UnitData.TURRET.value:
            self.turrets.append(address)
        elif name in UnitData.ORDER_MINION.value:
            self.order_minions.append(address)
        elif name in UnitData.CHAOS_MINION.value:
            self.chaos_minions.append(address)
        elif name.lower() in self.champions_names and name.lower() not in self.champions:
            Logger.warning(f"Found new champion: {name}")
            self.champions[name.lower()] = Object(address)
        elif name in UnitData.JUNGLE_MONSTERS.value:
            self.jungle_monsters.append(address)
        elif name in UnitData.DRAGONS.value:
            self.jungle_monsters.append(address)
        elif "VE" in name:
            self.champions[name.lower()] = Object(address)


        """  Fuck missiles, we are external :)
        elif spell_info_ptr := self.mem.read_int(address + offsets.missile_spell_info):
            if spell_info_ptr:
                try:
                    data = self.mem.read_int(spell_info_ptr + offsets.spell_info_spell_data)
                except pymem.exception.MemoryReadError:
                    return

                if data:

                    try:
                        name_ptr = self.mem.read_int(data + offsets.missile_name)
                        name = self.mem.read_string(name_ptr, 50)
                    except:
                        name = ""
                    if name:
                        if self.spell_data.get_spell_by_name(name):
                            # print(self.spell_data.get_spell_by_name(name))
                            self.missiles.append(spell_info_ptr)
                        else:

                            self.missiles.append(spell_info_ptr)
        """

    def update_thread_job(self):
        p = None
        while not p:
            p = pymem.Pymem("league of legends.exe")

        self.mem = p

        Logger.log("ObjectManager connected!")

        while True:
            self.scan_units(self.mem.read_int(self.mem.base_address + offsets.obj_manager))
            time.sleep(2)

    async def select_lowest_target(self):
        for champion in self.champions.values():
            if await champion.name() != await sdk.Sdk.local_player.name():
                champ_health = await champion.health()
                in_range = await Object.in_basic_attack_range(sdk.Sdk.local_player, champion)
                is_alive = await champion.is_alive()

                if champ_health > 0 and in_range and is_alive:
                    return champion
        return None

    async def get_closest_target(self):

        old_dist = 99999999999
        target = None

        player_pos = sdk.Sdk.local_player.object_data.position

        for champion in self.champions.values():
            champion_data = champion.object_data
            if champion_data.name != sdk.Sdk.local_player.object_data.name:

                if champion_data.health > 0 and champion_data.visible:
                    champ_pos = champion_data.position

                    dist = Object.distance_between_vec(player_pos, champ_pos)
                    if dist < old_dist:
                        old_dist = dist
                        target = champion
        return target
