import dataclasses
import glob
import importlib

import arrow
import pymem

import sdk.sdk as sdk
from utils.logger import Logger


@dataclasses.dataclass
class Script:
    path: str
    name: str
    load_path: str


class ScriptManager:

    def __init__(self):
        self.scripts = {}
        self.script_files = {}
        self.path = ""

    def load_from_directory(self, path="script"):
        self.path = path
        self.scripts.clear()
        self.script_files.clear()
        scripts = glob.glob(f"{path}/*.py")
        for script in scripts:
            path = script
            name = path.split("\\")[-1].replace(".py", "")
            load_path = path.replace("\\", ".").replace(".py", "")
            if "__init__" in load_path:
                continue
            self.script_files[name] = Script(path, name, load_path)

    async def load(self, path):
        try:
            mod = importlib.import_module(path)
            if mod.__name__ in self.scripts:
                return
            self.scripts[mod.__name__] = mod
            await self.initialize_script(mod)
            Logger.log(f"Loaded script: {mod.__name__}.")
        except ImportError:
            Logger.warning(f"Cannot load script {path}")

    async def unload(self, name):
        self.load_from_directory(self.path)
        try:
            script = self.scripts.get(name)
        except KeyError:
            Logger.warning(f"Cannot unload script: {name}")
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

    async def initialize_script(self, mod):
        try:

            module = mod

            await module.script_init()
        except AttributeError:
            Logger.warning(f"Cannot initialize script: {module.__name__}. Unloading.")
            await self.unload(module.__name__)
        except pymem.exception.MemoryReadError:
            Logger.error(f"Errorduring initializing script: {__name__}. Unloading.")
            await self.unload(module.__name__)

    async def update_scripts(self):
        start = arrow.utcnow()
        for module in self.scripts.copy().values():
            # try:
            await module.script_update()
            if sdk.Sdk.Renderer.renderer.show_menu:
                await module.script_menu()
            """
            except AttributeError:
                Logger.warning(f"Can not update script: {module.__name__}. Unloading.")
                await self.unload(module.__name__)
            except pymem.exception.MemoryReadError:
                    #Sometimes randomly raised.. //? fix

                pass
            """
        sdk.Sdk.BenchmarkData.script_update_time = (arrow.utcnow() - start).total_seconds() * 1000
