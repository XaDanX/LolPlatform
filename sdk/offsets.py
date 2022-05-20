SPELL_DATA_SIZE = 300
OBJECT_SIZE = 12000
MISSILE_SIZE = 12000
RENDER_SIZE = 12000

# Object
obj_health = 0xDB4
obj_max_health = 0xDC4
obj_mana = 0x2B4
obj_max_mana = obj_mana + 0x10
obj_name = 0x2BAC
obj_team = 0x4C
obj_armor = 0x12AC
obj_crit_chance = 0x12A8
obj_attack_range = 0x12cc
obj_recall_state = 0xD78
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
obj_move_speed = 0x12C4
obj_is_moving = 0x32E7
obj_spellbook = 0x2338  # Almost never changes

# Spell
spell_ready_at = 0x24  # Almost never changes
spell_slot = 0x488  # Almost never changes
spell_level = 0x1C  # Almost never changes
spell_info = 0x120  # Almost never changes
spell_data = 0x44  # Almost never changes
spell_name = 0x6C  # Almost never changes
spell_true_damage = 0x94  # Almost never changes

# Missile
missile_spell_info = 0x278
missile_name = 0x6C
spell_info_spell_data = 0x44
missile_src_index = 0x2DC
missile_dest_index = 0x330
missile_start_pos = 0x2F4
missile_end_pos = 0x300

# Game
under_mouse_obj = 0x24A838C
game_time = 0x30F0D14

local_player = 0x30F9BDC

renderer = 0x3128448
obj_manager = 0x24A8190
ai_manager = 0x2c84

view_matrix = 0x58
proj_matrix = 0x98
renderer_width = 0xC
renderer_height = 0x10

