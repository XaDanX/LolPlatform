import asyncio
import time
from typing import Any

import keyboard
import mouse

from sdk.sdk import Sdk
from sdk.utils import w2s
import imgui

__name__ = "orbwalker"
__description__ = "OrbWalker script."


async def script_init():
    ScriptData.game_time = await Sdk.game.time()
    ScriptData.can_move_time = ScriptData.game_time
    ScriptData.can_attack_time = ScriptData.game_time
    ScriptData.attacking = False


class ScriptData:
    game_time: Any
    can_attack_time: Any
    can_move_time: Any
    attacking: bool


async def get_attack_time():
    champ_info = Sdk.champion_stats.get_champion_info(str(await Sdk.local_player.name()).lower())
    attack_speed = champ_info.attack_speed_base
    attack_ratio = champ_info.attack_speed_ratio
    attack_speed_multi = await Sdk.local_player.attack_speed_multi()


    attack_cap = 2.5  # no lethal tempo included..

    total = min(attack_cap, (attack_speed_multi - 1) * attack_ratio + attack_speed)
    return 1. / total


async def get_windup_time():
    champ_info = Sdk.champion_stats.get_champion_info(str(await Sdk.local_player.name()).lower())
    attack_speed = champ_info.attack_speed_base
    attack_ratio = champ_info.attack_speed_ratio


    attack_time = await get_attack_time()
    base_windup = (1 / attack_speed) * champ_info.windup_percent
    windup_time = base_windup + ((attack_time * champ_info.windup_percent) - base_windup) * (
            champ_info.windup_modifier + 1)
    return -min(windup_time, attack_time)


async def walk(x, y):
    game_time = await Sdk.game.time()
    keyboard.press("n")
    if x is not None and y is not None and ScriptData.can_attack_time < game_time:
        ScriptData.attacking = True
        stored_x, stored_y = mouse.get_position()
        mouse.move(int(x), int(y))
        mouse.right_click()
        await asyncio.sleep(0.01)
        game_time = await Sdk.game.time()

        attack_time = await get_attack_time()
        windup_time = await get_windup_time()

        ScriptData.can_attack_time = game_time + attack_time
        ScriptData.can_move_time = game_time + windup_time
        mouse.move(int(stored_x), int(stored_y))
        ScriptData.attacking = False
    elif ScriptData.can_move_time < game_time:
        if not ScriptData.attacking:
            mouse.right_click()
        ScriptData.can_move_time = game_time + 0.05
    keyboard.release("n")


async def script_update():
    if keyboard.is_pressed(' '):
        target = await Sdk.object_manager.select_lowest_target()
        if target is not None:
            render = await Sdk.game.render()
            game_time = await Sdk.game.time()
            pos = await target.read_pos()
            w2s_pos = w2s(pos, render.view_proj_matrix)

            await walk(w2s_pos.x, w2s_pos.y)
        await asyncio.sleep(0.01)
