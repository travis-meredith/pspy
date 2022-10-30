
from contextlib import suppress
from typing import Callable, cast

TestFunction = Callable[[object], bool]

class Registered:

    name: str
    registry: list[tuple[TestFunction, Callable]]
    register: Callable
    dispatch: Callable

    def __call__(self, *args):
        return self.dispatch(*args)

def overload(default_function: Callable):

    registry: list[tuple[TestFunction, Callable]] = []

    def register(register_function: Callable):

        anno = getattr(register_function, "__annotations__", None)
        if anno is None:
            raise TypeError(f"No annotations provided to {register_function}")
        anno = cast(dict, anno)
        test_functions = tuple(anno.values())
        def tester(*args) -> tuple:
            if len(args) != len(test_functions):
                return ()
            with suppress(ValueError, TypeError):
                return tuple((test_function(arg) for test_function, arg in zip(test_functions, args)))
            return ()
        registry.append((tester, register_function)) # type: ignore

    def dispatch(*args):
        run_default = True
        for test, callback in reversed(registry):
            if run_default:
                nargs = test(*args)
                if nargs != ():
                    run_default = False
                    callback(*nargs)
        if run_default:
            default_function(*args)

    o = Registered()
    o.name = default_function.__name__
    o.registry = registry
    o.register = register # type: ignore
    o.dispatch = dispatch # type: ignore
    return o

def string_lower(s: str) -> str:
    return s.lower()

def string_equals(target_string: str) -> Callable[[str], str]:

    def _inner(string: str):
        if string.strip().lower() == target_string.strip().lower():
            return string.strip().lower()
        raise ValueError()

    return _inner
    
def string_membership(target_strings: set[str]) -> Callable[[str], str]:

    def _inner(string: str):
        string = string.strip().lower()
        if string in target_strings:
            return string
        raise ValueError()

    return _inner