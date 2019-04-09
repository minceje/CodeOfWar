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
from datetime import datetime

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

#get our team from API
my_team = gc.team()
#these dictionaries set up the priorities for each unit to interact with
priority_rangers = {
    bc.UnitType.Worker : 3,
    bc.UnitType.Knight : 2,
    bc.UnitType.Healer : 1,
    bc.UnitType.Ranger : 1,
    bc.UnitType.Mage : 1,
    bc.UnitType.Factory : 4,
    bc.UnitType.Rocket : 4,
}

priority_healers = {
    bc.UnitType.Worker : 4,
    bc.UnitType.Knight : 3,
    bc.UnitType.Healer : 2,
    bc.UnitType.Ranger : 1,
    bc.UnitType.Mage : 2
}
#a directions dictionary used to approach
approach_dir = {
    (0,1) : bc.Direction.North,
    (1,1) : bc.Direction.Northeast,
    (1,0) : bc.Direction.East,
    (1,-1) : bc.Direction.Southeast,
    (0,-1) : bc.Direction.South,
    (-1,-1) : bc.Direction.Southwest,
    (-1,0) : bc.Direction.West,
    (-1,1) : bc.Direction.Northwest,
}
#sets the my_team and enemy_team variables to know who to attack or help
enemy_team = bc.Team.Red
if my_team == bc.Team.Red:
    enemy_team = bc.Team.Blue
#find the start map and original units at start of game
start_map = gc.starting_map(bc.Planet.Earth)
init_units = start_map.initial_units
for i in range(init_units.__len__()):
    if init_units.__getitem__(i).team == enemy_team:
        enemy_spawn = init_units.__getitem__(i).location.map_location()

#flag for sending units into battle, flipped when an army has begun amassing
release_units = False
#flag for sending units to the rockets for escape
escape = False
fight = False


print("pystarted")

random.seed(datetime.now())

#Research order 
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Mage)



#method to move any unit
def move(unit):
    #API returns any possible moves in list form
    possible_directions = list(bc.Direction)
    choices = []

    #find only the moves that are valid moves
    for direct in possible_directions:
        if gc.can_move(unit.id, direct):
            choices.append(direct)
    #if not choices:
    #    gc.disintegrate_unit(unit.id)
    #    return
    if choices:
        dir = random.choice(choices)
        #if unit can move and is ready to move, randomly move them to a new position
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, dir):
            gc.move_robot(unit.id, dir)

#Try to approach a given target destination. (Note: NOT unit)
def approach(unit, location, destination):
    global approach_dir

    #Find the difference in unit position and reduce it to a simple coordinate pair
    #for use with the approach_dir dictionary.
    x_diff = destination.x - location.x
    y_diff = destination.y - location.y

    x_move = x_diff
    y_move = y_diff

    #if there is an x_diff/y_diff, reduce it to a movement in one direction.
    if x_diff != 0:
        x_move = x_diff/abs(x_diff)
    if y_diff != 0:
        y_move = y_diff/abs(y_diff)

    #if there is no moves to make, exit.
    if (x_move,y_move) == (0,0):
        return

    #if we can move in an optimal direction, move that direction.
    dir = approach_dir[(x_move,y_move)]
    if gc.is_move_ready(unit.id) and gc.can_move(unit.id,dir):
        gc.move_robot(unit.id, dir)
        return
    #if cant move in optimal direction, try moving in a similar direction
    if x_move == 0:
        x_move = random.choice([-1,1])
    elif y_move == 0:
        y_move = random.choice([-1,1])
    else:
        if x_diff > y_diff:
            y_move = 0
        else:
            x_move = 0
    dir = approach_dir[(x_move,y_move)]
    if gc.is_move_ready(unit.id) and gc.can_move(unit.id,dir):
        gc.move_robot(unit.id, dir)
        return
    #if nothing else works, move randomly
    move(unit)


#logic for worker units
def workerWork(worker):
    global num_workers, total_number_factories, escape, full_vision, fight

    #if there is a worker deficit and we have the resources to replicate,
    #find a valid direction to do so.
    if num_workers < 7 and gc.karbonite() >= 60:
        for dir in directions:
            if gc.can_replicate(worker.id, dir):
                gc.replicate(worker.id, dir)
                return #once an action is performed, that worker is done

    nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.vision_range, enemy_team)
    if nearby:
        fight = True
        full_vision.extend(nearby)

    #build on any existing nearby blueprints, or repair damaged structures
    nearby = gc.sense_nearby_units(worker.location.map_location(), 2)
    for other in nearby:
        if gc.can_build(worker.id, other.id):
            gc.build(worker.id, other.id)
            return
        elif other.health < other.max_health and gc.can_repair(worker.id, other.id):
            gc.repair(worker.id, other.id)
            return
    #build factories until game reaches round 150, then focus on making units
    if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.round() < 150:
        for dir in directions:
            if gc.can_blueprint(worker.id, bc.UnitType.Factory, dir):
                gc.blueprint(worker.id, bc.UnitType.Factory, dir)
                return

    if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and gc.round() > 550:
        for dir in directions:
            if gc.can_blueprint(worker.id, bc.UnitType.Rocket, dir):
                gc.blueprint(worker.id, bc.UnitType.Rocket, dir)
                return

    #find a direction to harvest
    for dir in directions:
        if gc.can_harvest(worker.id, dir):
            gc.harvest(worker.id, dir)
            return
    #if this part of the code is reached, then the only thing left to do is move
    move(worker)

