

class Take(Event):
    def filter(self, a, b):
        return ("person" in a.tags and "drink" in b.tags 
                and a.location == b.location and not a.has_drink)
    
    def action(self, a, b):
        self.remove(b)
        a.has_drink = True
        self.narrate(a, b)
    
    narrative = ["{a} took the {b}.", 
                 "'Oh hey, {b}!' said {a}, and picked it up."]

class Move(Event):
    match = ["person"]

    def filter(self, a):
        return not (person.location == "study" and person.has_drink)
    
    def action(self, a):
        current = self.actors[a.location]
        destinations = self.get_related("connects to", current)
        destination = random.choice(destinations)
        this.location = destination.name
        self.narrate(a=a, room=destination)
    
    narrative = ["After a while, {a} went into the {room}.",
                "{a} decided to go to {room}."]


    
