from collections.abc import MutableMapping
from functools import wraps, cached_property, partial, update_wrapper
from inspect import getclasstree, getdoc
from typing import TypeVar, Iterator, Type, Optional, Set, Tuple, Union, List

_UNSET = object()

_T = TypeVar("_T")

walk_class_tree_hint = List[Union[Type, Tuple[Type, Type], "recurse_class_tree_hint"]]

def walk_class_tree(l: walk_class_tree_hint) -> Iterator[Type]:
	if isinstance(l, type):
		yield l
	elif isinstance(l, tuple):
		yield l[0]
		if len(l) > 1:
			yield from walk_class_tree(l[1])
	else:
		for ll in l:
			yield from walk_class_tree(ll)

def collect_all_slots(cls) -> Set[str]:
	slots = set()
	if hasattr(cls, "__slots__"):
		slots.update(cls.__slots__)
	for clls in walk_class_tree(getclasstree([cls])):
		if hasattr(clls, "__slots__"):
			slots.update(clls.__slots__)
	return slots


def iter_needed_slots(cls: Type) -> Iterator[Tuple[str, Optional[str]]]:
	for clls in walk_class_tree([cls]):
		for attr in dir(clls):
			try:
				val = getattr(clls, attr)
			except AttributeError:
				continue
			if not isinstance(val, cached_property):
				continue
			if val.attrname is None:
				raise TypeError("cached_property without name")
			yield val.attrname, getdoc(val.func)


def init(slot_dict, core_init, self, *args, **kwargs):
	class SlotRedirector(MutableMapping, dict):
		# I think inheriting from dict means we still have an empty
		# dictionary floating in memory for each SlotRedirector instantiated.
		# That's eighty bytes we don't need...but at least it doesn't grow.
		__slots__ = slot_dict

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
	self.__dict__ = SlotRedirector()
	if callable(core_init):
		core_init(self, *args, **kwargs)
	else:
		super(type(self), self).__init__(*args, **kwargs)

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
		slot_dict = dict(iter_needed_slots(cls))
		if hasattr(cls, "__slots__"):
			if isinstance(cls.__slots__, dict):
				slot_dict.update(cls.__slots__)
			else:
				for slot in cls.__slots__:
					slot_dict[slot] = None
		if hasattr(cls, "__init__"):
			part = partial(init, slot_dict, cls.__init__)
			update_wrapper(part, cls.__init__)
		else:
			part = partial(init, slot_dict, None)
		cls.__init__ = part
		return cls

	if cls is None:
		return really_reslot
	return really_reslot(cls)
