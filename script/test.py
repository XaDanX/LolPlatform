from sdk.sdk import Sdk
from sdk.object import Object
import imgui

__name__ = "test script"
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
        attackable = await Object.in_basic_attack_range(Sdk.local_player, under_mouse_object)


        imgui.begin(f"Object {await under_mouse_object.name()} info")
        if attackable:
            with imgui.font(Sdk.Fonts.ruda.get(16)):
                imgui.text("Attackable")

        with imgui.font(Sdk.Fonts.ruda.get(16)):
            imgui.text(f"champion: {await under_mouse_object.name()}")
            imgui.text(f"health: {await under_mouse_object.health()}")
            imgui.text(f"max health: {await under_mouse_object.max_health()}")
            imgui.text(f"team: {await under_mouse_object.team()}")
            imgui.text(f"x: {int(obj_pos.x)} y: {int(obj_pos.y)} z: {int(obj_pos.z)}")

        if name.lower() in Sdk.champion_stats.names():
            q_spell = await under_mouse_object.get_spell_by_slot(0)
            w_spell = await under_mouse_object.get_spell_by_slot(1)
            e_spell = await under_mouse_object.get_spell_by_slot(2)
            r_spell = await under_mouse_object.get_spell_by_slot(3)
            d_spell = await under_mouse_object.get_spell_by_slot(4)
            f_spell = await under_mouse_object.get_spell_by_slot(5)
            with imgui.font(Sdk.Fonts.ruda.get(16)):
                imgui.text("Spells:")
                imgui.text(f"\t{q_spell.name}::{q_spell.level}::{round(q_spell.cool_down)}s\n")
                imgui.text(f"\t{w_spell.name}::{w_spell.level}::{round(w_spell.cool_down)}s\n")
                imgui.text(f"\t{e_spell.name}::{e_spell.level}::{round(e_spell.cool_down)}s\n")
                imgui.text(f"\t{r_spell.name}::{r_spell.level}::{round(r_spell.cool_down)}s\n")
                imgui.text(f"\t{d_spell.name}::{d_spell.level}::{round(d_spell.cool_down)}s\n")
                imgui.text(f"\t{f_spell.name}::{f_spell.level}::{round(f_spell.cool_down)}s\n")
        imgui.end()
