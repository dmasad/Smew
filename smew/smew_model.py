from abc import ABC, abstractmethod
import random
from itertools import permutations, product

class Event(ABC):
    ''' Abstract base for an event which can occur during a model run.

    Events have two key methods: `filter`, and `action`. `filter` determines
    whether an event can be applied to a given set of actors; `action` detemines
    what happens when the event is activated with that set of actors.
    '''
    
    match = None 
    narrative = [""]
        
    def __init__(self, model, *args):
        ''' Create a new (potential) event.

        Args:
            model: The SmewModel object the event is tied to.
            *args: One or more Actors involved in the event.
        '''
        self.model = model
        self._actors = args

    def __repr__(self):
        return f"{self.__class__.__name__}{tuple(self._actors)}"
    
    @abstractmethod
    def filter(self, *args):
        ''' 
        Check whether this event is applicable to the given Actors
        
        Args:
            *args: One or more Actors to check.
        
        Returns:
            Must return either True or False
        '''
        pass
    
    @abstractmethod
    def action(self, *args):
        ''' Update the Actors and add to the narration.
        
        Args:
            *args: One or more Actors; assumed to be the same actors that were
                   checked with filter.
        '''
        pass
    
    def run(self):
        ''' Execute the event with the actors passed to it.
        '''
        self.action(*self._actors)
    
    def narrate(self, **kwargs):
        ''' Add narration text describing the event.

        By default, choose one of the elements in the `narrative` list, and
        format using the dictionary provided.

        Args:
            **kwargs: A dictionary of variable names to use to format the
            string.  If "_text" is in the dictionary, its value is used verbatim
            instead.
        '''
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
        """
        Get an actor with a given name in the parent model.

        Args:
            name: The name of an actor to get.
        
        Returns:
            The Actor object in the model with that name.
        """
        return self.model.actors[name]
    
    def get_event(self, name):
        '''
        Get an Event class with the given name.
        '''
        return self.model.events[name]
    
    def get_related(self, a, b, c=None):
        '''
        Get actors related by a relationship.
        (calls `self.model.get_related`)

        Args:
            a, b, c=None: either Actor objects or relationship strings

        Returns:
            If `a` is a relationship and `b` is an actor, return a list
            of all actors that match (Actor, a, b)
            
            If `a` is an actor and `b` is a relationship, return a list
            of all actors that match (a, b, Actor)

            if `a` and `c` are actors, and `b` is a relationship, checks whether
            that relationship is present.
        '''
        return self.model.get_related(a, b, c)
    
    def relate(self, a, relation, b, reciprocal=True):
        '''
        Create a relationship between two actors.
        (calls `self.model.relate`)

        args:
            a, b: Actor objects to relate
            relation: a string describing the relationship
            reciprocal: if True, create two relationships, one
                        (a, relationship, b) and the other (b, relationship, a)
        '''
        self.model.relate(a, relation, b, reciprocal)
    
    def unrelate(self, a, relation, b, reciprocal=True):
        '''
        Removes a relationship between two actors.
        (calls `self.model.unrelate`)

        args:
            a, b: Actor objects to unrelate
            relation: the relationship string
            reciprocal: if True, removes the relationship in both directions
        '''
        self.model.unrelate(a, relation, b, reciprocal)
    
    def end(self):
        '''
        End the model run.
        '''
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
    ''' A generative model that consists of Actors and Events.
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
        self.relationships = []
        self.ended = False
    
    def add_actor(self, actor):
        '''
        Insert a new actor into the model.
        '''

        if actor.name in self.actors:
            raise SmewException(f"An actor named {actor} is already in the model.")
        self.all_actors.append(actor)
        self.actors[actor.name] = actor
    
    def remove_actor(self, actor, remove_relationships=True):
        '''
        Remove an actor from the model.

        args:
            actor: The Actor object to remove
            remove_relationships: if True, remove any relationship involving
                                  the actor as well
        '''
        self.all_actors.remove(actor)
        del self.actors[actor.name]
        
        if remove_relationships:
            to_delete = []
            for rel in self.relationships:
                if rel[0] == actor.name or rel[2] == actor.name:
                    to_delete.append(rel)
            for rel in to_delete:
                self.relationships.remove(rel)

    
    def add_event(self, event):
        '''
        Insert a new Event into the model.
        '''
        if event.__name__ in self.events:
            raise SmewException(f"An event named {event.__name__} is already in the model.")
        self.all_events.append(event)
        self.events[event.__name__] = event
    
    def relate(self, a, relation, b, reciprocal=True):
        '''
        Create a relationship between two actors.

        args:
            a, b: Actor objects to relate
            relation: a string describing the relationship
            reciprocal: if True, create two relationships, one
                        (a, relationship, b) and the other (b, relationship, a)
        '''
        relation_tuple = (a.name, relation, b.name)
        if relation_tuple not in self.relationships:
            self.relationships.append(relation_tuple)
        if reciprocal:
            self.relate(b, relation, a, False)
    
    def unrelate(self, a, relation, b, reciprocal=True):
        '''
        Removes a relationship between two actors.

        args:
            a, b: Actor objects to unrelate
            relation: the relationship string
            reciprocal: if True, removes the relationship in both directions
        '''
        relation_tuple = (a.name, relation, b.name)
        self.relationships.remove(relation_tuple)
        if reciprocal:
            self.unrelate(b, relation, a, False)
    
    def get_related(self, a, b, c=None):
        '''
        Get actors related by a relationship.

        Args:
            a, b, c=None: either Actor objects or relationship strings

        Returns:
            If `a` is a relationship and `b` is an actor, return a list
            of all actors that match (Actor, a, b)
            
            If `a` is an actor and `b` is a relationship, return a list
            of all actors that match (a, b, Actor)

            if `a` and `c` are actors, and `b` is a relationship, checks whether
            that relationship is present.
        '''
        related = []
        if isinstance(a, Actor) and isinstance(c, Actor):
            related = ((a.name, b, c.name) in self.relationships)
        elif type(a) is str and isinstance(b, Actor):
            for triple in self.relationships:
                if triple[1] == a and triple[2] == b.name:
                    related.append(self.actors[triple[0]])
        elif isinstance(a, Actor) and type(b) is str:
            for triple in self.relationships:
                if triple[0] == a.name and triple[1] == b:
                    related.append(self.actors[triple[2]])
        return related
    
    def get_tagged(self, tag):
        '''
        Return a list of all actors with the given tag.
        '''
        return [actor for actor in self.all_actors if actor.has_tag(tag)]
    
    def get_matching(self, AnEvent):
        '''
        Get all potential sets of actors to run the event filter against.
        '''
        if AnEvent.match:
            tagged_actors = [self.get_tagged(tag) for tag in AnEvent.match]
            return [actors for actors in product(*tagged_actors) 
                    if len(set(actors))==len(actors)]
            #return 
        else:
            return permutations(self.all_actors, AnEvent.n_actors())
    
    def get_possible_events(self):
        ''' Find the list of all valid instantiated events that can happen next.
        '''
        possible_events = []
        for AnEvent in self.all_events:

            for actors in self.get_matching(AnEvent):
                event = AnEvent(self, *actors)
                if event.filter(*actors):
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
    
    def generate(self, max_steps=100):
        '''
        Run the model until it ends (or to the maximum number of steps)
        '''
        steps = 0
        while not self.ended and steps < max_steps:
            self.advance()
            steps += 1
    
class SmewException(Exception):
    pass