from sdk.sdk import Sdk
from sdk.utils import Vec2
from utils.logger import Logger
import imgui

__name__ = "drawer"
__description__ = "drawing script."


async def script_init():
    pass


async def script_update():
    for champion in Sdk.object_manager.champions.copy().values():
        is_alive = await champion.is_alive()
        team = await champion.team()
        #visible = await champion.is_visible()

        if is_alive \
                and team != int(await Sdk.local_player.team()):
            obj_pos = await champion.pos()

            q_spell = await champion.get_spell_by_slot(0)
            w_spell = await champion.get_spell_by_slot(1)
            e_spell = await champion.get_spell_by_slot(2)
            r_spell = await champion.get_spell_by_slot(3)
            d_spell = await champion.get_spell_by_slot(4)
            f_spell = await champion.get_spell_by_slot(5)
            with imgui.font(Sdk.Fonts.ruda.get(16)):
                await Sdk.Renderer.drawing.draw_text_at(obj_pos, 0xFF00FF00,
                                                        f"Q: {str(round(q_spell.cool_down))}\n"
                                                        f"W: {str(round(w_spell.cool_down))}\n"
                                                        f"E: {str(round(e_spell.cool_down))}\n"
                                                        f"R: {str(round(r_spell.cool_down))}\n"
                                                        f"D: {str(round(d_spell.cool_down))}\n"
                                                        f"F: {str(round(f_spell.cool_down))}")
