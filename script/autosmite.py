from sdk.sdk import Sdk

__name__ = "auto  smite"
__description__ = "Auto smite script."


class Globals:
    smite_id = 0


async def script_menu():
    pass


async def script_unload():
    pass


async def script_init():
    if Globals.smite_id == 0:
        slot_1 = await Sdk.local_player.get_spell_by_slot(4)
        slot_2 = await Sdk.local_player.get_spell_by_slot(5)
        if slot_1.name in Sdk.Data.summoner_spell.SMITE.value:
            Globals.smite_id = 4
        elif slot_2.name in Sdk.Data.summoner_spell.SMITE.value:
            Globals.smite_id = 5


async def script_update():
    slot_2 = await Sdk.local_player.get_spell_by_slot(5)
    if Globals.smite_id != 0:
        under_mouse_object = await Sdk.game.under_mouse_obj()
        if under_mouse_object:
            object_health = await under_mouse_object.health()
            smite_spell_data = await Sdk.local_player.get_spell_by_slot(Globals.smite_id)
            smite_damage = smite_spell_data.spell_true_damage

            if await Sdk.local_player.is_spell_ready(Globals.smite_id):
                if object_health <= smite_damage:
                    await Sdk.controller.press_key('f')
