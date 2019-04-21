'''
Lady X's Ball

A work in progress about several characters at a vaguely Victorian ball.
They dance, wander around, fall in and out of love, and become jealous.
'''

import random
from smew import Event, Actor, SmewModel

# Events
# -------------------------------------------------------------------
class GetReady(Event):
    match = ["character"]

    narrative = [
        "{name} is getting dressed at home.",
        "{name}'s servants help them into their most elegant outfit for the night.",
        "'Oh {name}, you look wonderful!' their mother exclaims as they prepare to leave."
    ]

    def filter(self, a):
        return a.location=="home"
    
    def action(self, a):
        self.narrate(name=a)

class Arrive(Event):
    match = ["character"]
    narrative = [
        "{name} arrives at the ball.",
        "At last, {name} has arrived.",
        "{name}'s name is called at the top of the stairs, announcing their arrival."
    ]

    def filter(self, a):
        return a.location == "home"
    
    def action(self, a):
        a.location = "main hall"
        self.narrate(name=a)

class Move(Event):
    match = ["character", "room"]
    narrative = [
        "{a} decides to go from the {start} to the {end}.",
        "{a} follows the crowd to the {end}",
        "'I'm going to the {end},', {a} announces."
    ]

    def filter(self, a, b):
        return a.location != "home" and a.location != b.name
    
    def action(self, a, b):
        start = a.location
        a.location = b.name
        self.narrate(a=a, end=b, start=start)

class Notice(Event):
    match = ["character", "character"]
    narrative = [
        "{a} notices {b} across the room.",
        "{b} accidentally brushes against {a}.",
        "{a} turns and sees {b} standing right there."
    ]
    def filter(self, a, b):
        return (a.location != "home" and
                a.location == b.location and
                not self.get_related(a, "loves", b))
    
    def action(self, a, b):
        self.narrate(a=a, b=b)
        event = FallInLove(self.model, a, b)
        event.run()

class FallInLove(Event):
    match = ["character", "character"]

    narrative = [
        "{a} is smitten with {b}.",
        "At the sight of {b}, {a}'s heart suddenly beats faster.",
        "Suddenly, {a} realizes just how beautiful {b} looks tonight.",
        "{a} can't help but notice {b}'s sparking wit."
    ]

    def filter(self, a, b):
        return False # Can only be directly called from another event.
    
    def action(self, a, b):
        self.narrate(a=a, b=b)
        a_loves = self.get_related(a, "loves")
        if len(a_loves) > 0:
            for crush in a_loves:
                self.narrate(_text=f"All thoughts of {crush} are driven from {a}'s mind.")
                self.unrelate(a, "loves", crush, False)
        self.relate(a, "loves", b, False)

class DanceWithNPC(Event):
    match = ["character"]
    narrative = [
        "'May I have the next dance?' {name} is asked by a {partner}.",
        "A {partner} politely invites {name} to dance.",
        "A {partner} cuts in, insisting on a dance with {name}."
    ]

    def filter(self, a):
        return a.location=="main hall"

    def action(self, a):
        adjective = random.choice(["old", "young", "elegant", "handsome", "striking"])
        noun = random.choice(["debutante", "cavalry offier", "knight", "duchess", "matron"])
        self.narrate(name=a, partner=f"{adjective} {noun}")

class AskToDance(Event):
    match = ["character", "character"]
    asks = [
        "{a} works up the courage and asks {b} for a dance.",
        "'May I have the next dance?' {a} asks {b}.",
    ]

    rejections = [
        "'Perhaps later,' {b} answers coldly."
    ]

    dances = [
        "{a} takes {b}'s hand. As the music plays, they whirl across the floor.",
        "{a} and {b} step onto the floor and dance together."
    ]

    def filter(self, a, b):
        return (self.get_related(a, "loves", b) and
                a.location == "main hall" and a.location == b.location)
    
    def action(self, a, b):
        ask_text = random.choice(self.asks)
        self.narrate(_text=ask_text.format(a=a, b=b))
        if self.get_related(b, "hates", a):
            # B rejects A outright
            reject_text = random.choice(self.rejections)
            self.narrate(_text=reject_text.format(a=a, b=b))
            return
        elif self.get_related(b, "loves", a):
            # B is also in love with A
            self.narrate(_text="'It would be my pleasure,' {b}'s heart beats faster."
                               .format(b=b))
        dance_text = random.choice(self.dances).format(a=a, b=b)
        self.narrate(_text=dance_text)
        if not self.get_related(b, "loves", a) and  random.random() < 0.5:
            event = FallInLove(self.model, b, a)
            event.run()

class TalkQuietly(Event):
    match = ["character", "character"]
    narrative = [
        "{a} sits by {b}, and they talk quiety.",
        "{a} engages {b} in conversation.",
        "{a} and {b} converse on a setee in the salon."
    ]

    def filter(self, a, b):
        return (a.location == "salon" and b.location == "salon")
    
    def action(self, a, b):
        self.narrate(a=a, b=b)
        a_loves = self.get_related(a, "loves")
        if len(a_loves) > 0 and random.random() < 0.5:
            crush = random.choice(a_loves)
            adjective = random.choice(["beauty", "wit", "charm", "elegance"])
            _text = f"{a} can't help but mention {crush}'s {adjective}."
            self.narrate(_text=_text)
            if (self.get_related(b, "loves", crush) and 
                    not self.get_related(crush, "loves", "b")):
                self.narrate(_text=f"{b}'s eyes narrow with jealousy.'")
                self.relate(b, "hates", a, False)

## Set up characters
#names = ["Arabella", "Brenden", "Caroline", "De Viers", "Emilia", 
#         "Fitzroy", "Ginny", "Hayes", "Isabelle", "John"]
names = ["Arabella", "Brenden", "Caroline"]
actors = [Actor(name, "character", {"location": "home"}) for name in names]

# Set up rooms
room_names = ["main hall", "salon", "gardens"]
rooms = [Actor(name, "room") for name in room_names]
actors += rooms

#events = [Arrive, FallInLove, DanceWithNPC]
events = Event.__subclasses__()
model = SmewModel(actors, events)

for _ in range(50):
    model.advance()


        


