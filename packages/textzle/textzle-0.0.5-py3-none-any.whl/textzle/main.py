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
    def create_area(self, name:str, description:str, properties:dict | None = None, beings:list | None = None, monsters:list | None = None, items:list | None = None, exits:dict | None = None, climbables:dict | None = None, enterables:dict | None = None):
        properties = properties or {}
        beings = beings or []
        monsters = monsters or []
        items = items or []
        exits = exits or {}
        climbables = climbables or {}
        enterables = enterables or {}
        self.areas[name] = {"description": description, "properties": properties, "beings": beings, "monsters": monsters, "items": items, "exits": exits, "climbables": climbables, "enterables": enterables}
        return ("SUCCESS", True)
    def create_being(self, name:str, description:str, properties:dict | None = None):
        properties = properties or {}
        self.beings[name] = {"description": description, "properties": properties}
        return ("SUCCESS", True)
    def create_item(self, name:str, description:str, weight:int, properties:dict | None = None):
        properties = properties or {}
        self.items[name] = {"description": description, "weight": weight, "properties": properties}
        return ("SUCCESS", True)
    def create_container(self, name:str, description:str, capacity:int, contents:list | None = None, properties:dict | None = None):
        contents = contents or []
        properties = properties or {}
        self.containers[name] = {"description": description, "capacity": capacity, "contents": contents, "properties": properties}
        return ("SUCCESS", True)
    def go(self, place):
        try:
            destination = self.areas[self.location]["exits"][place]
        except KeyError:
            return ("You can't go there!", False)
        self.location = destination
        return ("SUCCESS", True)
    def enter(self, place:str):
        try:
            destination = self.areas[self.location]["enterables"][place]
        except KeyError:
            return ("You can't enter that!", False)
        self.location = destination
        return ("SUCCESS", True)
    def climb(self, place:str):
        try:
            destination = self.areas[self.location]["climbables"][place]
        except KeyError:
            return ("You can't climb that!", False)
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
            try:
                read = self.items[thing]["properties"]["text"]
            except:
                return ("You can't read that; you might as well try to read a rock!", False)
            return ("Text | " + read, True)
        else:
            return ("You can't read that; you don't have it!", False)
    def put_into_container(self, thing:str, container:str):
        try:
            cont = self.containers[container]
        except:
            return ("That container you're trying to use... is nonexistent.", False)
        try:
            item = self.items[thing]
        except:
            return ("That item you're trying to use... is nonexistent.", False)
        if self.containers[container]["capacity"] < self.items[thing]["weight"]:
            return ("That's too heavy to put in the container. You might as well put a tree in there.", False)
        
        if thing not in self.inventory:
            return ("Why don't you put the moon in there too?", False)

        self.containers[container]["capacity"] = self.containers[container]["capacity"] - self.items[thing]["weight"]
        self.containers[container]["contents"].append(thing)
        self.inventory.remove(thing)
        return ("SUCCESS", True)
    def take_from_container(self, thing:str, container:str):
        try:
            cont = self.containers[container]
        except:
            return ("That container you're trying to use... is nonexistent.", False)
        try:
            item = self.items[thing]
        except:
            return ("That item you're trying to find... is nonexistent.", False)
        
        if not (thing in self.containers[container]["contents"]):
            return ("You know... you can't take an elephant from a purse.", False)

        self.inventory.append(thing)
        self.containers[container]["capacity"] = self.containers[container]["capacity"] + self.items[thing]["weight"]
        self.containers[container]["contents"].remove(thing)
        return ("SUCCESS", True)
    def examine_location(self):
        return ("Your Current Location | Description: " + self.areas[self.location]["description"] + " | Obvious things: " + ",".join(self.areas[self.location]["items"]) + ",".join(self.areas[self.location]["climbables"].keys()) + ",".join(self.areas[self.location]["enterables"].keys()) + " | Obvious exits: " + ",".join(self.areas[self.location]["exits"].keys()) + "|", True)