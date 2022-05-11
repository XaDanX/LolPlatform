from sdk.sdk import Sdk
from sdk.utils import Vec2
from utils.logger import Logger
import imgui

__name__ = "drawer"
__description__ = "drawing script."


async def script_init():
    pass


async def script_menu():
    pass


async def script_update():
    for champion in Sdk.object_manager.champions.copy().values():
        team = int(await champion.team())

        if team != int(await Sdk.local_player.team()):
            alive = await champion.is_alive()
            visible = await champion.is_visible()

            if alive and visible:
                obj_pos = await champion.pos()

                #obj_pos.y +=

                q_spell = await champion.spell_ready_in(0)
                w_spell = await champion.spell_ready_in(1)
                e_spell = await champion.spell_ready_in(2)
                r_spell = await champion.spell_ready_in(3)
                d_spell = await champion.spell_ready_in(4)
                f_spell = await champion.spell_ready_in(5)
                with imgui.font(Sdk.Fonts.ruda.get(18)):
                    await Sdk.Renderer.drawing.draw_text_at(obj_pos, imgui.get_color_u32_rgba(0, 0.7, 1, 1),
                                                            f"|Q - {str(round(q_spell))}| "
                                                            f"|W - {str(round(w_spell))}| "
                                                            f"|E - {str(round(e_spell))}| "
                                                            f"|R - {str(round(r_spell))}| "
                                                            f"|D - {str(round(d_spell))}| "
                                                            f"|F - {str(round(f_spell))}|")
