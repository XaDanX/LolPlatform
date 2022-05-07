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
    for under_mouse_object in Sdk.object_manager.champions.copy().values():
        if under_mouse_object:
            visible = await under_mouse_object.is_visible()
            object_health = await under_mouse_object.health()

            if object_health > 1 and visible:
                obj_pos = await under_mouse_object.pos()
                name = await under_mouse_object.name()

                e = imgui.get_overlay_draw_list()
                attack_range = Sdk.champion_stats.get_champion_info(name).raw.get("attackRange")
                selection_radius = Sdk.champion_stats.get_radius(name.lower())
                await Sdk.Renderer.drawing.draw_circle_at(obj_pos, attack_range + selection_radius, (255, 0, 0, 255), 3, 100)
