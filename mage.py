"""
Created on Mon Apr  1 21:03:44 2019
Storing Mage code here for later
"""
#Mage stuff


priority_mage={
    bc.UnitType.Worker : 2
    bc.UnitType.Knight : 2
    bc.UnitType.Healer : 3
    bc.UnitType.Ranger : 1
    bc.UnitType.Mage : 1
    bc.UnitType.Factory : 4
    bc.UnitType.Rockets : 4
}
#mageAttack is very similar to rangerAttack
def mageAttack(unit, nearby):
    global priority_rangers
    best_target = 0

    #we find the best unit to attack from the priority_rangers dictionary
    #and attempt to attack the best unit.
    for enemy in nearby:
        if priority_mage[enemy.unit_type] > best_target:
            best_target = priority_mage[enemy.unit_type]
            attack_target = enemy

    #find the difference in our location and the enemy location for approach function
    x_diff = unit.location.map_location().x - attack_target.location.map_location().x
    y_diff = unit.location.map_location().y - attack_target.location.map_location().y

    #if we can attack, and something is nearby to attack, do so. If not, approach them/blink to them
    if gc.is_attack_ready(unit.id):
        if gc.can_attack(unit.id, attack_target.id):
            gc.attack(unit.id, attack_target.id)
        else:
            if gc.can_blink():
            blink(unit, attack_target.location.map_location())
        elif unit.is_move_ready():
            approach(unit,attack_target.location.map_location())
            

#method for blink
def blink(unit, location):
    posDir = list(bc.Direction)
    loc = random.choice(posDir)
    if gc.is_blink_ready(unit.id):
        gc.blink(unit.id, loc)
        
#mageLogic is basically the same as rangerLogic
def mageLogic(unit):
    
    if unit.unit_type != bc.UnitType.Mage:
        return
    
    #Attacks any nearby groups
    nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.vision_range(), enemy_team)
    if nearby:
        mageAttack(unit)

    if not nearby:
        if gc.can_blink():
            blink(unit)
        elif unit.is_move_ready():
            move(unit)
        
