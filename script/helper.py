import asyncio

import keyboard
import mouse

from sdk.object import Object
from sdk.sdk import Sdk
import imgui

__name__ = "helper"
__description__ = "Hi"

from sdk.utils import w2s


class Globals:
    KILLABLE_MINION_COLOR = [81 / 255, 27 / 255, 117 / 255, 0.8]

    draw_killable_minion = True


async def script_init():
    pass


async def script_unload():
    pass


async def script_menu():
    imgui.begin("Helper")
    _, Globals.draw_killable_minion = imgui.checkbox("Mark killable minnions", Globals.draw_killable_minion)
    imgui.end()


async def draw_killable_minion():
    local_player = await Sdk.local_player.load_object()

    for current_object_pointer in Sdk.object_manager.enemy_minions.copy():

        if current_object_pointer:

            current_object = Object(current_object_pointer)
            current_object_data = await current_object.load_object()

            if current_object_data.health > 1 and current_object_data.visible:
                effective_damage = Object.effective_damage(
                    local_player.attack_damage + local_player.bonus_attack_damage, current_object_data.armor)
                if effective_damage > current_object_data.health:
                    if Object.in_basic_attack_range(local_player, current_object_data):
                        await Sdk.Renderer.drawing.draw_circle_at(current_object_data.position, 55,
                                                                  Globals.KILLABLE_MINION_COLOR, 6, 10)
        del current_object
        del current_object_data


async def script_update():
    if Globals.draw_killable_minion:
        await draw_killable_minion()
