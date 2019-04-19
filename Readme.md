# Smew

Smew is a Python framework with a focus on event-driven generative narrative. Smew lets you define `Actors`, and `Events` which can happen to those actors and generate some text associated with them. Smew is heavily inspired by [Sea Duck](https://github.com/aparrish/seaduck) by [Allison Parrish](https://www.decontextualize.com/) (A [smew](https://en.wikipedia.org/wiki/Smew) is a kind of sea duck).

## Basic Example

Here's a Hello World model with Smew:

```python
from smew import Event, Actor, SmewModel

narrator = Actor("Narrator", "character", {"has_talked": False})

class HelloWorld(Event):
    match = ["character"]
    narrative = [
        "'Hello world!' says {a}",
        "{a} says 'Hello world!'"
    ]
    def filter(self, actor):
        return not actor.has_talked
    
    def action(self, actor):
        self.narrate(a=actor)
        actor.has_talked = True

model = SmewModel([narrator], [HelloWorld])
model.generate()
```

If you run this, you'll see either `'Hello world!' says Narrator`, or `Narrator says 'Hello world!'`.  

## Overview

As you can see in the example above, a Smew model consists of `Actor`s and `Event`s, which are passed to a `SmewModel` object. Actors are the entities in the model; they have `tags` that define what kind of entities they are, and `properties` that define model-specific qualities they have (that may change over the course of a model). Events describe, well, events that can involve those characters. Events also have text templates that define text that can be generated when the event occurs. The model holds the actors and events. Every round of the model, it finds all possible valid combinations of events and actors that may occur, and chooses one of them that actually happens. A model can also store `relations` between actors.

### Actors 

An Actor is an entity in a narrative. It can be a person (or group of people), an object, a room, or anything else. Actors are defined by a `name`, `tags`, and `properties`. 
    * Names are unique identifiers, and are also how the actor will be rendered in text. 
    * Tags are a string or list of strings; they help determine what events the actor can be involved in.
    * Properties are any variables that may change over the course of a model run. They are passed to 
Technically, both 

Actors are defined using `smew.Actor`, as in the example above. 

We can change the example above to include multiple actors; then each one will have a chance to greet us with "Hello world."

```python
# Adding to the example above
names = ["Kim", "Taylor"]
actors = [Actor(name, "person", {"has_talked": False}) for name in names]
model = SmewModel(actors, [HelloWorld])
model.generate()
```

### Events

Events are the heart of the framework. Events are defined as classes (a specific event object is an event associated with one or more specific actors). At a minimun, a `smew.Event` class must implement two methods: `filter`, and `action`. Both take one or more arguments, one for each actor that may be involved in the event. `filter` should returns `True` if a particular set of actors are valid for the event, and otherwise `False`. `action` takes the same arguments, and can be as complicated as you want; this is where the actors are changed, and narration happens.

An `Event` class will generally have two class variables: `match` and `narrative`. 

    * `match` is a list of tags, one for every actor involved in the event. (There must be the same number of tags as arguments to `filter` and `action`)
    * `narrative` is a list of string templates in [keyword argument](https://docs.python.org/3.6/library/string.html#formatstrings) format.

The model determines possible events in two steps. First, for all events in the model, it finds all possible combinations of actors with the tags specified in `match` (if no `match` is specified, it checks all possible combinations of actors). Then, it runs the event's `filter` method over each combination; if the filter returns `True`, it is a valid event. Finally, it randomly chooses one valid event with actors to run. 

Looking at the example above:

```python
class HelloWorld(Event):
    match = ["character"]
    narrative = [
        "'Hello world!' says {a}",
        "{a} says 'Hello world!'"
    ]
    def filter(self, actor):
        return not actor.has_talked
    
    def action(self, actor):
        self.narrate(a=actor)
        actor.has_talked = True
```

`match = ["character']` means that the event `HelloWorld` will be tested against all actors with the tag `"character"`. Then the `filter` method will checker whether those actors' `has_talked` property is `False` -- this will ensure that actors can only speak once. Finally, `action` will update the `has_talked` property of the chosen actor, and generate the resulting narration.

Here's an example of an event involving two characters, where one is greeting the other.

```python
class SayHello(Event):
    match = ["character", "character"]
    narrative = [
        "'Hi {b},' says {a}",
        "{a} says: 'Hello, {b}!'",
        "{a} greets {b}"
    ]
    def filter(self, a, b):
        return not self.get_related(a, "greeted", b)
    
    def action(self, a, b):
        self.narrate(a=a, b=b)
        self.relate(a, "greeted", b, reciprocal=False)

names = ["Alan", "Beth", "Carlos"]
actors = [Actor(name, "character") for name in names]
model = SmewModel(actors, [SayHello])
model.generate()
```

This will run until each actor has greeted each other actor. A sample output might be:

```
'Hi Carlos,' says Alan
Beth says: 'Hello, Carlos!'
Beth greets Alan
Carlos greets Beth
Carlos greets Alan
Alan says: 'Hello, Beth!'
```

This example also demonstrates relationships, which will be explained in more detail shortly. Notice that the `Event` class comes with methods for checking and updating relationships. These are just pass-throughs to methods of the same name that live in the parent `SmewModel` object; in fact, the entire model is accessible through the event's `model` property, i.e. `self.model`.

#### Narration

Narration is done through the event's `narrate` method. By default, `narrate` chooses one of the strings in the event's `narrative` property, and formats it using the [keywork formatting style](https://docs.python.org/3.6/library/string.html#formatstrings). This means that you need to explicitly name the variables you're passing to `narrate` to correspond with the strings in `narrative`. In the example above, `self.narrate(a=a, b=b)` works, but `self.narrate(a, b)` would not. By default, actors are rendered as their names; the keyword format allows you to explicity access properties within the curly braces. For example, if you have an actor that looks like `Actor("Neil", ["astronaut"], {"location": "the moon"})`, you could write a narrative string with the form `"{a} is at {a.location}"`.

You can also override the default narration behavior by passing the argument `_text` to narrate any arbitrary string, i.e. `self.narrate(_text="Render this string, no matter what self.narrative says")`. 

**TODO:**

    * At the moment, narration is just printed to the screen. It would be nice to track it internally too.
    * In Sea Duck, narration is done using Tracery grammar; that could be handy here too.


### Relationships

As mentioned above, Smew also lets you track relationships between actors. Relationships take the form of triples `(Actor, relationship, Actor)`, where the relationships themselves are just strings. You can add relationships with the `relate(a, relationship, b, reciprocal=True)` method (either on the model or the event). If `reciprocal=True` (the default), *two* relationships are added: `(a, relationship, b)` and `(b, relationship, a)`. If `reciprocal=False`, only the exact relationship is created. You can end a relationship with `unrelate` with the same arguments (again, if `reciprocal=False` it will only end the relationship in one direction). Actors can have any number of relationships, so if at some point you run `relate(a, "loves", b)` and later run `relate(a, "hates", b)` (for the same `a` and `b`), the latter does not overwrite the former; now `a` and `b` both `"love"` and `"hate"` each other.

You can access relationships using the `get_related` method. You can use it in three different ways:

    * `get_related(a, "loves")` will return a list of all the actors that actor `a` loves, i.e. any actors matching `(a, "loves", *)`.
    * `get_related("loves", a)` will return a list of all actors that love `a`, i.e. `(*, "loves", a)`.
    * `get_related(a, "loves", b)` will return `True` if the relationship `(a, "loves", b)` exists, and `False` otherwise.





