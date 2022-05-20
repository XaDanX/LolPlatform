import math

import sdk.sdk
from sdk.missile import Missile
from sdk.object import Object
from sdk.sdk import Sdk
import imgui

__name__ = "nidalle"
__description__ = "Script for nidalee"

from sdk.utils import w2s


class QSpell:
    name = ""
    flags = 6154
    delay = 0.25
    cast_range = 1500
    cast_radius = 299.29998779296875
    width = 40
    height = -50
    speed = 1300
    travel_time = 0


class Globals:
    pass


async def script_init():
    pass


async def script_unload():
    pass


async def script_menu():
    pass


async def predict_linear_spell():
    try:
        obj = Object(Sdk.object_manager.get_champion_by_name("Irelia"))
        target = await obj.load_object()
    except:
        return None

    """
    if not target.is_moving:
        return target.position
    """
    local_player = await Sdk.local_player.load_object()

    t = target.position.sub(local_player.position)

    t = t.length() / QSpell.speed
    t += 0.01

    missile = QSpell()

    target_dir = target.position.sub(target.prev_pos).normalize()
    if math.isnan(target_dir.x):
        target_dir.x = 0
    if math.isnan(target_dir.y):
        target_dir.y = 0
    if math.isnan(target_dir.z):
        target_dir.z = 0

    target = await obj.load_object()

    result = target.position.add_d(1 * target.movement_speed * t)

    return result



async def script_update():
    for miss in Sdk.object_manager.missiles.copy():
        curr = Missile(miss)
        data = await curr.load_object()
        print(miss)
        print(data)
