from typing import Callable, Dict, List
import abc
import copy
import operator


empty = object()


def method_proxy(func):
    def inner(self, *args):
        if self._wrapped is empty:
            self._setup()
        return func(self._wrapped, *args)
    return inner


class Lazy:
    """
    A wrapper for another class that can be used to delay instantiation of the
    wrapped class. The wrapper can provide properties that are already known
    (without instantiating the wrapped class).
    """

    # Avoid infinite recursion when tracing __init__
    _wrapped = None

    def __init__(self, getter: Callable, known_properties: Dict = None, known_non_properties: List = None):
        # Note: if a subclass overrides __init__(), it will likely need to
        # override __copy__() and __deepcopy__() as well.
        self.__dict__['_get_wrapped'] = getter
        self._wrapped = empty
        self.__dict__["_known_properties"] = known_properties if known_properties else {}
        self.__dict__["_known_non_properties"] = known_non_properties if known_non_properties else []

    def __getattr__(self, name):
        if self._wrapped is empty and name in self._known_properties:
            return self._known_properties[name]
        else:
            if self._wrapped is empty:
                if name in self._known_non_properties:
                    raise AttributeError()
                self._setup()
            return getattr(self._wrapped, name)

    def __setattr__(self, name, value):
        if name == "_wrapped":
            # Assign to __dict__ to avoid infinite __setattr__ loops
            self.__dict__["_wrapped"] = value
        else:
            if self._wrapped is empty:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        if name == "_wrapped":
            raise TypeError("Can't delete _wrapped.")
        if self._wrapped is empty:
            if name in self._known_non_properties:
                raise AttributeError()
            self._setup()
        delattr(self._wrapped, name)

    @abc.abstractmethod
    def _setup(self):
        self._wrapped = self._get_wrapped()

    def __reduce__(self):
        # Because we have messed with __class__ below, we confuse pickle as to what
        # class we are pickling. We're going to have to initialize the wrapped
        # object to successfully pickle it, so we might as well just pickle the
        # wrapped object since they're supposed to act the same way.
        #
        # Unfortunately, if we try to simply act like the wrapped object, the ruse
        # will break down when pickle gets our id(). Thus we end up with pickle
        # thinking, in effect, that we are a distinct object from the wrapped
        # object, but with the same __dict__. This can cause problems (see #25389).
        #
        # So instead, we define our own __reduce__ method and custom unpickler. We
        # pickle the wrapped object as the unpickler's argument, so that pickle
        # will pickle it normally, and then the unpickler simply returns its
        # argument.
        def unpickle_lazyobject(wrapped):
            return wrapped
        if self._wrapped is empty:
            self._setup()
        return unpickle_lazyobject, (self._wrapped,)

    def __copy__(self):
        if self._wrapped is empty:
            # If uninitialized, copy the wrapper. Use type(self), not
            # self.__class__, because the latter is proxied.
            return type(self)(self._get_object, self._known_properties)
        else:
            # If initialized, return a copy of the wrapped object.
            return copy.copy(self._wrapped)

    def __deepcopy__(self, memo):
        if self._wrapped is empty:
            # We have to use type(self), not self.__class__, because the
            # latter is proxied.
            result = type(self)(self._get_object, self._known_properties)
            memo[id(self)] = result
            return result
        return copy.deepcopy(self._wrapped, memo)

    __bytes__ = method_proxy(bytes)
    __str__ = method_proxy(str)
    __bool__ = method_proxy(bool)

    # Introspection support
    __dir__ = method_proxy(dir)

    # Need to pretend to be the wrapped class, for the sake of objects that
    # care about this (especially in equality tests)
    __class__ = property(method_proxy(operator.attrgetter("__class__")))
    __eq__ = method_proxy(operator.eq)
    __lt__ = method_proxy(operator.lt)
    __gt__ = method_proxy(operator.gt)
    __ne__ = method_proxy(operator.ne)
    __hash__ = method_proxy(hash)

    # List/Tuple/Dictionary methods support
    __getitem__ = method_proxy(operator.getitem)
    __setitem__ = method_proxy(operator.setitem)
    __delitem__ = method_proxy(operator.delitem)
    __iter__ = method_proxy(iter)
    __len__ = method_proxy(len)
    __contains__ = method_proxy(operator.contains)

    def __repr__(self):
        if self._wrapped is empty:
            return f"{type(self).__name__} -> {self._setupfunc}"
        else:
            return repr(self._wrapped)
