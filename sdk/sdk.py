from typing import Any

import overlay.drawing
from managers.object_manager import ObjectManager
from overlay.overlay import Overlay
from sdk.input import Controller
from sdk.object import Object, LocalPlayer
from sdk.game import Game, SummonerSpell
from sdk.stats import ChampionStats


class Sdk:
    game: Game = Game()
    local_player: LocalPlayer
    controller: Controller = Controller()
    champion_stats: ChampionStats
    object_manager: ObjectManager

    class Renderer:
        renderer: Overlay
        imgui: Overlay
        drawing = overlay.drawing.Drawing()

    class Fonts:
        ruda = {}

    class Data:
        summoner_spell = SummonerSpell

    class BenchmarkData:
        total_time = 0.
        render_time = 0.
        script_update_time = 0.
        object_manager_time = 0.

    class Info:
        width = 0
        height = 0

    class Internal:
        script_manager: None
