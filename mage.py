# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 21:03:44 2019

Storing Mage code here for later

"""
#Mage stuff
#Inspiration taken from https://github.com/kmbrgandhi/tricycle_bot/blob/master/tricycle_bot_qualifying/Units/Mage.py
import Units.sense_util as sense_util
import Units.explore as explore
import Units.variables as variables

#checks where the mage is
if variables.curr_planet == bc.Planet.Earth:
    passable_locations = variables.passable_locations_earth
else:
    passable_locations = variables.passable_locations_mars
directions = variables.directions

def timestep(unit):
    #Rename variables
    gc = variables.gc
    mage_roles = variables.mage_roles
    info = variables.info
    next_turn_battle_locs = variables.next_turn_battle_locs

    #Adds the mage to the fighting roster, or removes it from the rocket
    if unit.id in mage_roles["go_to_mars"] and info[6] == 0:
        mage_roles["go_to_mars"].remove(unit.id)
    if unit.id not in mage_roles["fighter"]:
        mage_roles["fighter"].append(unit.id)

    #Rename variables
    location = unit.location
    my_team = variables.my_team
    targeting_units = variables.targeting_units

    #Checks where a battle takes place and changes the sqaure size
    quadrant_battles = variables.quadrant_battle_locs
    if variables.curr_planet == bc.Planet.Earth:
        quadrant_size = variables.earth_quadrant_size
    else:
        quadrant_size = variables.mars_quadrant_size

    if location.is_on_map():
        #Locates new mages made and adds to the mage roster
        if unit.id not in variables.unit_locations:
            loc = unit.location.map_location()
            variables.unit_locations[unit.id] = (loc.x, loc.y)
            f_f_quad = (int(loc.x / quadrant_size), int(loc.y / quadrant_size))
            quadrant_battles[f_f_quad].add_ally(unit.id, "mage")

        #Tells the mage to get on the rocket
        map_loc = location.map_location()
        if variables.curr_planet == bc.Planet.Earth and len(mage_roles["go_to_mars"]) < 14 and unit.id not in \
                mage_roles["go_to_mars"] and unit.id in mage_roles["fighter"]:
            for rocket in variables.rocket_locs:
                target_loc = variables.rocket_locs[rocket]
                if sense_util.distance_squared_between_maplocs(map_loc, target_loc) < 150:
                    variables.which_rocket[unit.id] = (target_loc, rocket)
                    mage_roles["go_to_mars"].append(unit.id)
                    mage_roles["fighter"].remove(unit.id)
                    break

        dir, attack_target, snipe, move_then_attack, visible_enemies, closest_enemy, signals = mage_sense(gc, unit,
                                                                                                            variables.last_turn_battle_locs,
                                                                                                            mage_roles,
                                                                                                            map_loc,
                                                                                                            variables.direction_to_coord,
                                                                                                            variables.bfs_array,
                                                                                                            targeting_units,
                                                                                                            variables.rocket_locs)
        #If it can see an enemy close by, it will attack
        if visible_enemies and closest_enemy is not None:
            enemy_loc = closest_enemy.location.map_location()
            f_f_quad = (int(enemy_loc.x / 5), int(enemy_loc.y / 5))
            if f_f_quad not in next_turn_battle_locs:
                next_turn_battle_locs[f_f_quad] = (map_loc, 1)
            else:
                next_turn_battle_locs[f_f_quad] = (
                next_turn_battle_locs[f_f_quad][0], next_turn_battle_locs[f_f_quad][1] + 1)

        #Move in range to attack, else just attacks
        if move_then_attack:
            #Checks if mage can move
            if dir != None and gc.is_move_ready(unit.id) and gc.can_move(unit.id, dir):
                gc.move_robot(unit.id, dir)

            #Attacks a unit if it can
            if attack_target is not None and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, attack_target.id):
                if attack_target.id not in targeting_units:
                    targeting_units[attack_target.id] = 1
                else:
                    targeting_units[attack_target.id] += 1
                gc.attack(unit.id, attack_target.id)
        else:
            #Attacks a unit if it can
            if attack_target is not None and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, attack_target.id):
                if attack_target.id not in targeting_units:
                    targeting_units[attack_target.id] = 1
                else:
                    targeting_units[attack_target.id] += 1
                gc.attack(unit.id, attack_target.id)

#Checking to go to mars
def go_to_mars_sense(gc, unit, battle_locs, location, enemies, direction_to_coord, bfs_array, targeting_units,
                     rocket_locs):
    signals = {}
    #Changes variable values
    dir = None
    attack = None
    blink = None
    closest_enemy = None
    move_then_attack = False
    visible_enemies = False

    #If there's any enemies, change visible_enemies
    if len(enemies) > 0:
        visible_enemies = True
    start_coords = (location.x, location.y)

    #Rocket was launched
    if unit.id not in variables.which_rocket or variables.which_rocket[unit.id][1] not in variables.rocket_locs:
        variables.mage_roles["go_to_mars"].remove(unit.id)
        return dir, attack, blink, move_then_attack, visible_enemies, closest_enemy, signals
    target_loc = variables.which_rocket[unit.id][0]

    #Rocket was destroyed
    if not gc.has_unit_at_location(target_loc):
        variables.mage_roles["go_to_mars"].remove(unit.id)
        return dir, attack, blink, move_then_attack, visible_enemies, closest_enemy, signals
    
    #Checks if the rocket is ready and has a landing point
    if max(abs(target_loc.x - start_coords[0]), abs(target_loc.y - start_coords[1])) == 1:
        rocket = gc.sense_unit_at_location(target_loc)
        if gc.can_load(rocket.id, unit.id):
            gc.load(rocket.id, unit.id)
    else:
        target_coords = (target_loc.x, target_loc.y)
        start_coords_val = Ranger.get_coord_value(start_coords)
        target_coords_val = Ranger.get_coord_value(target_coords)

        if bfs_array[start_coords_val, target_coords_val] != float('inf'):
            best_dirs = Ranger.use_dist_bfs(start_coords, target_coords, bfs_array)
            choice_of_dir = random.choice(best_dirs)
            shape = direction_to_coord[choice_of_dir]
            options = sense_util.get_best_option(shape)
            for option in options:
                if gc.can_move(unit.id, option):
                    dir = option
                    break

    return dir, attack, blink, move_then_attack, visible_enemies, closest_enemy, signals


def mage_sense(gc, unit, battle_locs, mage_roles, location, direction_to_coord, bfs_array, targeting_units,
                 rocket_locs):
    enemies = gc.sense_nearby_units_by_team(location, unit.vision_range, variables.enemy_team)
    if unit.id in mage_roles["go_to_mars"]:
        return go_to_mars_sense(gc, unit, battle_locs, location, enemies, direction_to_coord, bfs_array,
                                targeting_units, rocket_locs)
    signals = {}
    #Changes variable values
    dir = None
    attack = None
    blink = None
    closest_enemy = None
    move_then_attack = False
    visible_enemies = False
    start_time = time.time()
    
    #If there are enemies, find the closest one, and then attack, or just goes on the rocket
    if len(enemies) > 0:
        visible_enemies = True
        start_time = time.time()
        closest_enemy = None
        closest_dist = float('inf')
        for enemy in enemies:
            loc = enemy.location
            if loc.is_on_map():
                dist = sense_util.distance_squared_between_maplocs(loc.map_location(), location)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_enemy = enemy
        
        start_time = time.time()
        
        if attack is not None:
            if closest_enemy is not None:
                start_time = time.time()
                    
                    start_time = time.time()
                    dir = sense_util.best_available_direction(gc, unit, [closest_enemy])
                    
        else:
            if gc.is_move_ready(unit.id):

                if closest_enemy is not None:
                    next_turn_loc = location.add(dir)
                    
                    if attack is not None:
                        move_then_attack = True
                    
    else:
        
        if len(rocket_locs) > 0 and gc.round() > 660 and variables.curr_planet == bc.Planet.Earth:
            if dir is not None:
                return dir, attack, blink, move_then_attack, visible_enemies, closest_enemy, signals

    return dir, attack, blink, move_then_attack, visible_enemies, closest_enemy, signals


#Updates the number of mages
def update_mages():
    """
    1. If no rockets, remove any rangers from going to mars.
    2. Account for launched / destroyed rockets (in going to mars sense)
    """
    gc = variables.gc
    mage_roles = variables.mage_roles
    which_rocket = variables.which_rocket
    rocket_locs = variables.rocket_locs
    info = variables.info

    #If mages were on the rocket, or if they were destroyed on with rocket
    for mage_id in mage_roles["go_to_mars"]:
        no_rockets = True if info[6] == 0 else False
        if mage_id not in which_rocket or which_rocket[mage_id][1] not in rocket_locs:
            launched_rocket = True
        else:
            launched_rocket = False
            target_loc = which_rocket[mage_id][0]
            if not gc.has_unit_at_location(target_loc):
                destroyed_rocket = True
            else:
                destroyed_rocket = False
        if no_rockets or launched_rocket or destroyed_rocket:
            mage_roles["go_to_mars"].remove(mage_id)
