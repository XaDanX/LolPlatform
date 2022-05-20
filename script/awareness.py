import asyncio

from sdk.object import Object
from sdk.sdk import Sdk
import imgui

__name__ = "awareness"
__description__ = "DevScript test."

from sdk.utils import w2s


class Globals:
    ATTACK_RANGE_COLOR = [207 / 255, 0, 76 / 255, 0.3]

    cool_down_tracker_font_size = 12

    draw_attack_ranges = True
    draw_cooldowns = True
    points = 23


async def script_init():
    pass


async def script_unload():
    pass


async def script_menu():
    imgui.begin("Awareness Menu")
    _, Globals.draw_attack_ranges = imgui.checkbox("Draw Attack Ranges", Globals.draw_attack_ranges)
    _, Globals.draw_cooldowns = imgui.checkbox("Draw Cooldowns", Globals.draw_cooldowns)
    changed, Globals.cool_down_tracker_font_size = imgui.slider_int(
        "font size", Globals.cool_down_tracker_font_size, 1, 35
    )
    changed, Globals.points = imgui.slider_int(
        "Circle points", Globals.points, 1, 500
    )

    imgui.end()


async def draw_attack_range(current_obj):
    if current_obj.health > 1 and current_obj.visible:
        selection_radius = Sdk.champion_stats.get_radius(current_obj.name)

        await Sdk.Renderer.drawing.draw_circle_at(current_obj.position,
                                                  current_obj.attack_range + selection_radius,
                                                  Globals.ATTACK_RANGE_COLOR, 2, Globals.points)


async def draw_cooldowns(current_obj):
    if current_obj.object_data.health > 1 and current_obj.object_data.visible:
        spell_book = current_obj.spell_book
        """
        with imgui.font(Sdk.Fonts.ruda.get(Globals.cool_down_tracker_font_size)):
            await Sdk.Renderer.drawing.draw_text_at(current_obj.object_data.position,
                                                    imgui.get_color_u32_rgba(1, 1, 1, 0.9),
                                                    f"{spell_book.q_spell.ready_at}  {spell_book.w_spell.ready_at}  {spell_book.e_spell.ready_at}  {spell_book.r_spell.ready_at}\n"
                                                    f"   {spell_book.summoner_spell_1.ready_at}  {spell_book.summoner_spell_2.ready_at}")
        """

async def script_update():
    for current_object in Sdk.object_manager.champions.copy().values():
        if current_object:

            if current_object.object_data.team == Sdk.local_player.object_data.team:  # Loop for teammates
                await draw_attack_range(current_object.object_data)
            else:
                if Globals.draw_attack_ranges:
                    await draw_attack_range(current_object.object_data)
                if Globals.draw_cooldowns:
                    await draw_cooldowns(current_object)

            if Globals.draw_attack_ranges:
                await draw_attack_range(current_object.object_data)
            if Globals.draw_cooldowns:
                await draw_cooldowns(current_object)
