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

#mageLogic is basicaly the same as rangerLogic
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


#Attacks
def mageAttack(unit):
    
    best_target = 0
    for enemy in nearby:
        if priority_mage[enemy] > best_target:
            best_target = priority_mage[enemy]
            attack_target = enemy
    if gc.can_attack(unit.id, attack_target.id):
        gc.attack(unit.id, attack_target.id)


#method for blink
def blink(unit, location):
    posDir = list(bc.Direction)
    loc = random.choice(posDir)
    if gc.is_blink_ready(unit.id):
        gc.blink(unit.id, loc)
        
