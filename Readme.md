# Smew

Smew is a Python framework with a focus on event-driven generative narrative. Smew lets you define `Actors`, and `Events` which can happen to those actors and generate some text associated with them. It is heavily inspired by [Sea Duck](https://github.com/aparrish/seaduck) by [Allison Parrish](https://www.decontextualize.com/) (A [smew](https://en.wikipedia.org/wiki/Smew) is a kind of sea duck).

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

You can see more examples in the `examples/` folder.

## Installation

Smew is very much a work in progress and under sporadic development, so installing it in `develop` mode is highly recommended (that means that the source code is kept at its current location, so edits you make there are immediately available next time you `import` it).

Download or clone this repository, open it in your terminal, and run

```
python setup.py develop
```

Smew's Tracery rendering relies on [Tracery for Python](https://github.com/aparrish/pytracery), also by Allison Parrish.

Smew was developed with Python 3.6, and probably requires Python 3.5 or above. 

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

* `narrative` is a list or dictionary of string templates, and can mix [keyword arguments](https://docs.python.org/3.6/library/string.html#formatstrings) and [Tracery](http://www.crystalcodepalace.com/traceryTut.html) formats.

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

Narration is done through the event's `narrate` method. By default, `narrate` chooses one of the strings in the event's `narrative` property, and formats it in two passes: first by parsing any Tracery symbols it has, then using the [keywork formatting style](https://docs.python.org/3.6/library/string.html#formatstrings). This means that you need to explicitly name the variables you're passing to `narrate` to correspond with the strings in `narrative`. In the example above, `self.narrate(a=a, b=b)` works, but `self.narrate(a, b)` would not. By default, actors are rendered as their names; the keyword format allows you to explicity access properties within the curly braces. For example, if you have an actor that looks like `Actor("Neil", ["astronaut"], {"location": "the moon"})`, you could write a narrative string with the form `"{a} is at {a.location}"`.

You can write narrative templates in a mix of Tracery and Python curly-braces. For example, the strings `"'Hello {a},' said {b}"`, `"'Hello #a#,' said #b#"` and `"'Hello #a#,' said {b}"` are equally valid, and would all render the same way when called with `self.narrate(a=a, b=b)`. 

Tracery grammar lets you expand symbols (anything between `#` signs) recursively. For example, if you wanted two characters to talk about a random topic, you could write the event's narrative as:

```python
narrative = {"origin": ["#a# talked to #b# about #topic#."],
             "topic": ["the weather", "the moon", "#a#'s family", "the game #game#"],
             "game": ["YAWP", "Gutter", "Ruin Value"]
            }
```

Then the symbol `#topic#` would get expanded into one of the strings associated with the key `"topic"` in the narrative dictionary; if the last string is chosen, the symbol `#game#` will be expanded into one of the options associated with `"game"`, and so forth. See the [Tracery documentation](http://tracery.io/) for more details. 

Note that if `narrative` is a dictionary, the default starting point for Tracery rendering is the key `"origin"`. (If `narrative` is a list, it is implicitly assigned to `origin`). You can also override that starting point using the `_origin` argument. For example, 

```python
# In an Event definition
narrative = {"happy": 
                     ["{a} was happy to see {b}", 
                     "'I'm so happy to see you, {b}!' said {a}"],
            "not_happy": "'Oh, it's you, {b},' said {a}"
            }

def action(self, a, b):
    if self.related(a, "likes", b):
        self.narrate(_origin="happy", a=a, b=b)
    else:
        self.narrate(_origin="not_happy", a=a, b=b)

```

Finally, you can also override the default narration behavior by passing the argument `_text` to narrate any arbitrary string, i.e. `self.narrate(_text="Render this string, no matter what self.narrative says")`. 

#### Advanced note

Each time the `narrate` method is called, Smew builds a new Tracery grammar object for that method run alone. It combines any grammar in the parent model's `grammar` property (which lets you define symbols you may want to use across events); the specific event class's grammar in the `narrative` variable; and any named arguments passed to the method itself. Later grammars override earlier ones; so if your model grammar and Event narrative both have a symbol `"adjectives"`, the event values are the ones used. Since each call generates a new grammar, you can't use Tracery actions / variable assignments (or rather; you can, but they won't persist past this specific narration).

Note that the keyword arguments passed to the `narrate` method are converted into a Tracery grammar; i.e. if you call it with `narrate(a=actor)`, the Tracery associated with that event will have access to a `#a#` symbol. Actor objects are converted to their names for Tracery purposes.

### Relationships

As mentioned above, Smew also lets you track relationships between actors. Relationships take the form of triples `(Actor, relationship, Actor)`, where the relationships themselves are just strings. You can add relationships with the `relate(a, relationship, b, reciprocal=True)` method (either on the model or the event). If `reciprocal=True` (the default), *two* relationships are added: `(a, relationship, b)` and `(b, relationship, a)`. If `reciprocal=False`, only the exact relationship is created. You can end a relationship with `unrelate` with the same arguments (again, if `reciprocal=False` it will only end the relationship in one direction). Actors can have any number of relationships, so if at some point you run `relate(a, "loves", b)` and later run `relate(a, "hates", b)` (for the same `a` and `b`), the latter does not overwrite the former; now `a` and `b` both `"love"` and `"hate"` each other.

You can access relationships using the `get_related` method. You can use it in three different ways:

* `get_related(a, "loves")` will return a list of all the actors that actor `a` loves, i.e. any actors matching `(a, "loves", *)`.

* `get_related("loves", a)` will return a list of all actors that love `a`, i.e. `(*, "loves", a)`.

* `get_related(a, "loves", b)` will return `True` if the relationship `(a, "loves", b)` exists, and `False` otherwise.


### Possible future work

Suggestions and pull requests welcome!

* At the moment, events and narration are tracked internally in `SmewModel.event_history` and `SmewModel.text_history`, respectively. It would be nice to have more sophisticated logging, including the actors and their current states. This would make it easier to pull out specific narrative strands (i.e. all events involving one actor, all events at a certain location).

* While we're at it, we should track the overall model state. This would also let us instantiate a model from a given model state.

* Add tags to events

* Make (some?) events actor-choosable; allow Actor subclasses to implement their own decision rules.

* Add more options for weighting event probabilities instead of just choosing uniformly at random.

* At the moment, if one event directly triggers another event, it needs to be called explicitly. It might be nice to allow events to directly trigger certain subsequent events (either deterministically or with some probability).

* Add actor grammar and narration, to allow actors to describe their current state (and possibly relationships).

### License

MIT License. 



