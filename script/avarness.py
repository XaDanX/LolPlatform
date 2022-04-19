from sdk.sdk import Sdk
import imgui

__name__ = "avarness"
__description__ = "DevScript test."

from utils.logger import Logger


class Globals:
    smite_id = 0


async def script_init():
    pass


async def script_update():
    under_mouse_object = await Sdk.game.under_mouse_obj()
    if under_mouse_object:
        object_health = await under_mouse_object.health()
        obj_pos = await under_mouse_object.read_pos()
        name = await under_mouse_object.name()

        if name.lower() in Sdk.champion_stats.names():
            e = imgui.get_overlay_draw_list()
            attack_range = Sdk.champion_stats.get_champion_info(name).raw.get("attackRange")
            selection_radius = Sdk.champion_stats.get_radius(name.lower())
            await Sdk.Renderer.drawing.draw_circle_at(obj_pos, attack_range + selection_radius, (255, 0, 0, 255), 3)
            with imgui.font(Sdk.Fonts.ruda.get(32)):
                await Sdk.Renderer.drawing.draw_text_at(obj_pos, 0xFFFFCCFF, f"HP: {str(object_health)}")

