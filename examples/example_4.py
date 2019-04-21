'''
Reimplementation of Sea Duck Example 4, by Allison Parrish
https://github.com/aparrish/seaduck/blob/master/examples/04_rooms_and_objects.js

'''

import random
from smew import Actor, Event, SmewModel

room_names = ["kitchen", "living room", "study"]
rooms = [Actor(name, "room") for name in room_names]

people_names = ["Max", "Rory"]
people = [Actor(name, "person", {"has_drink": False, "location": None}) 
          for name in people_names]

drinks = [Actor(name, "drink", {"location": None}) 
          for name in ["coffee", "tea"]]


class Take(Event):
    match = ["person", "drink"]
    narrative = ["{a} took the {b}.", 
                 "'Oh hey, {b}!' said {a}, and picked it up."]

    def filter(self, a, b):
        return a.location == b.location and not a.has_drink
    
    def action(self, a, b):
        a.has_drink = True
        self.narrate(a=a, b=b)
        self.model.remove_actor(b)

class Move(Event):
    match = ["person"]

    def filter(self, person):
        return not (person.location == "study" and person.has_drink)
    
    def action(self, a):
        current = self.get_actor(a.location)
        destinations = self.get_related("connects to", current)
        destination = random.choice(destinations)
        a.location = destination.name
        self.narrate(a=a, room=destination)
    
    narrative = ["After a while, {a} went into the {room}.",
                 "{a} decided to go to {room}."]
    
class Talk(Event):
    match = ["person", "person"]

    def filter(self, a, b):
        return a.location == b.location
    
    def action(self, a, b):
        self.narrate(a=a,b=b)
    
    narrative = {
        "origin": ["{a} and {b} chatted for a bit.",
                   "{a} asked {b} how their day was going.",
                   "{b} told {a} about a dream they had last night.",
                   "{a} and {b} talked for a bit about #topics#."
                  ],
        "topics":  ["the weather", "the garden", "the phase of the moon",
                    "{a}'s family", "the books they've been reading"]
    }

class Work(Event):
    match = ["person"]

    def filter(self, a):
        return a.location == "study" and a.has_drink
    
    def action(self, a):
        self.narrate(a=a)
    
    narrative = [
        "{a} typed furiously on their laptop.",
        "{a} was taking notes while reading a book from the library.",
        "{a} sighed as they clicked 'Send' on another e-mail."
    ]

    
class PlayGames(Event):
    match = ["person"]
    
    def filter(self, a):
        return a.location == "living room"
    
    def action(self, a):
        self.narrate(a=a, game=random.choice(self.games))
    
    narrative = [
        "{a} sat down to play {game}# for a while.",
        "{a} decided to get a few minutes of {game}# in.",
        "{a} turned on the video game console. 'Ugh I love {game} so much,' said {a}."
    ]
    
    games = ["Destiny 2", "Splatoon 2", "Skyrim", "Zelda", "Bejeweled"]

actors = people + rooms + drinks
events = [Take, Move, Talk, Work, PlayGames]
model = SmewModel(actors, events)

# Initialize relationships

model.relate(model.actors["kitchen"], "connects to", 
             model.actors["living room"])
model.relate(model.actors["kitchen"], "connects to", 
             model.actors["study"])

model.actors["Max"].location = "living room"
model.actors["Rory"].location = "study"
model.actors["coffee"].location = "kitchen"
model.actors["tea"].location = "kitchen"

model.generate()