from abc import ABC, abstractmethod
import random
from itertools import permutations

class Event(ABC):
    ''' Abstract base for an event which can occur during a model run.

    Events have two key methods: `filter`, and `action`. `filter` determines
    whether an event can be applied to a given set of actors; `action` detemines
    what happens when the event is activated with that set of actors.
    '''
    
    match = [] # TODO: implement tag-wise matching
    narrative = [""]
    
    def __new__(cls, *args):
        """Create a new event only if its filter passes.
        This prevents invalid event objects from being created.
        """
        event = object.__new__(cls)
        event.model = args[0]
        # Check filter
        if event.filter(*args[1:]):
            return event
        else:
            return False
        
    def __init__(self, model, *args):
        self.model = model
        self._actors = args
        self.actors = model.actors # Pass-through to parent
    
    @abstractmethod
    def filter(self, *args):
        pass
    
    @abstractmethod
    def action(self, *args):
        pass
    
    def run(self):
        self.action(*self._actors)
    
    def narrate(self, **kwargs):
        # TODO: better logging
        if "_text" in kwargs:
            print(kwargs["_text"])
        else:
            text = random.choice(self.narrative)
            print(text.format(**kwargs))
    
    @classmethod
    def n_actors(cls):
        return cls.action.__code__.co_argcount-1
    
    # Pass-throughs to parent model
    # ----------------------------------
    def get_actor(self, name):
        return self.model.actors[name]
    
    def get_related(self, a, b, c=None):
        # TODO Fill this in
        return self.model.get_related(a, b, c)
    
    def relate(self, a, relation, b, reciprocal=True):
        self.model.relate(a, relation, b, reciprocal)
    
    def unrelate(self, a, relation, b, reciprocal=True):
        self.model.unrelate(a, relation, b, reciprocal)
    
    def end(self):
        self.model.ended = True


class Actor:
    ''' One actor or other entity in the narrative.
    '''
    def __init__(self, name, tags, properties=None):
        self.name = name
        if isinstance(tags, list):
            self.tags = tags
        else:
            self.tags = [tags]
        self.properties = {}
        if properties is not None:
            self.properties = list(properties.keys())
            for key, val in properties.items():
                setattr(self, key, val)
    
    def has_tag(self, tag):
        return tag in self.tags
    
    def __getattr__(self, name):
            return None
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Actor({self.name}, {self.tags})"

class SmewModel:
    ''' A Smew is a kind of seaduck.
    '''
    
    def __init__(self, actors=None, events=None):
        if not actors:
            actors = []
        self.all_actors = actors
        self.actors = {actor.name: actor for actor in self.all_actors}
        
        if not events:
            events = []
        self.all_events = events
        self.events = {event.__name__: event for event in self.all_events}
        self.relationships = [] # List of triples
        self.ended = False
    
    def add_actor(self, actor):
        if actor.name in self.actors:
            raise SmewException(f"An actor named {actor} is already in the model.")
        self.all_actors.append(actor)
        self.actors[actor.name] = actor
    
    def remove_actor(self, actor):
        self.all_actors.remove(actor)
        del self.actors[actor.name]
    
    def add_event(self, event):
        if event.__name__ in self.events:
            raise SmewException(f"An event named {event.__name__} is already in the model.")
        self.all_events.append(event)
        self.events[event.__name__] = event
    
    def relate(self, a, relation, b, reciprocal=True):
        relation_tuple = (a.name, relation, b.name)
        self.relationships.append(relation_tuple)
        if reciprocal:
            self.relate(b, relation, a, False)
    
    def unrelate(self, a, relation, b, reciprocal=True):
        relation_tuple = (a.name, relation, b.name)
        self.relationships.remove(relation_tuple)
        if reciprocal:
            self.unrelate(b, relation, a, False)
    
    def get_related(self, a, b, c=None):
        ''' Get actors related by a relationship.
        
        Args:
            If `a` is a relationship and `b` is an actor, return a list
            of all actors that match (Actor, a, b)
            
            If `a` is an actor and `b` is a relationship, return a list
            of all actors that match (a, b, Actor)

            if `a` and `c` are actors, and `b` is a relationship, checks whether
            that relationship is present.
        '''
        related = []
        if type(a) is str and isinstance(b, Actor):
            for triple in self.relationships:
                if triple[1] == a and triple[2] == b.name:
                    related.append(self.actors[triple[0]])
        elif isinstance(a, Actor) and type(b) is str:
            for triple in self.relationships:
                if triple[0] == a.name and triple[2] == b:
                    related.append(self.actors[triple[2]])
        elif isinstance(a, Actor) and isinstance(c, Actor):
            related = ((a.name, b, c.name) in self.relationships)
        return related
            
    
    def get_possible_events(self):
        possible_events = []
        for Event in self.all_events:
            for actors in permutations(self.all_actors, Event.n_actors()):
                event = Event(self, *actors)
                if event:
                    possible_events.append(event)
        return possible_events
    
    def advance(self):
        if self.ended: return
        possible_events = self.get_possible_events()
        if len(possible_events) == 0:
            self.ended = True
            return
        event = random.choice(possible_events)
        event.run()
    
class SmewException(Exception):
    pass