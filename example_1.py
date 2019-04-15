from smew import Event, Actor, SmewModel

chris = Actor("Chris", "person", {"sleepiness": 0})
bed = Actor("king-sized bed", "bed", {"occupied": False})

class MoreSleepy(Event):
    
    narrative = [
        "{name} yawns.",
        "{name}'s eyelids droop.",
        "{name} says 'I could use a coffee.'"
    ]
    
    def filter(self, a):
        return "person" in a.tags and a.sleepiness < 10
    
    def action(self, a):
        a.sleepiness += 1
        self.narrate(name=a)

class ReallySleepy(Event):
    narrative = ["{name} is very sleepy."]
    
    def filter(self, a):
        return "person" in a.tags and a.sleepiness >= 7
    
    def action(self, a):
        self.narrate(name=a)

class GetInBed(Event):
    narrative = ["{name} gets into {bed}."]
    
    def filter(self, a, b):
        return ("person" in a.tags and "bed" in b.tags and
                not b.occupied and a.sleepiness > 7)
    
    def action(self, a, b):
        b.occupied = True
        self.narrate(name=a, bed=b)

class FallAsleep(Event):
    narrative = ["{name} falls asleep."]
    
    def filter(self, a, b):
        return "person" in a.tags and "bed" in b.tags and b.occupied
    
    def action(self, a, b):
        self.narrate(name=a)
        self.end()

model = SmewModel([chris, bed], 
                  [MoreSleepy, ReallySleepy, GetInBed, FallAsleep])
while not model.ended:
    model.advance()
