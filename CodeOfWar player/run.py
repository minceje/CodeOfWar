'''
CodeOfWar
COSC 370 AI Battlecode Project
Jennifer Mince, Carly Good, Matt Manoly, Zachary Taylor

Code for Inspiration: https://github.com/AnPelec/Battlecode-2018/blob/master/Project%20Achilles/run.py
'''

import battlecode as bc
import random
import sys
import traceback
import time

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

my_team = gc.team()
'''
enemy_team = bc.Team.Red
if my_team == bc.Team.Red:
    enemy_team = bc.Team.Blue
random.seed(datetime.now())

'''

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)
#the three levels if can be researched for Healer
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Healer) 

#get our team from API
my_team = gc.team()

'''
TODO:
    -add to research
    -Carly: Mage finish
    -Zach: Knights and Rangers
    -Jen: Healers and a move_unit method- done
    -Matt: Factories and more Worker stuff
    -Mars logic- all attacking once we get there, cannot build
    -Matt: Figure out when to call rocket launches (how many units per rocket, how late in the round)
'''


'''
Strategy:
    First use given workers and given 100 Karbonite- replicate to make more? Worker research to upgrade them- costs 25 rounds
    10-15 workers for karbonite harvesting
    factory produce knights, want to research that unit one at a time, do not go over 3-4 times
    workers replicate

    Then create a rocket as soon as we can, multiple, and collect resources
    5-10 units work together to make rocket, per group of rockets (full capability is 12 at level 3)

    Around round 700, get in rockets and fly to Mars

    Mars: create as many units as possible to win
'''
#method to move any unit
def move(unit, place, moveType):
    #API returns any possible moves in list form
    possible_directions = list(bc.Direction)
    dir = random.choice(possible_directions)
    #if unit can move and is ready to move, randomly move them to a new position
    if gc.is_move_ready(unit.id) and gc.can_move(unit.id, dir):
        gc.move_robot(unit.id, dir)
        
#logic for worker units
#CURRENT TODOS: Building rockets, repairing structures, reacting to enemy units
def workerWork(worker):
    #if there is a worker deficit and we have the resources to replicate,
    #find a valid direction to do so.
    if num_workers < 10 and gc.karbonite() >= 60:
        for dir in directions:
            if gc.can_replicate(worker.id, dir):
                replicate(worker.id, dir)
                print('replicating!')
                return #once an action is performed, that worker is done
        #build on any existing nearby blueprints. Took this bit of code from
        #below. Not entirely sure what the second param in this method is, and
        #I couldnt find it documented anywhere.
    nearby = gc.sense_nearby_units(worker.location.map_location(), 2)
    for other in nearby:
        if gc.can_build(worker.id, other.id):
            gc.build(unit.id, other.id)
            print('built a factory!')
            return
        #im not sure when the best times to build factories are, so for now
        #its just an arbitrary 10% chance they try doing that instead of
        #harvesting. This will only happen if there is enough Karbonite
        #to make a factory in the first place
    if gc.karbonite() > bc.UnitType.Factory.blueprint_cost():
        fact_chance = random.randint(0,9)
    else:
        fact_chance = 1
        #find a direction to harvest or set a blueprint
    for dir in directions:
        if fact_chance == 0:
            if gc.can_blueprint(worker.id, bc.UnitType.Factory, dir):
                gc.blueprint(worker.id, bc.UnitType.Factory, dir)
                return
        elif gc.can_harvest(worker.id, dir):
            gc.harvest(worker.id, dir)
            return
        #if this part of the code is reached, then the only thing left to do is move
        if gc.is_move_ready(worker.id):
            choices = [] #list of possible directions
            for dir in directions:
                if gc.can_move(worker.id, dir):
                    choices.append(dir)
            #if there is a valid square to move to, do so
            if choices:
                gc.move_robot(worker.id, random.choice(choices))
                return
            #if there isnt, then it seems to be stuck...and it must die
            gc.disintegrate_unit(worker.id)
    
#method to heal nearby units           
def Healer_heal(unit):
    if not gc.is_heal_ready(unit.id):
        return
    location = unit.location
    #find nearby units on team
    nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.attack_range(), my_team)
    #if can heal, heal
    for other in nearby:
        if gc.can_heal(unit.id, other.id):
            gc.heal(unit.id, other.id)
            return 
        
#method to call when want to Healer overcharge         
def Healer_overcharge(unit):
    if not gc.is_overcharge_ready(unit.id):
        return
    #cannot overcharge if not at level 3
    if bc.ResearchInfo().get_level(bc.UnitType.Healer) < 3:
        return
    location = unit.location
    #get all possible targets arounc
    possible_targets = sense_nearby_units_by_team(location.map_location(), unit.ability_range(), my_team)
    for other in possible_targets:
        if gc.can_heal(unit.id, other.id):
            gc.heal(unit.id, other.id)
            return
          