"""

#include "Offsets.h"	
 
Offsets::Offsets() {};
 
int Offsets::GameTime = 0x30F0D14; // 12.9
int Offsets::ObjectManager = 0x24A8190; // 12.9
int Offsets::LocalPlayer = 0x30F9BDC; // 12.9
int Offsets::UnderMouseObject = 0x24A838C; // 12.9
int Offsets::Chat = 0x24A83B0; // 12.9
int Offsets::ViewProjMatrices = 0x31254E8; // 12.9
int Offsets::Renderer = 0x3128448; // 12.9
int Offsets::MinimapObject = 0x30F0D54; // 12.9
 
int Offsets::ChatIsOpen = 0x75C;
 
int Offsets::ObjIndex = 0x20;
int Offsets::ObjTeam = 0x4C;
int Offsets::ObjMissileName = 0x6C;
int Offsets::ObjNetworkID = 0xCC;
int Offsets::ObjPos = 0x1F4;
int Offsets::ObjMissileSpellCast = 0x250;
int Offsets::ObjVisibility = 0x28C;
int Offsets::ObjSpawnCount = 0x2A0;
int Offsets::ObjSrcIndex = 0x02AC;
int Offsets::ObjMana = 0x2B4;
int Offsets::ObjMaxMana = 0x2C4;
int Offsets::ObjRecallState = 0xD78;
int Offsets::ObjHealth = 0xDB4;
int Offsets::ObjMaxHealth = 0xDC4;
int Offsets::ObjAbilityHaste = 0x16A0;
int Offsets::ObjLethality = 0x11C0;
int Offsets::ObjArmor = 0x12AC;
int Offsets::ObjBonusArmor = 0x12B0;
int Offsets::ObjMagicRes = 0x12B4;
int Offsets::ObjBonusMagicRes = 0x12B8;
int Offsets::ObjBaseAtk = 0x1284;
int Offsets::ObjBonusAtk = 0x11FC;
int Offsets::ObjMoveSpeed = 0x12C4;
int Offsets::ObjSpellBook = 0x27C0;
int Offsets::ObjTransformation = 0x3040;
int Offsets::ObjName = 0x2BAC;
int Offsets::ObjLvl = 0x33A0;
int Offsets::ObjExpiry = 0x298;
int Offsets::ObjCrit = 0x12E0;
int Offsets::ObjCritMulti = 0x12D0;
int Offsets::ObjAbilityPower = 0x1750;
int Offsets::ObjAtkSpeedMulti = 0x1280;
int Offsets::ObjAtkRange = 0x12cc;
int Offsets::ObjTargetable = 0xD1C;
int Offsets::ObjInvulnerable = 0x3EC;
int Offsets::ObjIsMoving = 0x32E7;
int Offsets::ObjDirection = 0x1B88;
int Offsets::ObjItemList = 0x33E8;
int Offsets::ObjExpierience = 0x337C;
int Offsets::ObjMagicPen = 0x11DC;
int Offsets::ObjMagicPenMulti = 0x11E4;
int Offsets::ObjAdditionalApMulti = 0x1248;
int Offsets::ObjManaRegen = 0x1150;
int Offsets::ObjHealthRegen = 0x12F8;
 
int Offsets::ObjBuffManager = 0x2180;
int Offsets::BuffManagerEntriesArray = 0x10;
int Offsets::BuffEntryBuff = 0x8;
int Offsets::BuffType = 0x4;
int Offsets::BuffEntryBuffStartTime = 0xC;
int Offsets::BuffEntryBuffEndTime = 0x10;
int Offsets::BuffEntryBuffCount = 0x74;
int Offsets::BuffEntryBuffCountAlt = 0x24;
int Offsets::BuffEntryBuffCountAlt2 = 0;
int Offsets::BuffName = 0x8;
int Offsets::BuffEntryBuffNodeStart = 0x20;
int Offsets::BuffEntryBuffNodeCurrent = 0x24;
 
int Offsets::ItemListItem = 0xC;
int Offsets::ItemInfo = 0x20;
int Offsets::ItemInfoId = 0x68;
 
int Offsets::RendererWidth = 0xC;
int Offsets::RendererHeight = 0x10;
 
int Offsets::SpellBookActiveSpellCast = 0x20;
int Offsets::SpellBookSpellSlots = 0x478;
int Offsets::SpellSlotLevel = 0x1C;
int Offsets::SpellSlotTime = 0x24;
int Offsets::SpellSlotCharges = 0x54;
int Offsets::SpellSlotTimeCharge = 0x74;
int Offsets::SpellSlotDamage = 0x94;
int Offsets::SpellSlotSpellInfo = 0x120;
int Offsets::SpellInfoSpellData = 0x44;
int Offsets::SpellDataSpellName = 0x6C;
int Offsets::SpellDataMissileName = 0x6C;
int Offsets::SpellSlotSmiteTimer = 0x64;
int Offsets::SpellSlotSmiteCharges = 0x58;
int Offsets::SpellCastSpellInfo = 0x8;
int Offsets::SpellCastStartTime = 0x544;
int Offsets::SpellCastStartTimeAlt = 0x534;
int Offsets::SpellCastCastTime = 0x4C0;
int Offsets::SpellCastStart = 0x80;
int Offsets::SpellCastEnd = 0x8C;
int Offsets::SpellCastSrcIdx = 0x68;
int Offsets::SpellCastDestIdx = 0xC0;
 
int Offsets::ObjectMapCount = 0x2C;
int Offsets::ObjectMapRoot = 0x28;
int Offsets::ObjectMapNodeNetId = 0x10;
int Offsets::ObjectMapNodeObject = 0x14;
 
int Offsets::MissileSpellInfo = 0x278;
int Offsets::MissileSrcIdx = 0x2DC;
int Offsets::MissileDestIdx = 0x330;
int Offsets::MissileStartPos = 0x2F4;
int Offsets::MissileEndPos = 0x300;
 
int Offsets::MinimapObjectHud = 0x120;
int Offsets::MinimapHudPos = 0x44;
int Offsets::MinimapHudSize = 0x4C;
"""
