
import json
import os
from typing import Callable, Union, cast

from ftscripts import expose, forward_command, out, out_paste, route
from overload import overload, string_equals
from settings import Settings

def _strenumerate(ls: list, strPad: int = 4):
    for i, terms in enumerate(ls):
        _i = str(i).rjust(strPad, " ")
        if isinstance(terms, (tuple, list)):
            yield i % Settings.content_height, _i, *terms
        else:
            yield i % Settings.content_height, _i, terms

def _truncate_path(path: str, max_length: int) -> str:
    cutoff = (max_length // 2) - 2
    return "".join((path[:cutoff:], "...", path[len(path) - cutoff::]))

def truncate_path(path: str, max_length: int) -> str:
    return (_truncate_path(path, max_length) if len(path) >= max_length else path)

def _truncate_paths(paths: list[str], max_length: int) -> list[str]:
    return [_truncate_path(path, max_length) if len(path) >= max_length else path for path in paths]

class DirectorySearch:

    test_function: Union[Callable, None] = None

    @staticmethod
    def get_path_list(paths: list[str]) -> str:

        sanitised_paths = _truncate_paths(paths, Settings.file_name_length)
        string_list = ["" for _ in range(Settings.content_height)]
        for i, _i, path in _strenumerate(sanitised_paths):
            slr = path.rjust(Settings.file_name_length, "-")
            string_list[i] = " | ".join((string_list[i], f"{_i} {slr}"))
        return "\n".join(string_list).strip()

    @staticmethod
    def look() -> list[str]:
        cwd = os.getcwd()
        paths = []
        for path in os.listdir(cwd):
            if DirectorySearch.test_function(path):  # type: ignore
                paths.append(path)
        return paths

    @staticmethod
    def equate_string(s: str) -> int:
        if s[0] == "=":
            return int(s[1::])
        raise ValueError()

    @staticmethod
    def npequate_string(s: str) -> str:
        if s[0] == "=":
            return s
        raise ValueError()

    @staticmethod
    def l_display(paths: list[str]):
        print("*" * Settings.content_width)
        out(" ", end="")
        out(DirectorySearch.get_path_list(paths))
        print("*" * Settings.content_width)



"""
    ######## l[ f | d ]
"""

def grab_indexed_term(terms: list[str], index: int) -> str:
    if 0 <= index < len(terms):
        return terms[index]
    return ""

@expose
@overload
def l():
    print(f"Looking at {os.getcwd()}:\n")
    if DirectorySearch.test_function is None:
        DirectorySearch.test_function = lambda string: True
    terms = DirectorySearch.look()
    DirectorySearch.l_display(terms)

@l.register
def term_no_target(search_term: str):
    print(f"Looking for {search_term} in {os.getcwd()}")
    if DirectorySearch.test_function is None:
        DirectorySearch.test_function = lambda string: string.count(search_term) > 0
    terms = DirectorySearch.look()
    DirectorySearch.l_display(terms)

@l.register
def no_term_target(target: DirectorySearch.equate_string): # type: ignore
    # target: int
    if DirectorySearch.test_function is None:
        DirectorySearch.test_function = lambda string: True
    terms = DirectorySearch.look()
    found = grab_indexed_term(terms, target)
    if found == "":
        print(f"Cannot search for index `{target}` as it doesn't exist")
    else:
        out_paste(f".\\{terms[target]}")

@l.register
def term_target(search_term: str, target: DirectorySearch.equate_string): # type: ignore
    # target: int
    print(f"Looking for {search_term} in {os.getcwd()}")
    if DirectorySearch.test_function is None:
        DirectorySearch.test_function = lambda string: string.count(search_term) > 0
    terms = DirectorySearch.look()
    found = grab_indexed_term(terms, target)
    if found == "":
        print(f"Cannot search for index `{target}` as it doesn't exist")
    else:
        out_paste(f".\\{terms[target]}")

@expose
@overload
def lf():
    DirectorySearch.test_function = lambda string: os.path.isfile(string)
    l()

@lf.register
def fterm_no_target(search_term: str):
    DirectorySearch.test_function = lambda string: os.path.isfile(string) and string.count(search_term) > 0
    l(search_term)
    
@lf.register
def fno_term_target(target: DirectorySearch.npequate_string): # type: ignore
    DirectorySearch.test_function = lambda string: os.path.isfile(string)
    l(target)

@lf.register
def fterm_target(search_term: str, target: DirectorySearch.npequate_string): # type: ignore
    DirectorySearch.test_function = lambda string: os.path.isfile(string) and string.count(search_term) > 0
    l(search_term, target)

@expose
@overload
def ld():
    DirectorySearch.test_function = lambda string: os.path.isdir(string)
    l()

@ld.register
def dterm_no_target(search_term: str):
    DirectorySearch.test_function = lambda string: os.path.isdir(string) and string.count(search_term) > 0
    l(search_term)
    
@ld.register
def dno_term_target(target: DirectorySearch.npequate_string): # type: ignore
    DirectorySearch.test_function = lambda string: os.path.isdir(string)
    l(target)

@ld.register
def dterm_target(search_term: str, target: DirectorySearch.npequate_string): # type: ignore
    DirectorySearch.test_function = lambda string: os.path.isdir(string) and string.count(search_term) > 0
    l(search_term, target)

"""
        ####    goto[ s | e | l ]
"""

def get_jumps() -> dict:
    return json.load(open(route("objects\\goto.json")))

def dump_jumps(jumps: dict):
    json.dump(jumps, open(route("objects\\goto.json"), "w"))

def add_jump(key: str, target: str):
    jumps = get_jumps()
    jumps[key] = target
    dump_jumps(jumps)

def remove_jump(key: str):
    jumps = get_jumps()
    del jumps[key]
    dump_jumps(jumps)

def get_trips() -> list:
    return json.load(open(route("objects\\return.json")))["return"]

def dump_trips(trips: list[str]):
    d = {"return": trips}
    json.dump(d, open(route("objects\\return.json"), "w"))

def add_trip(route: str):
    trips = get_trips()
    trips.append(route)
    dump_trips(trips)

def pop_trip() -> str:
    trips = get_trips()
    trip = trips.pop()
    target_trip = trips[-1]
    dump_trips(trips)
    return target_trip

@expose
@overload
def goto():
    jumps = get_jumps()
    print("Goto jump list:")
    print("*" * Settings.content_width)
    for alias, jump in jumps.items():
        _alias = alias.rjust(Settings.goto_list_width, " ")
        _jump = truncate_path(jump, Settings.content_width - Settings.goto_list_width).ljust(Settings.content_width - Settings.goto_list_width - 12, " ")
        print(f"\t{_alias} -> {_jump}", end="\n")
    print("*" * Settings.content_width)

@goto.register
def jump_to(key: str):
    print(f"Jumping to {key}:")
    jumps = get_jumps()
    if key in jumps:
        target = cast(str, jumps[key])
        if not os.path.isdir(target):
            target = "\\".join(target.split("\\")[:-1:])
        forward_command("goto", f"cd \"{target}\"")
        add_trip(target)
    else:
        print(f"\tKey `{key}` does not exist!")

@goto.register
def jump_back(_: string_equals("..")): # type: ignore
    print(f"Returning to last jump")
    target = pop_trip()
    forward_command("goto", f"cd \"{target}\"")

@expose
@overload
def gotoe():
    goto()

@gotoe.register
def open_explorer_at(key: str):
    print(f"Opening explorer at {key}:")
    jumps = get_jumps()
    if key in jumps:
        target = jumps[key]
        forward_command("gotoe", f"explorer.exe \"{target}\"")
    else:
        print(f"\tKey `{key}` does not exist!")

@expose
@overload
def gotol():
    goto()

@gotol.register
def launch_program(key: str):
    print(f"Launching program from {key}:")
    jumps = get_jumps()
    if key in jumps:
        target = jumps[key]
        forward_command("gotol", f"Start-Process \"{target}\"")
    else:
        print(f"\tKey `{key}` does not exist!")

"""
        ####    aw[ p | d ]
"""

@expose
@overload
def awp():
    print("Add Waypoint:\n\tawp <key> <path>")

@awp.register
def error_no_path(key: str):
    print(f"Need more arguments! No path supplied")

@awp.register
def add_waypoint(key: str, path: str):
    jumps = get_jumps()
    if key in jumps:
        print(f"Key {key} already in paths. Delete with awd")
    else:
        jumps[key] = path
        dump_jumps(jumps)

@expose
@overload
def awd():
    print("Delete Waypoint:\n\tawd <key>")

@awd.register
def delete_waypoint(key: str):
    jumps = get_jumps()
    if key in jumps:
        del jumps[key]
        dump_jumps(jumps)
    else:
        print(f"Key {key} does not exist so cannot be deleted!")


@expose
@overload
def path():
    out_paste(os.getcwd())

@expose
@overload
def touch():
    print("Create file at location:")
    print("\t<filename>: Creates <filename> empty")
    print("\t<filename> <content_string>: Creates <filename> with <content> written")

@touch.register
def touch_filename(filename: str):
    if os.path.exists(filename):
        print(f"Touch will not overwrite file {filename} ({os.getcwd()})")
    else:
        with open(filename, "w") as f:
            pass

@touch.register
def touch_filename_with_content(filename: str, content: str):
    if os.path.exists(filename):
        print(f"Touch will not overwrite file {filename} ({os.getcwd()})")
    else:
        with open(filename, "w") as f:
            f.write(content)


@expose
@overload
def dump():
    print("give target file")

@dump.register
def dump_file(filename: str):
    if os.path.exists(filename):
        ...
