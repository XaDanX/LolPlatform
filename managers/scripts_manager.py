import importlib

import pymem

from utils.logger import Logger


class ScriptManager:

    def __init__(self):
        self.scripts = {}

    def load(self, path):
        try:
            mod = importlib.import_module(path)
            self.scripts[mod.__name__] = mod
            Logger.log(f"Loaded script: {mod.__name__}.")
        except ImportError:
            Logger.warning(f"Cannot load script {path}")

    async def unload(self, name):
        try:
            script = self.scripts.get(name)
        except KeyError:
            Logger.warning(f"Cannot unload script: name")
            return
        try:
            await script.script_unload()
        except AttributeError:
            Logger.warning("Cannot execute unload function. UNSAFE Unloading.")
        try:
            self.scripts.pop(name)
        except KeyError:
            Logger.warning(f"Cannot unload script: name")
            return

    async def initialize_scripts(self):
        for module in self.scripts.copy().values():
            try:
                await module.script_init()
            except AttributeError:
                Logger.warning(f"Cannot initialize script: {module.__name__}. Unloading.")
                await self.unload(module.__name__)
            except pymem.exception.MemoryReadError:
                Logger.error(f"Errorduring initializing script: {__name__}. Unloading.")
                await self.unload(module.__name__)

    async def update_scripts(self):
        for module in self.scripts.copy().values():
            try:
                await module.script_update()
            except AttributeError:
                Logger.warning(f"Can not update script: {module.__name__}. Unloading.")
                await self.unload(module.__name__)
            except pymem.exception.MemoryReadError:
                """
                    Sometimes randomly raised.. //? fix
                """
                pass