#Mars Info Finding and Rocket variables
marsMap = gc.starting_map(bc.Planet.Mars)
(marsHeight, marsWidth) = find_dimensions(bc.Planet.Mars)

#gc.karbonite() >= 150 and number of units enough, then build rocket
total_number_rockets = 0
#add to this variable as rockets are built

#method to find a safe location on Mars to land using known Mars info from the API
def find_locations_Mars():
    component_num = 0
    for i in range(marsHeight+1):
        for j in range(marsWidth+1):
            if (i, j) not in component:
                temp_loc = bc.MapLocation(bc.Planet.Mars, i, j)
                try:
                    if marsMap.is_passable_terrain_at(temp_loc):
                        safe_locations.append((i, j)) #this stores the locations that are safe to use later
                        component_num += 1

                except Exception as e:
                    print(i, j)
                    print('Error:', e)
                    traceback.print_exc()
                    
#now choose a safe location to launch to per rocket
def findRocketLand(rocket):
    #not sure what range to use
    temp_range= 5
	for t in range(temp_range):
	    return_value = random.choice(safe_locations) #calls locations from above method
	    if (t < temp_range -1):
	        continue
        return bc.MapLocation(bc.Planet.Mars, return_value[0], return_value[1])
        #returns the map location to land on

#method to launch the rocket
def launch(unit):
    global total_number_rockets

    #if the round is the right number
    if gc.round() > 700:
        return
    #need to send the units into rocket and check, yes enough are in the rocket so we can launch it

    garrison = unit.structure_garrison()
    freeMarsLoc = findRocketLand(unit)

    if gc.can_launch_rocket(unit.id, free_loc):
        #if can launch, launch
        gc.launch_rocket(unit.id, free_loc)
        total_number_rockets -= 1

#method to unload and garrison the rocket once built
def unloadRocket(rocket):
		garrison = unit.structure_garrison()
		if len(garrison) > 0:
			for d in directions:
				if gc.can_unload(unit.id, d):
					gc.unload(unit.id, d)

find_locations_Mars()

while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')
	# count how much of each unit we have at the beginning of each turn
	num_workers = 0
	num_knights = 0
	num_healers = 0
	num_rangers = 0
	num_mages = 0
	total_number_factories = 0
	total_number_rockets = 0
	for unit in gc.my_units():
		if unit.unit_type == bc.UnitType.Worker:
			num_workers += 1
		if unit.unit_type == bc.UnitType.Knight:
			num_knights += 1
		if unit.unit_type == bc.UnitType.Healer:
			num_healers += 1
		if unit.unit_type == bc.UnitType.Ranger:
			num_rangers += 1
		if unit.unit_type == bc.UnitType.Mage:
			num_mages += 1
		if unit.unit_type == bc.UnitType.Factory:
			total_number_factories += 1
		if unit.unit_type == bc.UnitType.Rockets:
			total_number_rockets += 1
    # frequent try/catches are a good idea
    try:
        # walk through our units:
        for unit in gc.my_units():
   
            if unit.unit_type == bc.UnitType.Worker:
                workerWork(unit)

            # first, factory logic
            if unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        print('unloaded a knight!')
                        gc.unload(unit.id, d)
                        continue
                elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                    gc.produce_robot(unit.id, bc.UnitType.Knight)
                    print('produced a knight!')
                    continue

			'''
            # first, let's look for nearby blueprints to work on
            location = unit.location
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                        print('built a factory!')
                        # move onto the next unit
                        continue
                    if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                        print('attacked a thing!')
                        gc.attack(unit.id, other.id)
                        continue

            # okay, there weren't any dudes around
            # pick a random direction:
            d = random.choice(directions)

            # or, try to build a factory:
            if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                gc.blueprint(unit.id, bc.UnitType.Factory, d)
            # and if that fails, try to move
            elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)
			'''
       # if current_unit.unit_type == bc.UnitType.Rocket:
           #unload_rocket(current_unit)

    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()

	
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
'''

A MapLocation represents a concrete space on a given planet. It has x and y coordinates,
in addition to the planet itself, as attributes.


A Location represents the location of a robot. Whenever a robot is on a map, this object maps directly to a MapLocation object.
However, this is not always the case! A Location may also represent a point in space (as in the case of a rocket traveling to Mars),
or a space in a structure’s garrison.
Methods can be used to determine, more concretely, what a Location represents.
'''
#To Handle:
    #Earth:
        #impassible water spots
        #Factories
        #Workers- pick up harvest karbonite, build, repair, blueprint, or replicate (1 to 3 at start)
        #Knights- javelin
        #Mages- fight
        #Rangers- snipe
        #Healers- heal
        #other robots from opponent
        #Rockets to mars: need to build, then find a correct space to land and survive
    #Mars:
        #rocketing to land in a good spot, not right away, but before the flood on Earth
        #karbonite, structures, other robots
        #unwalkable terrain
        #meteor storms- recheck square
