


import json
import os

from overload import overload, string_equals, string_lower
from ftscripts import expose, out, out_paste, route
from settings import Settings



@expose 
@overload
def conf():
    print("Conf:\n\tclear: sets all config to default\n\t<attr_name> <new_value> (note: uses `eval`)")
    out(Settings.serialise())

@conf.register
def clear_config(action: string_equals("clear")): # type: ignore
    # str
    with open(route("/objects/settings.json"), "w") as file:
        json.dump(Settings.serialise(), file)

@conf.register
def add_config(key: str, value: str):
    setattr(Settings, key, eval(value))
    js = json.dumps(Settings.serialise())
    with open(route("/objects/settings.json"), "w") as file:
        file.write(js)

@expose
@overload
def env():
    print("Usage:")
    print("\tArg0 = `keys` to list all os.environ keys\n\tArg0 = `items` to list all os.environ pairs")
    print("\tFlag: -f is the format flag. Seperates elements in key by semicolon")
    print("\tInsert: `env insert <key> <index> <value>` to insert new values in semicolon seperated keys")
    print("\t\Del: `env del <key> <index>` to insert new values in semicolon seperated keys")

@env.register
def key(key: str):
    print(f"{key} is: \n\t", end="")
    out_paste(os.environ.get(key))

@env.register
def keys(_: string_equals("keys")): # type: ignore
    out_paste(list(os.environ.keys()))

@env.register
def items(_: string_equals("items")): # type: ignore
    for key, item in os.environ.items():
        out(f"{key}: {item}")

@env.register
def format_(key: str, _: string_equals("-f")): # type: ignore
    print(f"{key} is: \n", end="")
    out_paste("\n".join(os.environ.get(key).split(";"))) # type: ignore

@env.register
def insert(_: string_equals("insert"), key: str, index: int, value: str): # type: ignore
    print(f"Inserting {value} into {key} at {index}")
    ls = os.environ.get(key).split(";") # type: ignore
    ls.insert(index, value)
    os.environ[key] = ";".join(ls)

@env.register
def removea(_: string_equals("del"), key: str, index: int): # type: ignore
    ls = os.environ.get(key).split(";") # type: ignore
    print(f"Deleting value {ls[index]} at index {index} from {key}")
    del ls[index]
    os.environ[key] = ";".join(ls)

