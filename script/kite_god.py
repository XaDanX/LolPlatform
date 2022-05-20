import asyncio

import keyboard
import mouse

import sdk.utils
from sdk.object import Object
from sdk.sdk import Sdk
import imgui

__name__ = "kite_god"
__description__ = "Orbwalker :D"

from sdk.utils import w2s


class Globals:
    attack_timer = sdk.utils.Timer()
    move_timer = sdk.utils.Timer()
    humanizer = sdk.utils.Timer()

    last = 0
    kite_ping = 20

    attacking = False


async def script_init():
    pass


async def script_unload():
    pass


async def script_menu():
    imgui.begin("KiteGod")

    changed, Globals.kite_ping = imgui.slider_int(
        "MS", Globals.kite_ping, 1, 90
    )

    imgui.end()


class Kite:

    @staticmethod
    def get_total_attack_speed():
        return Sdk.local_player.object_data.attack_speed_multiplier * Sdk.champion_stats.get_champion_info(
            str(Sdk.local_player.object_data.name)).attack_speed_ratio

    @staticmethod
    def get_attack_time():
        champ_info = Sdk.champion_stats.get_champion_info(str(Sdk.local_player.object_data.name).lower())
        attack_speed = champ_info.attack_speed_base
        attack_ratio = champ_info.attack_speed_ratio
        attack_speed_multi = Sdk.local_player.object_data.attack_speed_multiplier

        attack_cap = 2.5  # no lethal tempo included..

        total = min(attack_cap, (attack_speed_multi - 1) * attack_ratio + attack_speed)
        return 1. / total

    @staticmethod
    def get_windup_time():
        champ_info = Sdk.champion_stats.get_champion_info(str(Sdk.local_player.object_data.name).lower())
        attack_speed = champ_info.attack_speed_base
        attack_ratio = champ_info.attack_speed_ratio

        attack_time = Sdk.local_player.object_data.attack_speed_multiplier
        base_windup = (1 / attack_speed) * champ_info.windup_percent
        windup_time = base_windup + ((attack_time * champ_info.windup_percent) - base_windup) * (
                champ_info.windup_modifier + 1)
        ret = min(windup_time, attack_time)
        if ret < 0:
            ret = -ret

        return ret

    @staticmethod
    async def click(x, y):
        Sdk.controller.mouse_input_lock(True)
        if x is not None and y is not None:
            Globals.attacking = True
            stored_x, stored_y = mouse.get_position()
            mouse.move(int(x), int(y))
            mouse.right_click()
            await asyncio.sleep(0.001)
            mouse.move(int(stored_x), int(stored_y))
            Globals.attacking = False
        Sdk.controller.mouse_input_lock(False)


async def script_update():
    imgui.begin("KiteGod - DEBUG")

    champ = await Sdk.object_manager.get_closest_target()

    if Sdk.local_player.object_data.alive:
        if keyboard.is_pressed(' '):
            atk_time = Kite.get_windup_time()
            windup_time = Kite.get_windup_time()
            target = await Sdk.object_manager.get_closest_target()  # TODO: target selector
            if target:
                imgui.text(f"Windup: {windup_time}")
                imgui.text(f"Attack: {atk_time}")
                imgui.text(f"Target: {target.object_data.name}")
                if Globals.attack_timer.timer() and target:
                    if Object.in_basic_attack_range(Sdk.local_player, target):
                        render = await Sdk.game.render()
                        position = w2s(target.object_data.position, render.view_proj_matrix)
                        await Kite.click(position.x, position.y)
                        Globals.attack_timer.set_timer(atk_time)
                        Globals.move_timer.set_timer(windup_time)
                    else:
                        if Globals.humanizer.timer():
                            mouse.right_click()
                            Globals.humanizer.set_timer(0.2)


                else:
                    if Globals.move_timer.timer():
                        mouse.right_click()
            else:
                if Globals.humanizer.timer():
                    mouse.right_click()
                    Globals.humanizer.set_timer(0.2)

    imgui.end()
