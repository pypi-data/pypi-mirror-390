import builtins
from collections.abc import MutableMapping
from functools import wraps, cached_property
from inspect import getclasstree, getdoc
from typing import TypeVar, Iterator, Type, Optional, Set, Tuple

_UNSET = object()

_T = TypeVar("_T")


def collect_all_slots(cls) -> Set[str]:
	def recurse(l):
		if isinstance(l, type):
			yield l
		elif isinstance(l, tuple):
			yield l[0]
			yield from map(recurse, l[1])
		else:
			for ll in l:
				yield from recurse(ll)

	slots = set()
	if hasattr(cls, "__slots__"):
		slots.update(cls.__slots__)
	for clls in recurse(getclasstree([cls])):
		if hasattr(clls, "__slots__"):
			slots.update(clls.__slots__)
	return slots


def iter_needed_slots(cls: Type) -> Iterator[Tuple[str, str]]:
	for attr in dir(cls):
		try:
			val = getattr(cls, attr)
		except AttributeError:
			continue
		if not isinstance(val, cached_property):
			continue
		if val.attrname is None:
			raise TypeError("cached_property without name")
		yield val.attrname, getdoc(val.func)

def reslot(
	cls: Optional[Type[_T]] = None,
) -> Type[_T]:
	"""Class decorator to enable ``@cached_property`` with ``__slots__``

	The decorated class needs a ``__dict__`` slot, but we won't put an actual
	dictionary in it. Instead, we'll put a mapping with the needed slots in it.
	"""

	def really_reslot(cls: Type[_T]) -> Type[_T]:
		if not hasattr(cls, "__slots__"):
			raise TypeError("Class doesn't have __slots__")
		slots = collect_all_slots(cls)
		if "__dict__" not in slots:
			raise TypeError("Need __dict__ slot")

		class SlotRedirector(dict, MutableMapping):
			# I think inheriting from dict means we still have an empty
			# dictionary floating in memory for each SlotRedirector instantiated.
			# That's eighty bytes we don't need...but at least it doesn't grow.
			__slots__ = dict(iter_needed_slots(cls))

			def __setitem__(self, key, value, /):
				try:
					setattr(self, key, value)
				except AttributeError:
					raise KeyError("No such slot", key) from None

			def __delitem__(self, key, /):
				try:
					delattr(self, key)
				except AttributeError:
					raise KeyError("Slot not set", key)

			def __getitem__(self, key, /):
				try:
					return getattr(self, key)
				except AttributeError:
					raise KeyError("Slot not set", key)

			def __len__(self):
				return len(self.__slots__)

			def __iter__(self):
				return iter(self.__slots__)

		if hasattr(cls, "__init__"):
			core__init__ = cls.__init__

			@wraps(core__init__)
			def __init__(self, *args, **kwargs):
				self.__dict__ = SlotRedirector()
				core__init__(self, *args, **kwargs)

			cls.__init__ = __init__
		else:
			def __init__(self, *args, **kwargs):
				self.__dict__ = SlotRedirector()
				super(cls, self).__init__(*args, **kwargs)

			cls.__init__ = __init__
		return cls

	if cls is None:
		return really_reslot
	return really_reslot(cls)
