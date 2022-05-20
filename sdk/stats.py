import json
from typing import Any

import requests
from functools import lru_cache
import dataclasses

import urllib3

GAME_DATA_ENDPOINT = 'https://127.0.0.1:2999/liveclientdata/allgamedata'
CHAMPION_INFO_ENDPOINT = 'https://raw.communitydragon.org/latest/game/data/characters/{champion}/{champion}.bin.json'
DEFAULT_RADIUS = 65.
DEFAULT_WINDUP = 0.3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def clean_champion_name(name):
    return name.split('game_character_displayname_')[1].lower()


@dataclasses.dataclass
class ChampionInfo:
    attack_speed_base: float
    attack_speed_ratio: float
    windup_percent: float
    windup_modifier: float
    raw: Any


class ChampionStats:
    def __init__(self):
        game_data = requests.get(GAME_DATA_ENDPOINT, verify=False).json()
        champion_names = [clean_champion_name(player['rawChampionName']) for player in game_data['allPlayers']]
        self.champion_data = {}
        for champion in champion_names:
            champion_response = requests.get(CHAMPION_INFO_ENDPOINT.format(champion=champion)).json()
            self.champion_data[champion] = {k.lower(): v for k, v in champion_response.items()}

    @lru_cache(maxsize=None)
    def get_champion_info(self, target):
        root_key = 'characters/{}/characterrecords/root'.format(target.lower())
        attack_speed_base = self.champion_data[target.lower()][root_key]['attackSpeed']
        attack_speed_ratio = self.champion_data[target.lower()][root_key]['attackSpeedRatio']
        basic_attack = self.champion_data[target.lower()][root_key]['basicAttack']
        windup_percent = 0.3
        windup_modifier = 0.
        if 'mAttackDelayCastOffsetPercent' in basic_attack:
            windup_percent = basic_attack['mAttackDelayCastOffsetPercent'] + DEFAULT_WINDUP
        if 'mAttackDelayCastOffsetPercentAttackSpeedRatio' in basic_attack:
            windup_modifier = basic_attack['mAttackDelayCastOffsetPercentAttackSpeedRatio']
        return ChampionInfo(attack_speed_base, attack_speed_ratio, windup_percent, windup_modifier,
                            self.champion_data[target.lower()][root_key])

    @lru_cache(maxsize=None)
    def get_spells(self, target):
        root_key = 'characters/{}/characterrecords/root'.format(target.lower())
        return [
            self.champion_data[target.lower()]['characters/{}/spells/{}'.format(target.lower(), spell.lower())][
                'mSpell']
            for spell in self.champion_data[target.lower()][root_key]['spellNames']
        ]

    @lru_cache(maxsize=None)
    def get_health_bar_height(self, target):
        root_key = 'characters/{}/characterrecords/root'.format(target.lower())
        return self.champion_data[target.lower()][root_key].get("healthBarHeight")

    def names(self):
        return list(self.champion_data.keys())

    @lru_cache(maxsize=None)
    def get_radius(self, target):
        root_key = 'characters/{}/characterrecords/root'.format(target.lower())
        return self.champion_data[target.lower()][root_key].get('overrideGameplayCollisionRadius', 65.)


class SpellData:
    def __init__(self):
        self.data = [{
            "name": "EzrealQ",
            "icon": "Ezreal_Q",
            "flags": 6154,
            "delay": 0.25,
            "castRange": 1150.0,
            "castRadius": 210.0,
            "width": 60.0,
            "height": 100.0,
            "speed": 2000.0,
            "travelTime": 0.0,
            "projectDestination": True
        }]

    def get_spell_by_name(self, name):
        return next(filter(lambda spell: spell['name'] == name, self.data), None)




