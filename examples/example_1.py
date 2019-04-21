'''
Reimplementation of Sea Duck example 1, by Allison Parrish
https://github.com/aparrish/seaduck/blob/master/examples/01_basic.js
'''


from smew import Event, Actor, SmewModel

chris = Actor("Chris", "person", {"sleepiness": 0})
bed = Actor("king-sized bed", "bed", {"occupied": False})

class MoreSleepy(Event):
    match = ["person"]
    narrative = [
        "#name# yawns.",
        "#name#'s eyelids droop.",
        "#name# says 'I could use a coffee.'"
    ]
    
    def filter(self, a):
        return a.sleepiness < 10
    
    def action(self, a):
        a.sleepiness += 1
        self.narrate(name=a)

class ReallySleepy(Event):
    match = ["person"]
    narrative = ["#name# is very sleepy."]
    
    def filter(self, a):
        return a.sleepiness >= 7
    
    def action(self, a):
        self.narrate(name=a)

class GetInBed(Event):
    narrative = ["#name# gets into #bed#."]
    
    def filter(self, a, b):
        return (a.has_tag("person") and "bed" in b.tags and
                not b.occupied and a.sleepiness > 7)
    
    def action(self, a, b):
        b.occupied = True
        self.narrate(name=a, bed=b)

class FallAsleep(Event):
    narrative = ["#name# falls asleep."]
    
    def filter(self, a, b):
        return a.has_tag("person") and "bed" in b.tags and b.occupied
    
    def action(self, a, b):
        self.narrate(name=a)
        self.end()

model = SmewModel([chris, bed], 
                  [MoreSleepy, ReallySleepy, GetInBed, FallAsleep])
model.generate()