# Textzle
# An text adventure game thats a puzzle.
# This code if for the structure of the game.
# By splot.dev

class Textzle:
    def __init__(self, name:str, location:str):
        self.areas = {}
        self.beings = {}
        self.items = {}
        self.containers = {}
        
        self.inventory = []
        self.location = location
        self.health = 100
        self.name = name
    def create_area(self, name:str, description:str, properties:dict | None = None, beings:list | None = None, monsters:list | None = None, items:list | None = None, exits:dict | None = None, climbables:dict | None = None, enterables:dict | None = None, containers:list | None = None):
        properties = properties or {}
        beings = beings or []
        monsters = monsters or []
        items = items or []
        exits = exits or {}
        climbables = climbables or {}
        enterables = enterables or {}
        containers = containers or []
        self.areas[name] = {"description": description, "properties": properties, "beings": beings, "monsters": monsters, "items": items, "exits": exits, "climbables": climbables, "enterables": enterables, "containers": containers}
        return ("SUCCESS", True)
    def create_being(self, name:str, description:str, alive:bool, properties:dict | None = None):
        properties = properties or {}
        self.beings[name] = {"description": description, "properties": properties, "alive": alive}
        return ("SUCCESS", True)
    def create_item(self, name:str, description:str, weight:int, properties:dict | None = None):
        properties = properties or {}
        self.items[name] = {"description": description, "weight": weight, "properties": properties}
        return ("SUCCESS", True)
    def create_container(self, name:str, description:str, max_capacity:int, contents:list | None = None, properties:dict | None = None):
        contents = contents or []
        properties = properties or {}
        self.containers[name] = {"description": description, "capacity": 0, "max_capacity": max_capacity, "contents": contents, "properties": properties}
        return ("SUCCESS", True)
    def go(self, place):
        try:
            destination = self.areas[self.location]["exits"][place]
        except KeyError:
            return ("You can't go there!", False)
        if destination not in self.areas:
            return ("This place doesn’t seem to exist.", False)
        self.location = destination
        return ("SUCCESS", True)
    def enter(self, place:str):
        try:
            destination = self.areas[self.location]["enterables"][place]
        except KeyError:
            return ("You can't enter that!", False)
        if destination not in self.areas:
            return ("This place doesn’t seem to exist.", False)
        self.location = destination
        return ("SUCCESS", True)
    def climb(self, place:str):
        try:
            destination = self.areas[self.location]["climbables"][place]
        except KeyError:
            return ("You can't climb that!", False)
        if destination not in self.areas:
            return ("This place doesn’t seem to exist.", False)
        self.location = destination
        return ("SUCCESS", True)
    def take(self, thing:str):
        if thing in self.areas[self.location]["items"]:
            self.inventory.append(thing)
            self.areas[self.location]["items"].remove(thing)
            return ("SUCCESS", True)
        else:
            return ("You can't take that; it doesn't exist in that room yet!", False)
    def drop(self, thing:str):
        if thing in self.inventory:
            self.areas[self.location]["items"].append(thing)
            self.inventory.remove(thing)
            return ("SUCCESS", True)
        else:
            return ("You can't drop that; you don't have it!", False)
    def read(self, thing:str):
        if thing in self.inventory:
            read = self.items[thing]["properties"].get("text")
            if not read:
                return ("You can't read that.", False)
            return ("Text | " + read, True)
        else:
            return ("You can't read that; you don't have it!", False)
    def put_into_container(self, thing:str, container:str):
        try:
            cont = self.containers[container]
        except:
            return ("That container you're trying to use is nonexistent.", False)
        try:
            item = self.items[thing]
        except:
            return ("That item you're trying to use is nonexistent.", False)

        if (self.containers[container]["capacity"] + self.items[thing]["weight"]) > self.containers[container]["max_capacity"]:
            return ("That's too heavy to put in the container.", False)
        
        if thing not in self.inventory:
            return ("That is not in your inventory.", False)
        
        if not (container in self.areas[self.location]["containers"]):
            return ("That container is not in the area!", False)

        self.containers[container]["capacity"] = self.containers[container]["capacity"] + self.items[thing]["weight"]
        self.containers[container]["contents"].append(thing)
        self.inventory.remove(thing)
        return ("SUCCESS", True)
    def take_from_container(self, thing:str, container:str):
        try:
            cont = self.containers[container]
        except:
            return ("That container you're trying to use is nonexistent.", False)
        try:
            item = self.items[thing]
        except:
            return ("That item you're trying to find is nonexistent.", False)
        
        if not (thing in self.containers[container]["contents"]):
            return ("That item is not in the container!", False)
        
        if not (container in self.areas[self.location]["containers"]):
            return ("That container does not exist", False)

        self.inventory.append(thing)
        self.containers[container]["capacity"] = self.containers[container]["capacity"] - self.items[thing]["weight"]
        self.containers[container]["contents"].remove(thing)
        return ("SUCCESS", True)
    def examine_location(self):
        return ("Your Current Location | Description: " + self.areas[self.location]["description"] + " | Obvious things: " + ",".join(self.areas[self.location]["items"]) + ",".join(self.areas[self.location]["containers"]) + ",".join(self.areas[self.location]["climbables"].keys()) + ",".join(self.areas[self.location]["enterables"].keys()) + " | Obvious exits: " + ",".join(self.areas[self.location]["exits"].keys()) + "|", True)
    def examine_item(self, thing:str):
        if thing in self.inventory:
            if thing in self.items:
                return (f"'{thing}' Item | Description: {self.items[thing]['description']} | Weight: {str(self.items[thing]['weight'])} |", True)
            else:
                return ("You cannot examine something that is nonexistent.", False)
        else:
            return ("The item must be in your inventory.", False)
    def examine_being(self, being:str):
        if being in self.areas[self.location]["beings"]:
            if being in self.beings:
                if self.beings[being]["alive"] is True:
                    return (f"'{being}' Being | Description: {self.beings[being]['description']} |", True)
                else:
                    return (f"'{being}' Being | Description: Defeated, no description.|", True)
            else:
                return ("You cannot examine something that is nonexistent.", False)
        else:
            return ("You cannot examine something that is not in the area.", False)
    def examine_container(self, container:str):
        if container in self.areas[self.location]["containers"]:
            if container in self.containers:
                return (f"'{container}' Container | Description: {self.containers[container]['description']} | Max Capacity: {self.containers[container]['max_capacity']} | Current Capacity: {self.containers[container]['capacity']}|", True)
            else:
                return ("You cannot examine something that is nonexistent.", False)
        else:
            return ("You cannot examine something that is not in the area.", False)
    def interact_with_being(self, being:str):
        if not (being in self.areas[self.location]["beings"]):
            return ("That being is not in the area.", False)
        if not (being in self.beings):
            return ("That being does not exist.", False)
        try:
            interact = self.beings[being]["properties"]["interact"]
        except:
            return ("This being can't interact with you!", False)
        
        if self.beings[being]["alive"] is False:
            return ("This being is not alive, so you cannot interact with it.", False)
        return (f"'{being}' Being | {interact}", True)
    def attack_being(self, being:str):
        if not (being in self.areas[self.location]["beings"]):
            return ("That being is not in the area.", False)
        if not (being in self.beings):
            return ("That being does not exist.", False)
        try:
            weakness = self.beings[being]["properties"]["weakness"]
        except:
            return ("This being can't fight with you!", False)
        
        if self.beings[being]["alive"] is False:
            return ("This being is not alive; it cannot fight with you.", False)

        strong = False
        for item in self.inventory:
            if item in weakness:
                strong = True
                break
        try:
            damage = self.beings[being]["properties"]["damage"]
        except:
            if not strong:
                return ("You lost, but are alive.", True)
            else:
                self.beings[being]["alive"] = False
                return ("You defeated the being!", True)
        
        if not strong:
            self.health = self.health - damage
        else:
            self.beings[being]["alive"] = False
            return ("You defeated the being!", True)
        
        return ("You lost some health, because you were defeated.", True)
    def health_amount(self):
        return (f"Health | {self.health} |", True)
    def is_alive(self):
        # special output
        if self.health > 0:
            return True
        else:
            return False
    def change_health(self, amount:int):
        self.health += amount
        return (self.health, True)