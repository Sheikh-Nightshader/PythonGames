#!/usr/bin/env python3
#Code by Sheikh Nightshader
#Assassin Game

import os, sys, random, time

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

WIDTH, HEIGHT = 40, 20
MAX_PLAYER_HP = 30

def make_player(name):
    return {
        "name": name,
        "x": WIDTH//2,
        "y": HEIGHT//2,
        "symbol": RED + "𖨆" + RESET,
        "hp": 20,
        "inventory": [],
        "gold": 0,
        "kills": 0,
        "atk": 5,
        "defense": 1
    }

def generate_map():
    m = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for x in range(WIDTH):
        m[0][x] = m[HEIGHT-1][x] = "#"
    for y in range(HEIGHT):
        m[y][0] = m[y][WIDTH-1] = "#"
    for _ in range(60):
        x, y = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2)
        m[y][x] = random.choice(["𖠿", "𖠰", "ᨒ"])
    return m

def place_random(symbol, name, color):
    while True:
        x, y = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2)
        if game_map[y][x] == ".":
            return {"x": x, "y": y, "symbol": color + symbol + RESET, "name": name}

def place_target():
    while True:
        tx, ty = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2)
        if game_map[ty][tx] != ".": continue
        if (tx,ty) in [(handler["x"],handler["y"]), (safehouse["x"],safehouse["y"])]:
            continue
        collision = False
        for e in enemies:
            if (tx,ty) == (e["x"], e["y"]):
                collision = True; break
        if not collision:
            return {"x": tx, "y": ty, "symbol": CYAN + "𖨆" + RESET, "name": "Target", "hp": 30, "alive": True}

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def pause(msg):
    print(YELLOW + msg + RESET)
    input("Press ENTER to continue...")

def draw():
    clear()
    print(RED + "="*10 + " 🗡 Assassin Rogue 🗡 " + "="*10 + RESET)
    for y in range(HEIGHT):
        line = ""
        for x in range(WIDTH):
            if x == player["x"] and y == player["y"]:
                line += player["symbol"]
            elif x == handler["x"] and y == handler["y"]:
                line += handler["symbol"]
            elif x == safehouse["x"] and y == safehouse["y"]:
                line += safehouse["symbol"]
            elif target["alive"] and x == target["x"] and y == target["y"]:
                line += target["symbol"]
            else:
                drawn = False
                for e in enemies:
                    if e["alive"] and x == e["x"] and y == e["y"]:
                        line += e["symbol"]; drawn = True; break
                if not drawn:
                    line += game_map[y][x]
        print(line)
    status = "None"
    if mission_given and not mission_complete:
        status = "Eliminate Target"
    elif mission_complete and not returned:
        status = "Return to Handler"
    print(RED + f"{player['name']} HP: {player['hp']}/{MAX_PLAYER_HP}" + RESET +
          YELLOW + f"  Mission: {status}" + RESET +
          CYAN + f"  Inventory: {player['inventory']}" + RESET +
          GREEN + f"  Gold: {player['gold']}  Kills: {player['kills']}" + RESET)
    print("W/A/S/D = move | E = interact | Q = quit")

def find_enemy_at(x,y):
    for e in enemies:
        if e["alive"] and e["x"]==x and e["y"]==y:
            return e
    return None

def fight_enemy(e):
    pause(f"You prepare to fight {e['name']} (HP {e['hp']}).")
    while e["hp"] > 0 and player["hp"] > 0:
        action = input("Choose action: (A)ttack / (R)un: ").strip().lower()
        if action == "r":
            if random.random() < 0.5:
                pause("You escape the fight!")
                return
            else:
                pause("Failed to escape!")
        crit = random.random() < 0.1
        p_atk = max(0, player["atk"] - random.randint(0, e.get("defense",0)))
        if crit: p_atk *= 2
        e["hp"] -= p_atk
        pause(f"You strike {e['name']} for {p_atk}{' (CRIT!)' if crit else ''}! Enemy HP: {max(0,e['hp'])}")
        if e["hp"] <= 0:
            e["alive"] = False
            loot = f"{e['name']} token"
            player["inventory"].append(loot)
            player["gold"] += e.get("gold",0)
            player["kills"] += 1
            pause(f"You've eliminated {e['name']}! Loot: {loot} +{e.get('gold',0)} gold")
            return
        enemy_hit = max(0, e["damage"] - player["defense"])
        player["hp"] -= enemy_hit
        pause(f"{e['name']} strikes you for {enemy_hit}! HP: {player['hp']}")
        if player["hp"] <= 0:
            pause("You have died... Mission failed.")
            game_over()

def fight_target():
    pause("Eliminate the Target!")
    while target["hp"] > 0 and player["hp"] > 0:
        action = input("Choose action: (A)ttack / (R)un: ").strip().lower()
        if action == "r":
            pause("You cannot escape the Target!")
        crit = random.random() < 0.15
        p_atk = max(0, player["atk"] - 2)
        if crit: p_atk *= 2
        target["hp"] -= p_atk
        pause(f"You strike the Target for {p_atk}{' (CRIT!)' if crit else ''}! HP: {max(0,target['hp'])}")
        if target["hp"] <= 0:
            target["alive"] = False
            player["inventory"].append("Target's Head")
            player["gold"] += 50
            player["kills"] += 1
            pause("Target eliminated. Mission complete! +50 gold")
            return
        dmg = random.randint(2,6)
        player["hp"] -= max(0, dmg - player["defense"])
        pause(f"The Target strikes you for {dmg} (reduced by defense: {max(0,dmg - player['defense'])})! HP: {player['hp']}")
        if player["hp"] <= 0:
            pause("You were slain by the Target... Mission failed.")
            game_over()

