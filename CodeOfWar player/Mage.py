#code adapted from https://github.com/kmbrgandhi/tricycle_bot/blob/master/tricycle_bot_qualifying/Units/Mage.py
import battlecode as bc
import random
import sys
import traceback
import time


order = [bc.UnitType.Worker, bc.UnitType.Knight, bc.UnitType.Ranger, bc.UnitType.Mage,
         bc.UnitType.Healer, bc.UnitType.Factory, bc.UnitType.Rocket]  # storing order of units


def timestep(unit):
     
    location = unit.location

    if location.is_on_map():
        # Add new ones to unit_locations, else just get the location
        if unit.id not in variables.unit_locations:
            loc = unit.location.map_location()
            f_f_quad = (int(loc.x / quadrant_size), int(loc.y / quadrant_size))
            quadrant_battles[f_f_quad].add_ally(unit.id, "mage")

        dir, attack_target, move_then_attack, visible_enemies, closest_enemy = mage_sense(gc, unit, mage_roles, map_loc, targeting_units)
        #If it can see an enemy close by, it will attack
        if visible_enemies and closest_enemy is not None:
            enemy_loc = closest_enemy.location.map_location()
            f_f_quad = (int(enemy_loc.x / 5), int(enemy_loc.y / 5))
            if f_f_quad not in next_turn_battle_locs:
                next_turn_battle_locs[f_f_quad] = (map_loc, 1)
            else:
                next_turn_battle_locs[f_f_quad] = (
                next_turn_battle_locs[f_f_quad][0], next_turn_battle_locs[f_f_quad][1] + 1)
            
            if attack_target is not None and bc.is_attack_ready(unit.id) and bc.can_attack(unit.id, attack_target.id):
                if attack_target.id not in targeting_units:
                    targeting_units[attack_target.id] = 1
                else:
                    targeting_units[attack_target.id] += 1
                bc.attack(unit.id, attack_target.id)
        else:
            if attack_target is not None and bc.is_attack_ready(unit.id) and bc.can_attack(unit.id, attack_target.id):
                if attack_target.id not in targeting_units:
                    targeting_units[attack_target.id] = 1
                else:
                    targeting_units[attack_target.id] += 1
                bc.attack(unit.id, attack_target.id)

            if dir != None and bc.is_move_ready(unit.id) and bc.can_move(unit.id, dir):
                bc.move_robot(unit.id, dir)
   
#Checking to go to mars
def go_to_mars_sense(gc, unit, battle_locs, location, enemies, direction_to_coord, bfs_array, targeting_units,
                     rocket_locs):
    
    
    # print('GOING TO MARS')
    signals = {}
    dir = None
    attack = None
    blink = None
    closest_enemy = None
    move_then_attack = False
    visible_enemies = False

    if len(enemies) > 0:
        visible_enemies = True
    start_coords = (location.x, location.y)
    
    
    if max(abs(target_loc.x - start_coords[0]), abs(target_loc.y - start_coords[1])) == 1:
        rocket = gc.sense_unit_at_location(target_loc)
        if gc.can_load(rocket.id, unit.id):
            gc.load(rocket.id, unit.id)
    else:
        target_coords = (target_loc.x, target_loc.y)

        if bfs_array[start_coords_val, target_coords_val] != float('inf'):
            choice_of_dir = random.choice(best_dirs)
            shape = direction_to_coord[choice_of_dir]
            for option in options:
                if gc.can_move(unit.id, option):
                    dir = option
                    break
                    # print(dir)

    return dir, attack, blink, move_then_attack, visible_enemies, closest_enemy, signals


def mage_sense(gc, unit, mage_roles, location, targeting_units):
    
    enemies = gc.sense_nearby_units_by_team(location, unit.vision_range, variables.enemy_team)
    if unit.id in mage_roles["go_to_mars"]:
        return go_to_mars_sense(gc, unit, location, enemies, targeting_units)
    signals = {}
    dir = None
    attack = None
    blink = None
    closest_enemy = None
    move_then_attack = False
    visible_enemies = False
    start_time = time.time()
    
    if len(enemies) > 0:
        visible_enemies = True
        start_time = time.time()
        closest_enemy = None
        closest_dist = float('inf')
        
        start_time = time.time()

    return dir, attack, blink, move_then_attack, visible_enemies, closest_enemy
