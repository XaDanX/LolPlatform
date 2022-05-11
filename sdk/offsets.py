SPELL_DATA_SIZE = 300

# Object
obj_health = 0xDB4
obj_max_health = 0xDC4
obj_mana = 0x2B4
obj_max_mana = obj_mana + 0x10
obj_name = 0x2BAC
obj_team = 0x4C
obj_armor = 0x12AC
obj_crit_chance = 0x12A8
obj_spellbook = 0x2338
obj_attack_range = 0x12cc
obj_recall_state = 0xD78
obj_manager = 0x24B80A8
obj_map_root = 0x28
obj_map_count = 0x2C
obj_map_node_net_id = 0x10
obj_map_node_object = 0x14
obj_pos = 0x1F4
obj_visibility = 0x28C
obj_attack_speed_multi = 0x1280
obj_spawn_count = 0x2A0
obj_health_bar_position = 0x17B080
obj_attack_damage = 0x1284
obj_bonus_attack_damage = 0x11FC

# Spell
spell_ready_at = 0x24

spell_level = 0x1C
spell_info = 0x120
spell_data = 0x44  # [[spell_info] + spell_data]
spell_name = 0x90
spell_true_damage = 0x94

# Game
under_mouse_obj = 0x30FCAD0
game_time = 0x31001D0

local_player = 0x31090E8

renderer = 0x3136FC8
view_matrix = 0x58
proj_matrix = 0x98
renderer_width = 0xC
renderer_height = 0x10