def interact():
    global mission_given, mission_complete, returned
    e = find_enemy_at(player["x"], player["y"])
    if e:
        fight_enemy(e)
        return
    if target["alive"] and player["x"]==target["x"] and player["y"]==target["y"]:
        if not mission_given:
            pause("You have no active contract. Speak to your Handler first.")
            return
        confirm = input(RED + "Strike the Target now? (y/n): " + RESET).strip().lower()
        if confirm == "y":
            fight_target()
            if not target["alive"]:
                mission_complete = True
                pause("Mission complete! Return to your Handler.")
        else:
            pause("You step back for now.")
        return
    if player["x"]==handler["x"] and player["y"]==handler["y"]:
        if not mission_given:
            mission_given = True
            pause(f"{handler['name']}: Welcome, assassin. Your contract — eliminate the Target and any of their guards. Return with proof and be rewarded.")
            return
        elif mission_complete and not returned:
            returned = True
            end_game()
            return
        else:
            pause(f"{handler['name']}: Your contract awaits. Eliminate the Target first.")
            return
    if player["x"]==safehouse["x"] and player["y"]==safehouse["y"]:
        heal = random.randint(4,9)
        player["hp"] = min(MAX_PLAYER_HP, player["hp"] + heal)
        pause(f"The {safehouse['name']} restores {heal} HP. Your HP: {player['hp']}")
        return
    pause("Nothing to interact with here.")

def check_bump():
    e = find_enemy_at(player["x"], player["y"])
    if e:
        fight_enemy(e)

def move_enemies():
    for e in enemies:
        if not e["alive"]: continue
        dx,dy = random.choice([-1,0,1]), random.choice([-1,0,1])
        nx, ny = e["x"]+dx, e["y"]+dy
        if 0 < nx < WIDTH-1 and 0 < ny < HEIGHT-1 and game_map[ny][nx] == "." and (nx,ny) not in [(handler["x"],handler["y"]), (safehouse["x"],safehouse["y"]), (target["x"],target["y"])]:
            if find_enemy_at(nx, ny) is None:
                e["x"], e["y"] = nx, ny

def game_over():
    again = input(RED + "Play again? (y/n): " + RESET).strip().lower()
    if again == "y":
        start_game()
    else:
        sys.exit()

def end_game():
    base_score = player["gold"]
    kill_score = player["kills"] * 10
    mission_bonus = 50 if mission_complete else 0
    total_score = base_score + kill_score + mission_bonus
    pause(f"Handler: Excellent work, assassin. Contract complete. ENDING: You survive and gain reputation in the underground.\n\nYour Score:\nGold: {player['gold']}\nKills: {player['kills']} (+{kill_score} points)\nMission Bonus: {mission_bonus}\nTOTAL SCORE: {total_score}")
    game_over()

def start_game():
    global game_map, player, handler, safehouse, enemies, target, mission_given, mission_complete, returned
    clear()
    name = input("Enter your assassin name: ").strip() or "Player"
    game_map = generate_map()
    player = make_player(name)
    handler = place_random("𖨆", "Handler", GREEN)
    safehouse = place_random("𖠿", "Safehouse", BLUE)
    enemy_types = [
        {"symbol": MAGENTA+"𖨆"+RESET, "name":"Guard","damage":1,"hp":8, "gold":3},
        {"symbol": YELLOW+"𖨆"+RESET, "name":"Bodyguard","damage":2,"hp":10, "gold":5},
        {"symbol": WHITE+"𖨆"+RESET, "name":"Mercenary","damage":3,"hp":14, "gold":8},
    ]
    enemies = []
    for _ in range(12):
        et = random.choice(enemy_types)
        while True:
            ex, ey = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2)
            if game_map[ey][ex] == "." and (ex,ey) not in [(handler["x"],handler["y"]), (safehouse["x"],safehouse["y"])]:
                enemies.append({
                    "x": ex, "y": ey,
                    "symbol": et["symbol"], "name": et["name"],
                    "damage": et["damage"], "hp": et["hp"], "alive": True,
                    "gold": et["gold"]
                })
                break
    target = place_target()
    mission_given = False
    mission_complete = False
    returned = False

    while True:
        draw()
        action = input("Action: ").strip().lower()
        if action == "q":
            pause("Exiting. Stay in the shadows.")
            game_over()
        if action == "e":
            interact()
        else:
            if action == "w" and game_map[player["y"]-1][player["x"]] != "#":
                player["y"] -= 1
            elif action == "s" and game_map[player["y"]+1][player["x"]] != "#":
                player["y"] += 1
            elif action == "a" and game_map[player["y"]][player["x"]-1] != "#":
                player["x"] -= 1
            elif action == "d" and game_map[player["y"]][player["x"]+1] != "#":
                player["x"] += 1
            check_bump()
            move_enemies()

start_game()
