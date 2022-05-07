import random
import time

import pymem
from pymem.exception import MemoryReadError
from recordclass import recordclass

from memory.memory import Memory
from sdk.object import Object
import sdk.offsets as offsets
from sdk.stats import ChampionStats
import sdk.sdk as sdk

import arrow

Node = recordclass('Node', 'address, next')


def linked_insert(current_node, next_address):
    next_node = Node(next_address, current_node.next)
    current_node.next = next_node


def int_from_buffer(data, offset):
    return int.from_bytes(data[offset:offset + 4], 'little')


class ObjectManager:

    def __init__(self):
        self.champions = {

        }
        self.minions = []
        self.stats = ChampionStats()

    def get_champion_by_name(self, name) -> Object:
        champion = self.champions[name.lower()]
        return champion

    def get_all_champions(self):
        return list(self.champions.values())

    def update(self):  # Threaded update for better performance.

        start = arrow.utcnow()

        self.champions.clear()
        self.minions.clear()

        # object_pointers = await Memory().read(Memory.process.base_address + offsets.obj_manager, "int")

        object_pointers = Memory.process.read_int(Memory.process.base_address + offsets.obj_manager)

        # root_node = Node(await Memory().read(object_pointers + offsets.obj_map_root, "int"), None)

        root_node = Node(Memory.process.read_int(object_pointers + offsets.obj_map_root), None)

        addresses_seen = set()
        current_node = root_node
        pointers = []
        count = 0
        while current_node is not None and count < 500:  # max
            if current_node.address in addresses_seen:
                current_node = current_node.next
                continue
            addresses_seen.add(current_node.address)
            try:
                # data = await Memory().read_bytes(current_node.address, 0x18)

                data = Memory.process.read_bytes(current_node.address, 0x18)

                count += 1
            except MemoryReadError:
                pass
            else:
                for i in range(3):
                    child_address = int_from_buffer(data, i * 4)
                    if child_address in addresses_seen:
                        continue
                    linked_insert(current_node, child_address)
                net_id = int_from_buffer(data, offsets.obj_map_node_net_id)
                if net_id - 0x40000000 <= 0x100000:
                    pointers.append(int_from_buffer(data, offsets.obj_map_node_object))
            current_node = current_node.next

        names = self.stats.names()
        for obj in pointers:
            if obj > 0:
                try:
                    try:
                        name_ptr = Memory.process.read_int(obj + offsets.obj_name)
                        name = Memory.process.read_string(name_ptr, 16)
                    except (UnicodeDecodeError, pymem.exception.MemoryReadError):
                        continue

                    if name.lower() in names and name.lower():
                        self.champions[name.lower()] = Object(obj)
                    if "Minion" in name:
                        self.minions.append(Object(obj))
                except:
                    pass
        sdk.Sdk.BenchmarkData.object_manager_time = (arrow.utcnow() - start).total_seconds() * 1000

    def update_thread_job(self):
        while True:
            self.update()
            time.sleep(5)

    async def select_lowest_target(self):
        for champion in self.champions.values():
            if await champion.name() != await sdk.Sdk.local_player.name():
                champ_health = await champion.health()
                in_range = await Object.in_basic_attack_range(sdk.Sdk.local_player, champion)
                is_alive = await champion.is_alive()

                if champ_health > 0 and in_range and is_alive:
                    return champion
        return None
