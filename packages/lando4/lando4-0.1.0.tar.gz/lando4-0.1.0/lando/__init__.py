# lando/__init__.py

from . import examples

# expose all examples directly
ex1 = examples.ex1
ex2 = examples.ex2
ex3 = examples.ex3
ex4 = examples.ex4
ex5 = examples.ex5
ex6 = examples.ex6
ex7 = examples.ex7

def get(name: str):
    """Return example code dynamically by name, e.g. lando.get('ex1')."""
    return getattr(examples, name, f"No example named '{name}' found.")
