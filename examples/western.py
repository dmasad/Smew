# Western Domain
# Implementing the western domain from Ware, 2014

import random
from smew import Event, Actor, SmewModel


class Die(Event):
    match = ["person"]

    def filter(self, person):
        return person.sick == True
    
    def action(self, person):
        self.narrate(person=person)
        self.model.remove_actor(person, remove_relationships=False)
    
    narrative = ["{person} dies."]

class Steal(Event):
    match = ["person", "item", "sheriff"]

    def filter(self, person, item, sheriff):
        return not self.get_related(person, "has", item)
    
    def action(self, person, item, sheriff):
        owner = self.get_related("has", item)[0]
        self.unrelate(owner, "has", item)
        self.relate(person, "has", item)
        self.relate(sheriff, "after", person, False)
        self.relate(owner, "after", person, False)
        self.narrate(person=person, item=item, owner=owner)
    
    narrative = ["{person} steals {item} from {owner}."]

class Shoot(Event):
    match = ["person", "person"]

    def filter(self, shooter, target):
        return self.get_related(shooter, "after", target)
    
    def action(self, shooter, target):
        self.narrate(_origin="shoots", shooter=shooter, target=target)
        if random.random() < 0.5:
            self.narrate(_origin="hit", target=target)
            target.sick = True
        else:
            self.narrate(_origin="miss", shooter=shooter, target=target)
            self.relate(target, "after", shooter)
    
    narrative = {
        "shoots": ["{shooter} shoots {target}!"],
        "hit": ["{target} is hit!"],
        "miss": ["{shooter} misses!", "The shot goes wide!"]
    }

class Heal(Event):
    match = ["person", "person", "medicine"]

    def filter(self, healer, victim, medicine):
        return victim.sick and self.get_related(healer, "has", medicine)
    
    def action(self, healer, victim, medicine):
        self.narrate(healer=healer, victim=victim)
        self.model.remove_actor(medicine)
        victim.sick = False
    
    narrative = ["{healer} heals {victim}."]


# Set up scene
timmy = Actor("Timmy", "person", {"sick": True})
hank = Actor("Hank", "person", {"sick": False})
carl = Actor("Carl", "person", {"sick": False})
william = Actor("William", ["person", "sheriff"], {"sick": False})
medicine = Actor("medicine", ["item", "medicine"])

actors = [timmy, hank, carl, william, medicine]
model = SmewModel(actors, Event.__subclasses__())
model.relate(carl, "has", medicine)

if __name__ == "__main__":
    model.generate()

    