#factoryProduce takes a factory and first to ungarrison any available units
#then attempts to produce a ratio of a 4 rangers to 1 healer
def factoryProduce(factory):
    global num_healers, num_rangers, release_units, fight
    garrison = unit.structure_garrison()

    if num_rangers + num_healers > 15 or fight:
        release_units = True

    #If a unit is garrisoned, release them in an available spot.
    if len(garrison) > 0 and release_units:
        for dir in directions:
            if gc.can_unload(factory.id, dir):
                gc.unload(factory.id, dir)
    if gc.round() > 650:
        return
    #If the factory is available to produce another unit. If we have enough
    #healers, produce rangers.
    if gc.can_produce_robot(factory.id, bc.UnitType.Ranger):
        if num_rangers < num_healers * 4:
            gc.produce_robot(factory.id, bc.UnitType.Ranger)
        else:
            gc.produce_robot(factory.id, bc.UnitType.Healer)
        return

#Healer_heal finds units near the healer and attempts to heal them
def Healer_heal(unit):
    global enemy_spawn, my_team, full_vision

    location = unit.location

    #find nearby units on team
    nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.attack_range(), my_team)

    #if can heal, heal
    heal = False
    if gc.is_heal_ready(unit.id):
        lowest_health = unit
        for other in nearby:
            if other.health < lowest_health.health and other.health < other.max_health:
                lowest_health = other
                heal = True
        if gc.can_heal(unit.id, lowest_health.id) and heal:
            gc.heal(unit.id, lowest_health.id)
            return
    #if no heal targets, walk towards the action
    if full_vision:
        approach(unit, unit.location.map_location(),full_vision[0].location.map_location())
    else:
        approach(unit, unit.location.map_location(),enemy_spawn)

#Healer_overcharge finds a nearby unit and restores their ability charge.
def Healer_overcharge(unit):
    global my_team
    #if we can't overcharge, exit
    if not gc.is_overcharge_ready(unit.id):
        return

    #cannot overcharge if not at research level 3
    if bc.ResearchInfo().get_level(bc.UnitType.Healer) < 3:
        return

    #find our location
    location = unit.location

    #get all possible targets around, and choose one to heal
    possible_targets = sense_nearby_units_by_team(location.map_location(), unit.ability_range(), my_team)
    for other in possible_targets:
        if gc.can_heal(unit.id, other.id):
            gc.heal(unit.id, other.id)
            return

#Mars Info Finding and Rocket variables
marsMap = gc.starting_map(bc.Planet.Mars)
marsHeight = marsMap.height
marsWidth = marsMap.width

#add to this variable as rockets are built
safe_locations = []
#method to find a safe location on Mars to land using known Mars info from the API
def find_locations_Mars():
    global safe_locations
    component_num = 0
    for i in range(marsHeight):
        for j in range(marsWidth):
            if (i, j) not in safe_locations:
                temp_loc = bc.MapLocation(bc.Planet.Mars, i, j)
                try:
                    if marsMap.is_passable_terrain_at(temp_loc):
                        safe_locations.append((i, j)) #this stores the locations that are safe to use later
                        component_num += 1

                except Exception as e:
                    print(i, j)
                    print('Error:', e)
                    #traceback.print_exc()

#now choose a safe location to launch to per rocket
def findRocketLand(rocket):
    global safe_locations
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

    garrison = unit.structure_garrison()
    free_loc = findRocketLand(unit)

    if gc.can_launch_rocket(unit.id, free_loc):
        #if can launch, launch
        gc.launch_rocket(unit.id, free_loc)

#method to unload and garrison the rocket once built
def unloadRocket(rocket):
    garrison = unit.structure_garrison()
    if len(garrison) > 0:
        for d in directions:
            if gc.can_unload(unit.id, d):
                gc.unload(unit.id, d)

