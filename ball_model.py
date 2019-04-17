'''
Lady X's Ball

There are N characters, all attending a high-society ball. They walk around, 
dance, fall in and out of love, get jealous, and fight.

Locations: 
Main hall, salon, gardens

'''
import random
from smew import Event, Actor, SmewModel

# Events
# -------------------------------------------------------------------
class GetReady(Event):
    narrative = [
        "{name} is getting dressed at home.",
        "{name}'s servants help them into their most elegant outfit for the night.",
        "'Oh {name}, you look wonderful!' their mother exclaims as they prepare to leave."
    ]

    def filter(self, a):
        return a.has_tag("character") and a.location=="home"
    
    def action(self, a):
        self.narrate(name=a)

class Arrive(Event):
    narrative = [
        "{name} arrives at the ball.",
        "At last, {name} has arrived.",
        "{name}'s name is called at the top of the stairs, announcing their arrival."
    ]

    def filter(self, a):
        return a.has_tag("character") and a.location == "home"
    
    def action(self, a):
        a.location = "main hall"
        self.narrate(name=a)
    
class FallInLove(Event):
    narrative = [
        "{a} notices {b} across the room, and is immediately smitten.",
        "At the sight of {b}, {a}'s heart suddenly beats faster.",
        "Suddenly, {a} realizes just how beautiful {b} looks tonight."
    ]

    def filter(self, a, b):
        return (a.has_tag("character") and b.has_tag("character") and
                a.location == b.location and a.location != "home" and
                not self.get_related(a, "loves", b))
    
    def action(self, a, b):
        self.narrate(a=a, b=b)
        a_loves = self.get_related(a, "loves")
        if len(a_loves) > 0:
            for crush in a_loves:
                self.narrate(_text=f"All thoughts of {crush} are driven from {a}'s mind.")
                self.unrelate(a, "loves", crush, False)
        self.relate(a, "loves", b, False)

class DanceWithNPC(Event):
    narrative = [
        "'May I have the next dance?' {name} is asked by a {partner}.",
        "A {partner} politely invites {name} to dance.",
        "A {partner} cuts in, insisting on a dance with {name}."
    ]

    def filter(self, a):
        return (a.has_tag("character") and a.location=="main hall")

    def action(self, a):
        adjective = random.choice(["old", "young", "elegant", "handsome", "striking"])
        noun = random.choice(["debutante", "cavalry offier", "knight", "duchess", "matron"])
        self.narrate(name=a, partner=f"{adjective} {noun}")

#class AskToDance(Event):
#    narrative = [
#        "{a} works up the courage and asks {b} for a dance.",
#        "'May I have the next dance?' {a} asks {b}.",
#    ]


## Set up characters
#names = ["Arabella", "Brenden", "Caroline", "De Viers", "Emilia", 
#         "Fitzroy", "Ginny", "Hayes", "Isabelle", "John"]
names = ["Arabella", "Brenden", "Caroline"]
actors = [Actor(name, "character", {"location": "home"}) for name in names]
#events = [Arrive, FallInLove, DanceWithNPC]
events = Event.__subclasses__()

model = SmewModel(actors, events)
for _ in range(50):
    model.advance()


        


