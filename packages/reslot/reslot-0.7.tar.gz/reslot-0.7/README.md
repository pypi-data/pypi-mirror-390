# reslot


A class decorator that lets you use `@cached_property` on classes with `__slots__`.

The decorated class needs a `__dict__` slot, but there won't exactly be a
dictionary in it. Instead, `@reslot` will give it a custom `MutableMapping`
with *its own* slots. `@cached_property` will keep its cache there.

The custom `MutableMapping`'s slots will be exactly the slots needed to store
the results of every `@cached_property` that was on the class at the time it
was declared. This minimizes the memory footprint and makes lookup speedy.


## Usage

```python
from functools import cached_property

from reslot import reslot

BEANED = False

@reslot
class Spam:
    __slots__ = ("__dict__",)

    @cached_property
    def eggs(self):
        return {"delicious": False}

    @cached_property
    def beans(self):
        global BEANED
        BEANED = True
        return {"spam": 111000, "delicious": True}

spam = Spam()
print(spam.eggs)   # {"delicious": False}
print(BEANED)      # False
print(spam.beans)  # {"spam": 111000, "delicious": True}
print(BEANED)      # True
```