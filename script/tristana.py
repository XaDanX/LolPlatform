import sdk.sdk
from sdk.object import Object
from sdk.sdk import Sdk
import imgui

__name__ = "tristana"
__description__ = "Script for tristana ;o"


class Globals:
    RADIUS = 55
    DAMAGE = [0, 70, 80, 90, 100, 110]
    PERCENTAGE = [0, 1.5, 1.75, 2, 2.25, 2.50]
    NORMAL_COLOR = imgui.get_color_u32_rgba(0, 1, 0, 1)
    KILLABLE_COLOR = imgui.get_color_u32_rgba(1, 0, 0, 1)


async def script_init():
    pass


async def script_unload():
    pass


async def script_menu():
    pass


async def e_effective_damage():
    under_mouse = await Sdk.game.under_mouse_obj()
    if under_mouse:
        if under_mouse != Sdk.local_player.base and under_mouse in Sdk.object_manager.champions.values():

            target = Object(under_mouse)
            target_data = await target.load_object()

            tristana_e_spell = Sdk.local_player.spell_book.e_spell
            player_crit_chance = Sdk.local_player.object_data.crit_chance

            target_armor = target_data.armor

            local_player_ad = Sdk.local_player.object_data.attack_damage + \
                              Sdk.local_player.object_data.bonus_attack_damage
            local_player_crit_mult = player_crit_chance * 0.33

            damage = Globals.DAMAGE[tristana_e_spell.level] + (
                    local_player_ad * Globals.PERCENTAGE[tristana_e_spell.level]) + local_player_crit_mult + (
                             4 * 0.3)

            tristana_e_spell_damage = Object.effective_damage(damage, target_armor)

            auto_attack_effective = Object.effective_damage(local_player_ad, target_armor)

            combo_damage = tristana_e_spell_damage + (auto_attack_effective * 4)

            obj_pos = target_data.position

            obj_pos.y += 100
            with imgui.font(Sdk.Fonts.ruda.get(16)):
                if combo_damage > target_data.health:
                    await sdk.sdk.Sdk.Renderer.drawing.draw_text_at(obj_pos, Globals.KILLABLE_COLOR,
                                                                    "Combo Damage: {}".format(combo_damage))
                else:
                    await sdk.sdk.Sdk.Renderer.drawing.draw_text_at(obj_pos, Globals.NORMAL_COLOR,
                                                                    "Combo Damage: {}\nNormal Damage: {}".format(
                                                                        combo_damage, tristana_e_spell_damage))


async def attack_range():
    tristana = await Sdk.local_player.load_object()
    tristana_attack_range = tristana.attack_range
    obj_pos = tristana.position
    await Sdk.Renderer.drawing.draw_circle_at(obj_pos, tristana_attack_range + Globals.RADIUS, (1, 0, 0, 0.3), 3,
                                              100)


async def script_update():
    await e_effective_damage()
    await attack_range()
