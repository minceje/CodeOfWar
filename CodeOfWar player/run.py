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

enemy_team = bc.Team.Red
if my_team == bc.Team.Red:
    enemy_team = bc.Team.Blue

start_map = gc.starting_map(bc.Planet.Earth)
init_units = start_map.initial_units
for i in range(init_units.__len__()):
    if init_units.__getitem__(i).team == enemy_team:
        enemy_spawn = init_units.__getitem__(i).location.map_location()


print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
#gc.queue_research(bc.UnitType.Rocket)
#gc.queue_research(bc.UnitType.Worker)
#gc.queue_research(bc.UnitType.Knight)
#the three levels if can be researched for Healer
#gc.queue_research(bc.UnitType.Healer)
#gc.queue_research(bc.UnitType.Healer)
#gc.queue_research(bc.UnitType.Healer)
#For now here is the research order
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Mage)


'''
TODO:
    -add to research-
    -Carly fix mage code for later use
    -Zach: Knights and Rangers, Mars attack logic
    -Jen: Rocket launch
    -Matt: Factories and more Worker stuff, Earth Logic
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
def move(unit):
    #API returns any possible moves in list form
    possible_directions = list(bc.Direction)
    choices = []
    for direct in possible_directions:
        if gc.can_move(unit.id, direct):
            choices.append(direct)
    if not choices:
        gc.disintegrate_unit(unit.id)
        return
    dir = random.choice(choices)
    #if unit can move and is ready to move, randomly move them to a new position
    if gc.is_move_ready(unit.id) and gc.can_move(unit.id, dir):
        gc.move_robot(unit.id, dir)

#approach a given target, or at least try to
def approach(unit, destination):
    global approach_dir
    x_diff = destination.x - unit.location.map_location().x
    y_diff = destination.y - unit.location.map_location().y
    x_move = x_diff
    y_move = y_diff
    if x_diff != 0:
        x_move = x_diff/abs(x_diff)
    if y_diff != 0:
        y_move = y_diff/abs(y_diff)
    if (x_move,y_move) == (0,0):
        return
    dir = approach_dir[(x_move,y_move)]
    if gc.is_move_ready(unit.id) and gc.can_move(unit.id,dir):
        gc.move_robot(unit.id, dir)
        return
    #if cant move in optimal direction, and optimal direction was diag, try moving straight
    if x_move != 0 and y_move != 0:
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
#CURRENT TODOS: Building rockets, repairing structures
def workerWork(worker):
    global num_workers, total_number_factories
    #if there is a worker deficit and we have the resources to replicate,
    #find a valid direction to do so.
    if num_workers < 10 and gc.karbonite() >= 60:
        for dir in directions:
            if gc.can_replicate(worker.id, dir):
                gc.replicate(worker.id, dir)
                print('replicating!')
                return #once an action is performed, that worker is done
    #build on any existing nearby blueprints. Took this bit of code from
    #below. Not entirely sure what the second param in this method is, and
    #I couldnt find it documented anywhere.
    nearby = gc.sense_nearby_units(worker.location.map_location(), 2)
    for other in nearby:
        if gc.can_build(worker.id, other.id):
            gc.build(unit.id, other.id)
            return
    #5 is an arbitrary limit for now
    if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and total_number_factories < 5:
        for dir in directions:
            if gc.can_blueprint(worker.id, bc.UnitType.Factory, dir):
                gc.blueprint(worker.id, bc.UnitType.Factory, dir)
                print('built a factory!')
                return
    #find a direction to harvest or set a blueprint
    for dir in directions:
        if gc.can_harvest(worker.id, dir):
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

#produce units in factories, and unload them
def factoryProduce(factory):
    global num_healers, num_rangers
    garrison = unit.structure_garrison()
    if len(garrison) > 0:
        for dir in directions:
            if gc.can_unload(factory.id, dir):
                gc.unload(factory.id, dir)
    #going for 4:1 rangers:healers for now
    if gc.can_produce_robot(factory.id, bc.UnitType.Ranger):
        if num_healers * 4 < num_rangers:
            gc.produce_robot(factory.id, bc.UnitType.Healer)
            return
        gc.produce_robot(factory.id, bc.UnitType.Ranger)
        return

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
#(marsHeight, marsWidth) = gc.find_dimensions(bc.Planet.Mars)
marsHeight = 10
marsWidth = 10

#gc.karbonite() >= 150 and number of units enough, then build rocket
total_number_rockets = 0
#add to this variable as rockets are built
safe_locations = []
#method to find a safe location on Mars to land using known Mars info from the API
def find_locations_Mars():
    global safe_locations
    component_num = 0
    for i in range(marsHeight+1):
        for j in range(marsWidth+1):
            if (i, j) not in safe_locations:
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
#method to move the rockets towards the rockets
def moveUnitToRocket(unit):
    if not gc.is_move_ready(unit.id):
        return
    #if ready to move
    #get a location of the unit
    location = unit.location.map_location()
    #use directions from above
    best = directions[0]
    #set a distance
    closest_distance = 100000
    #find nearby rocket
    nearby = gc.sense_nearby_units_by_type(location, unit.vision_range, bc.UnitType.Rocket)
    #for each of nearby
    for x in nearby:
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

def rangerAttack(unit, nearby):
    global priority_rangers
    best_target = 0
    for enemy in nearby:
        #i don't know the proper code for this
        #if enemy is too close, back away:
            #code here
        if priority_rangers[enemy.unit_type] > best_target:
            best_target = priority_rangers[enemy.unit_type]
            attack_target = enemy
    x_diff = unit.location.map_location().x - attack_target.location.map_location().x
    y_diff = unit.location.map_location().y - attack_target.location.map_location().y
    if gc.is_attack_ready(unit.id):
        if gc.can_attack(unit.id, attack_target.id):
            gc.attack(unit.id, attack_target.id)
        else:
            approach(unit,attack_target.location.map_location())

#Ranger start
#TODO: Implement logic to move in groups once enemy has been found
def rangerLogic(unit):
    global enemy_spawn
    #just to be sure only rangers receive ranger orders
    if unit.unit_type != bc.UnitType.Ranger:
        return

    #if gc.round < 200:
    #sense enemies that are nearby
    location = unit.location
    nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.vision_range, enemy_team)
    if nearby:
        rangerAttack(unit, nearby)
    #however, if there is no nearby enemies, move randomly
    #it's extremely important to move randomly at the start
    #to find out more about surrounding area, and hopefully
    #the enemy position. Could be improved to finding if we
    #are near a wall and going the opposite direction
    if not nearby:
        if gc.is_move_ready(unit.id):
            approach(unit, enemy_spawn)
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
    # frequent try/catches are a good idea
    try:
        # walk through our units:
        for unit in gc.my_units():
            location = unit.location
            if unit.unit_type == bc.UnitType.Factory:
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
