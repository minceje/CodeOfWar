"""
Created on Mon Apr  1 21:03:44 2019

Storing Mage code here for later

"""
#Mage stuff
#Inspiration taken from https://github.com/kmbrgandhi/tricycle_bot/blob/master/tricycle_bot_qualifying/Units/Mage.py

def timestep(unit):

    #Rename variables
    location = unit.location

    dir, attack_target, snipe, move_then_attack, visible_enemies, closest_enemy, signals = mage_sense(bc, unit, map_loc)
    
    #If it can see an enemy close by, it will attack
    if visible_enemies and closest_enemy is not None:
        enemy_loc = closest_enemy.location.map_location()
        f_f_quad = (int(enemy_loc.x / 5), int(enemy_loc.y / 5))
       
    #Move in range to attack, else just attacks
    if move_then_attack:
        #Checks if mage can move
        if dir != None and bc.is_move_ready(unit.id) and bc.can_move(unit.id, dir):
            bc.move_robot(unit.id, dir)

        #Attacks a unit if it can
        if attack_target is not None and bc.is_attack_ready(unit.id) and bc.can_attack(unit.id, attack_target.id):                
            bc.attack(unit.id, attack_target.id)



def mage_sense(gc, unit, location):
    enemies = bc.can_sense_unit(location)
  
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
        
        start_time = time.time()
        
        if attack is not None:
            if closest_enemy is not None:
                start_time = time.time()
                    
        else:
            if bc.is_move_ready(unit.id):

                if closest_enemy is not None:
                    next_turn_loc = location.add(dir)
                    
                    if attack is not None:
                        move_then_attack = True

    return dir, attack, blink, move_then_attack, visible_enemies, closest_enemy
