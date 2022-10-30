
import json
from sys import stdout
from typing import Callable, cast
from contextlib import contextmanager

import pyperclip  # type: ignore

from overload import Registered  # type: ignore

pyperclip.copy = cast(Callable[[str], None], pyperclip.copy)

__exposed__: dict[str, Registered] = {}

PATH = "C:\\Users\\frogb\\Desktop\\Workshop\\pspy"

def expose(function: Registered) -> Registered:
    __exposed__[function.name] = function
    return function

def route(extension: str) -> str:
    return f"{PATH}\\{extension}"

def script_content(cmd: str) -> str:
    return "\npython {_route} {_cmd} $args" \
           "\n{_next_script_route}".format(
               _route=route("\\filetools.py"), 
               _cmd=cmd, 
               _next_script_route=route(f"\\scripts\\callback.ps1")
               )

def create_command(cmd: str):
    with open(route(f"\\scripts\\{cmd}.ps1"), "w") as file:
        file.write(script_content(cmd))
    forward_command(cmd, "")

def forward_command(cmd: str, script: str):
    with open(route(f"\\scripts\\callback.ps1"), "w") as file:
        file.write(script)

def out_paste(string: object):
    string = str(string)
    out(string)
    pyperclip.copy(string)

def out(*args, **kwargs):
    print(*args, **kwargs, file=Out.OUT_STREAM)

class Operate:
    def operate(argv):
        print("ERROR")

class Out:
    
    OUT_STREAM = stdout

    @contextmanager
    def set_stream(stream):
        Out.OUT_STREAM = stream
        yield
        Out.OUT_STREAM = stdout
