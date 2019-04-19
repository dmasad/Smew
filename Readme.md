# Smew

Smew is a Python framework with a focus on event-driven generative narrative. Smew lets you define `Actors`, and `Events` which can happen to those actors and generate some text associated with them. Smew is heavily inspired by [Sea Duck]() by [Allison Parrish]() (A smew is a kind of sea duck).

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
model.advance()
```

If you run this, you'll see either `'Hello world!' says Narrator`, or `Narrator says 'Hello world!'`.  

