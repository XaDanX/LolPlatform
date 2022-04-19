import time

import imgui

import sdk.game
from overlay.overlay import Overlay
import requests
from pymem.exception import MemoryReadError

from utils.logger import Logger
from managers.scripts_manager import ScriptManager

import asyncio

import pymem
import sdk.offsets as offsets

from memory.memory import Memory

from sdk.sdk import *


async def main():
    while 1:
        try:

            local_player = await Memory().read(Memory.process.base_address + offsets.local_player, "int")
            Sdk.local_player = LocalPlayer(local_player)
        except pymem.exception.MemoryReadError:
            time.sleep(1)

        try:
            Sdk.object_manager = ObjectManager()
            await Sdk.object_manager.update()
        except pymem.exception.MemoryReadError:
            time.sleep(1)

        Sdk.champion_stats = ChampionStats()

        if Sdk.local_player and len(Sdk.object_manager.champions) > 0:
            break

    """
        Loading scripts
    """
    Sdk.Renderer.renderer = Overlay("League of Legends (TM) Client")

    for x in range(1, 36):
        font = Sdk.Renderer.renderer.craft_font(x)
        Sdk.Fonts.ruda[x] = font

    script_manager = ScriptManager()
    #script_manager.load("script.autosmite")
    script_manager.load("script.test")
    script_manager.load("script.avarness")
    #cript_manager.load("script.drawer")
    script_manager.load("script.orbwalker")
    await script_manager.initialize_scripts()

    await Sdk.Renderer.renderer.update()

    while True:
        e = await Sdk.object_manager.select_lowest_target()
        for x in range(300):
            try:
                imgui.new_frame()
            except:
                pass
            await script_manager.update_scripts()  # Update all scripts

            # TODO: Overlay, drawing, timing

            await Sdk.Renderer.renderer.update()
        await Sdk.object_manager.update()


if __name__ == "__main__":
    Logger().init()
    Logger.log("Waiting for game.")
    while True:
        try:
            handle = pymem.Pymem("League of Legends.exe")
            Memory.process = handle
            break
        except pymem.exception.ProcessNotFound:
            time.sleep(1)

    Logger.log("Game found!")
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        Logger.log("Closing.")
