

import os
from typing import Callable, Union
from ftscripts import expose, out
from overload import TestFunction, overload, string_equals, string_membership

def _wide_scan_names(path: str, test_function: Callable[[str], bool]):
    candidates = []
    try:
        for candidate in os.listdir(path):
            paths = f"{path}\\{candidate}"
            if os.path.isfile(paths):
                if test_function(candidate):
                    yield paths
            elif os.path.isdir(paths):
                if test_function(candidate):
                    yield paths
                candidates.append(paths)
    except OSError:
        pass
    yield candidates

def wide_scan_names(path: str, test_function: Callable[[str], bool], lim: Union[float, int] = 1_000):
    out(path, lim)
    i = 0
    li = -1
    cPatha = [[path]]
    while i < lim:
        cPathsu = list()
        li = i
        for cPaths in cPatha:
            for cPath in cPaths:
                for candidate in _wide_scan_names(cPath, test_function):
                    i += 1
                    if isinstance(candidate, str):
                        # match
                        yield candidate
                    elif isinstance(candidate, list):
                        # dirs
                        cPathsu.append(candidate)
        if li == i:
            return
        cPatha = tuple(cPathsu) # type: ignore

def _wsn(test_function: Callable[[str], bool], start_path: str=os.getcwd(), limit: Union[float, int]=float("inf")):

    for match in wide_scan_names(start_path, test_function, limit):
        out(match)

@expose
@overload
def wsn():
    out("Wide Seach:")
    out("\tstring: `wsn string <search_string>` finds all files containing this string")
    out("\textension: `wsn [ ext | extension ] <file_suffix>` finds all files ending in this string")
    out("\teval: `wsn eval <eval_string>` uses eval (test string is called `string`) on all items")

@wsn.register
def wsn_string(_: string_equals("string"), test_string: str): # type: ignore
    _wsn(lambda string: test_string in string)

@wsn.register
def wsn_ext(_: string_membership({"extension", "ext"}), test_ext: str): # type: ignore
    _wsn(lambda string: string.endswith(test_ext))

@wsn.register
def wsn_eval(_: string_membership({"eval"}), eval_string: str): # type: ignore
    _wsn(lambda string: eval(eval_string))

@expose
@overload
def wsnf():
    out("Wide Seach for file:")
    out("\tstring: `wsnf string <search_string>` finds all files containing this string")
    out("\textension: `wsnf [ ext | extension ] <file_suffix>` finds all files ending in this string")
    out("\teval: `wsnf eval <eval_string>` uses eval (test string is called `string`) on all items")

@wsnf.register
def wsnf_string(_: string_equals("string"), test_string: str): # type: ignore
    _wsn(lambda string: test_string in string and os.path.isfile(string))

@wsnf.register
def wsnf_ext(_: string_membership({"extension", "ext"}), test_ext: str): # type: ignore
    _wsn(lambda string: string.endswith(test_ext) and os.path.isfile(string))

@wsnf.register
def wsnf_eval(_: string_membership({"eval"}), eval_string: str): # type: ignore
    _wsn(lambda string: eval(eval_string) and os.path.isfile(string))

@expose
@overload
def wsnd():
    out("Wide Seach for directory:")
    out("\tstring: `wsnd string <search_string>` finds all directories containing this string")
    out("\textension: `wsnd [ ext | extension ] <file_suffix>` finds all directories ending in this string")
    out("\teval: `wsnd eval <eval_string>` uses eval (test string is called `string`) on all directories")

@wsnd.register
def wsnd_string(_: string_equals("string"), test_string: str): # type: ignore
    _wsn(lambda string: test_string in string and os.path.isdir(string))

@wsnd.register
def wsnd_ext(_: string_membership({"extension", "ext"}), test_ext: str): # type: ignore
    _wsn(lambda string: string.endswith(test_ext) and os.path.isdir(string))

@wsnd.register
def wsnd_eval(_: string_membership({"eval"}), eval_string: str): # type: ignore
    _wsn(lambda string: eval(eval_string) and os.path.isdir(string))
