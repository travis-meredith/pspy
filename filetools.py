
from __future__ import annotations

import json
import os
import sys

from ftscripts import (PATH, Operate, __exposed__, create_command, forward_command,
                       out, route)
from settings import Settings


def operate(argv):

    import metatools
    import pathtools
    import searchtools
    import sourcetools

    for cmd in __exposed__:
        create_command(cmd)
    if len(argv) == 1:
        print("No argument. Generated PowerShell Scripts (.ps1).\n\tTools: ", end="")
        print(", ".join(sorted(__exposed__)))
        return sys.exit(0)
    if argv[1] in __exposed__:
        forward_command(argv[1], "")
        __exposed__[argv[1]](*argv[2::])
    else:
        print(f"Filetools function {argv[1], (type(argv[1]))} does not exist.")

if __name__ == "__main__":

    with open(route("objects\\settings.json"), "r") as settings_file:
        settings = json.load(settings_file)

    # populate globals from settings here
    for key, value in settings.items():
        setattr(Settings, key, value)

    # main
    Operate.operate = operate # type: ignore
    operate(sys.argv)