find_locations_Mars()
#method to move the units towards the rockets
def moveUnitToRocket(unit,nearby):
    if not gc.is_move_ready(unit.id):
        return
    #if ready to move
    #get a location of the unit
    location = unit.location.map_location()
    #use directions from above
    best = directions[0]
    #set a distance
    closest_distance = 100000
    #for each of nearby
    for x in nearby:
        if gc.can_load(x.id, unit.id):
            gc.load(x.id,unit.id)
            return
        next_location = x.location.map_location()
        #now the distance is from that location to the next one found
        current_distance = location.distance_squared_to(next_location)
        #if closer than the set closest distance, go there
        if current_distance < closest_distance:
            closest_distance = current_distance
            best = location.direction_to(next_location)
        #moving the units based off current location and if they can move
        range_index = 8
        for i in range(8):
            if directions[i] == best:
                range_index = i
                break
        for i in range(4):
            temp_index = (range_index + i + 9)%9
            if gc.can_move(unit.id, directions[temp_index]):
                gc.move_robot(unit.id, directions[temp_index])
                return
            temp_index = (range_index - i + 9)%9
            if gc.can_move(unit.id, directions[temp_index]):
                gc.move_robot(unit.id, directions[temp_index])
                return

#rangerAttack takes a unit and who is nearby to attempt an attack.
def rangerAttack(unit, nearby):
    global priority_rangers
    best_target = 0
    targets = [] #list of targets from least valuable to most
    #we find the best unit to attack from the priority_rangers dictionary
    #and attempt to attack the best unit.
    for enemy in nearby:
        #if enemy is too close, back away
        if gc.is_move_ready(unit.id):
            x_diff = unit.location.map_location().x - enemy.location.map_location().x
            y_diff = unit.location.map_location().y - enemy.location.map_location().y
            #backing away is done by reversing location and destination in approach function
            if (x_diff * x_diff) + (y_diff * y_diff) < 20:
                approach(unit,enemy.location.map_location(),unit.location.map_location())
        if priority_rangers[enemy.unit_type] > best_target:
            best_target = priority_rangers[enemy.unit_type]
            targets.append(enemy)

    #if we can attack, and something is nearby to attack, do so.
    if gc.is_attack_ready(unit.id):
        for i in range(len(targets)-1,-1,-1):
            if gc.can_attack(unit.id, targets[i].id):
                gc.attack(unit.id, targets[i].id)
                return
    if gc.is_move_ready(unit.id):
        approach(unit,unit.location.map_location(),targets[-1].location.map_location())

#rangerLogic handles movement when no enemies are nearby, and attack orders.
def rangerLogic(unit):
    global enemy_spawn, enemy_team, escape, full_vision
    #Make sure only rangers get ranger orders.
    if unit.unit_type != bc.UnitType.Ranger:
        return

    location = unit.location
    #if its time to escape, try to run to a rocket
    if escape and unit.location.map_location().planet == bc.Planet.Earth:
        nearby = gc.sense_nearby_units_by_type(location.map_location(), unit.vision_range, bc.UnitType.Rocket)
        if nearby:
            moveUnitToRocket(unit,nearby)
            return

    #sense enemies that are nearby, and then attack them
    nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.vision_range, enemy_team)
    if nearby:
        full_vision.extend(nearby)
        rangerAttack(unit, nearby)

    #if no one is nearby then approach the enemy, if no enemies are seen by anyone, approach enemy spawn
    if not nearby and gc.is_move_ready(unit.id):
        if full_vision:
            approach(unit, unit.location.map_location(),full_vision[0].location.map_location())
        else:
            approach(unit, unit.location.map_location(),enemy_spawn)

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
        if unit.unit_type == bc.UnitType.Rocket:
            total_number_rockets += 1
            
    # shared unit vision
    full_vision = []

    try:
        # walk through our units:
        for unit in gc.my_units():
            location = unit.location
            if unit.unit_type == bc.UnitType.Rocket:
                escape = True
                if unit.location.map_location().planet == bc.Planet.Mars:
                    unloadRocket(unit)
                elif len(unit.structure_garrison()) >= 8 or gc.round() >= 748 or unit.health < unit.max_health:
                    launch(unit)
            elif unit.unit_type == bc.UnitType.Factory:
                factoryProduce(unit)
            elif unit.unit_type == bc.UnitType.Worker:
                workerWork(unit)
            elif unit.unit_type == bc.UnitType.Healer:
                if location.is_on_map():
                    Healer_heal(unit)
            elif unit.unit_type == bc.UnitType.Ranger:
                if location.is_on_map():
                    rangerLogic(unit)

        #when we want to move to rockets call is
        #moveUnitToRocket(unit)
        #want to make sure it is right time in the game and we have enough units to fill the rockets
        #launch(unit id of rocket to launch)

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
