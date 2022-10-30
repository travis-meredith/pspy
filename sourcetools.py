
import os

from ftscripts import expose, out
from overload import overload, string_membership
from settings import Settings

NULL = "", "\n", "\r", "\n\r", "\t", "\t\t", " ", "  ", "   ", "    "

CHARS = 90
CHARSE = 110

def find_files_with_suffixs(route: str, suffixs: list[str]) -> list[str]:
    routes = []
    for base, _, files in (os.walk(route)):
        for file in files:
            for suffix in suffixs:
                if file.endswith(suffix):
                    routes.append(f"{base}\\{file}")
    return routes

def find_files_with_prefix(route: str, prefix: str) -> list[str]:
    routes = []
    for base, _, files in (os.walk(route)):
        for file in files:
            if file.startswith(prefix):
                routes.append(f"{base}\\{file}")
    return routes
    
def count_lines_in_file(route: str) -> int:
    with open(route, "r") as f:
        return sum((line not in NULL for line in f.readlines()))

def display_in_path_order(route: str):
    out("*" * CHARSE)
    routes = find_files_with_suffixs(route, [".py", ".glsl"])
    total = 0
    for route in routes:
        route = route.replace(".\\", "")
        token = " " * (CHARS - len(route))
        lines = count_lines_in_file(route)
        total += lines
        lstring = str(lines).rjust(6, " ")
        out(f"* {route} has{token}{lstring}")
    return total

def display_in_order(route: str):
    out("*" * CHARSE)
    routes = find_files_with_suffixs(route, [".py", ".glsl"])
    total = 0
    data = {}
    for route in routes:
        data[route] = count_lines_in_file(route)
    sort = {k: v for k, v in sorted(data.items(), key=lambda item: item[1])}.items()
    for route, lines in sort:
        total += lines
        token = " " * (47 - len(route))
        lstring = str(lines).rjust(6, " ")
        out(f"* {route} has{token}{lstring}")
    return total

def _sloc(start_path: str=".", sort: bool=False, loose: bool=False):

    global NULL
    if loose:
        NULL = (NULL[0],) # type: ignore

    total = display_in_order(start_path) if sort else display_in_path_order(start_path)

    out("*" * Settings.content_width)
    token = (Settings.content_width - 18)
    lstring = str(total).rjust(6, " ")
    out(f"Total lines across files{token}{lstring}")
    out("*" * Settings.content_width)

@expose
@overload
def sloc():
    _sloc()

@sloc.register
def one_flag(flag: string_membership({"-s", "-l"})): # type: ignore
    _sloc(sort="-s" == flag, loose="-l" == flag)

@sloc.register
def two_flags(flaga: string_membership({"-s", "-l"}), flagb: string_membership({"-s", "-l"})): # type: ignore
    flags = {flaga, flagb}
    _sloc(sort="-s" in flags, loose="-l" in flags)
