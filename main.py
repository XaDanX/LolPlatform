import os
import sys
from time import sleep, monotonic

from ctypes import windll

import arrow
import imgui
from imgui import new_frame

from threading import Thread

import sdk.game
import sdk.offsets

from utils.logger import Logger
from managers.scripts_manager import ScriptManager

from asyncio import get_event_loop

import pymem
import sdk.offsets as offsets

from memory.memory import Memory

from sdk.sdk import *

from multiprocessing import Process


async def main():
    while 1:
        try:

            local_player = await Memory().read(Memory.process.base_address + offsets.local_player, "int")
            Sdk.local_player = LocalPlayer(local_player)
            for x in range(2):
                await Sdk.local_player.load_object()
            await Sdk.local_player.load_spell_book(True)
            Logger.log("Local player: OK")
        except pymem.exception.MemoryReadError:
            sleep(1)

        try:
            Sdk.object_manager = ObjectManager()
            Sdk.object_manager.mem = Memory.process
            Sdk.object_manager.scan_units(Memory.process.read_int(Memory.process.base_address + offsets.obj_manager))
            Logger.log("Object Manager: OK")
        except pymem.exception.MemoryReadError:
            sleep(1)

        if Sdk.local_player and len(Sdk.object_manager.champions) > 0:
            Sdk.champion_stats = ChampionStats()
            Logger.log("Champion Stats: OK")
            break

    Logger.log("Starting overlay.")
    Sdk.Renderer.renderer = Overlay("League of Legends (TM) Client")

    for x in range(1, 36):
        font = Sdk.Renderer.renderer.craft_font(x)
        Sdk.Fonts.ruda[x] = font

    object_manager_update_process = Process(target=Sdk.object_manager.update_thread_job, args=())
    object_manager_update_process.start()  # Non-blocking process for better performance

    script_manager = ScriptManager()
    Sdk.Internal.script_manager = script_manager

    Logger.log("Loading scripts.")

    script_manager.load_from_directory("script")

    await Sdk.Renderer.renderer.update()

    render = await sdk.game.Game.render()
    Sdk.Info.width = render.width
    Sdk.Info.height = render.height

    os.system("cls")
    Logger.log("Ready to use!")

    while True:
        for tick in range(Sdk.Internal.loop_update_rate):
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
        for champion in Sdk.object_manager.champions.copy().values():
            try:
                await champion.load_object()
                await champion.load_spell_book()
            except pymem.exception.MemoryReadError:
                pass
        try:
            await Sdk.local_player.load_object()
            await Sdk.local_player.load_spell_book()
        except pymem.exception.MemoryReadError:
            pass


if __name__ == "__main__":
    Logger().init()
    # windll.kernel32.SetConsoleTitleA("Some private scripting platform.") //Not working?
    os.system("title Some private scripting platform")
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
        Logger.log("Closing.")
        sys.exit(0)
