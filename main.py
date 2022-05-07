from time import sleep, monotonic

from ctypes import windll

import arrow
from imgui import new_frame

from threading import Thread

from utils.logger import Logger
from managers.scripts_manager import ScriptManager

from asyncio import get_event_loop

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
            sleep(1)

        try:
            Sdk.object_manager = ObjectManager()
            await Sdk.object_manager.update()
        except pymem.exception.MemoryReadError:
            sleep(1)

        if Sdk.local_player and len(Sdk.object_manager.champions) > 0:
            Sdk.champion_stats = ChampionStats()
            break

    Sdk.Renderer.renderer = Overlay("League of Legends (TM) Client")

    for x in range(1, 36):
        font = Sdk.Renderer.renderer.craft_font(x)
        Sdk.Fonts.ruda[x] = font

    fast_render_thread = Thread(target=Game.fast_render.calculate_matrices_thread, args=())
    fast_render_thread.start()

    script_manager = ScriptManager()

    script_manager.load("script.avarness")
    script_manager.load("script.orbwalker")

    await script_manager.initialize_scripts()

    await Sdk.Renderer.renderer.update()

    while True:
        for x in range(300):
            start = arrow.utcnow()
            try:
                new_frame()
            except:
                pass

            #  Execute scripts
            await script_manager.update_scripts()

            #  Render frame
            await Sdk.Renderer.renderer.update()

            Sdk.BenchmarkData.total_time = (arrow.utcnow() - start).total_seconds() * 1000

        #  Update Objects
        await Sdk.object_manager.update()


if __name__ == "__main__":
    Logger().init()
    windll.kernel32.SetConsoleTitleA("Some private scripting platform.")
    Logger.log("You are using a private scripting platform, please don't share it with anyone and have fun.")
    Logger.log("Waiting for game.")
    while True:
        try:
            handle = pymem.Pymem("League of Legends.exe")
            Memory.process = handle
            break
        except pymem.exception.ProcessNotFound:
            sleep(1)

    Logger.log("Game found!")
    try:
        get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        Sdk.Renderer.renderer.close()
        Logger.log("Closing.")
        quit(1)
