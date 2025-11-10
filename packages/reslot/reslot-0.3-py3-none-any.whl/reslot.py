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
		if cached_property.attrname is None:
			raise TypeError("cached_property without name")
		yield cached_property.attrname, getdoc(cached_property.func)

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

		class SlotRedirector(MutableMapping):
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

		if hasattr(cls, "__getattr__"):
			core_getattr = cls.__getattr__

			@wraps(core_getattr)
			def __getattr__(self: _T, attr: str):
				if attr == "__dict__":
					val = getattr(super(cls, self), "__dict__", _UNSET)
					if val is _UNSET:
						val = SlotRedirector()
						setattr(self, "__dict__", val)
					return val
				return core_getattr(self, attr)

			cls.__getattr__ = __getattr__
		else:

			def __getattr__(self: _T, attr: str):
				if attr == "__dict__":
					val = getattr(super(cls, self), "__dict__", _UNSET)
					if val is _UNSET:
						val = SlotRedirector()
						setattr(self, "__dict__", val)
					return val
				return getattr(super(type(self), self), attr)

			cls.__getattr__ = __getattr__
		return cls

	if cls is None:
		return really_reslot
	return really_reslot(cls)
