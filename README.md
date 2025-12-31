# `pysyspath`: Python System Path Tools

`pysyspath` is a Python package mainly aimed at recursively crawling subfolders
and adding it to Python's system path quickly with common quirks ironed out

`pypath` is the main module that emulates MATLAB's `addpath()`, `genpath()` and `addpath(genpath())`. The major use case is 'Add everything you can find in there into the search path', which is approximately MATLAB's `addpath(genpath())`.

`lsos` (`ls` by OS) is the engine `pypath` used to crawl all subfolders recursively using standard command line
program provided in major OS (`dir` in Windows, `find` in POSIX/Linux/MacOS).

## The simplest recommended use case
```
from pysyspath import pypath
pypath.addpath_recursive('{your path here}')
```
This is the most common default use case (default optional parameters):
- add from the top (`side='-begin'`)
- search current directory first (`keepFirstEmptyPath=True`)
- skip paths that are already in `sys.path` (`excludeExisting=True`)
- the root input folder is included in the output (`is_self_included=True`)

## Consider using it in startup.py
If this tool is not already managed in a site-repository already (like `pip` downloads),
you can place the `pysyspath` package folder in the same folder as `startup.py` 
and use `pypath` to load your in-house libraries at startup.
```
import os
import sys

# Add the location of this startup.py which also contains pysyspath
path_to_this_file = os.path.dirname(os.path.realpath(__file__))
# The first element of sys.path is reserved for current directory ''
sys.path[1:1] = [path_to_this_file]

import pysyspath
user_library_path = 'D:/Python/Libraries'
pysyspath.pypath.addpath_recursive(user_library_path)
```

## Reviewing crawled (and optionally prepared) paths

If you want to see what the `addpath_recursive()` sees (current paths excluded)
```
pypath.recurse_subfolders_for_syspath('{your path here}')
```
`genpath()` is just `recurse_subfolders_for_syspath()` with `excludeExisting=True`


## MATLAB style interface

Mimick MATLAB's `addpath(genpath())`:
```
pypath.addpath_genpath('{your path here}')
```
- add from the top (`side='-begin'`)
- search current directory first (`keepFirstEmptyPath=True`)
- allow duplicate paths (`excludeExisting=False`)

Mimick MATLAB's `genpath()`:
```
pypath.genpath('{your path here}')
```

## Rare use case(s)

In the extremely rare case that you want the newly added path to be searched before current directory:
```
pypath.addpath_recursive_top('{your path here}', excludeExisting={your choice}, keepFirstEmptyPath=True)
```

## `lsos` can be used as a standalone package

If you do not need paths already in `sys.path` to be filtered out before adding (which reduces `sys.path` bloat),
don't bother with `pypath`.  Go straight to the juicy implementation in the `lsos` module
```
from pysyspath import lsos
lsos.list_subfolders_recursively('{your path here}')
```
`pypath.recurse_subfolders_for_syspath()` merely calls the same thing and optionally filters out unwanted (duplicate) paths. 

## Default behavior difference between `lsos` and `pypath`
If you just want to crawl subfolders recursively using OS commands and have nothing to do with `sys.path`, you'd be better off using the `lsos` module instead of `pypath.recurse_subfolders_for_syspath(p, excludeExisting=False)` which is clumsy. You don't want to confuse people who read your code thinking it's `_for_syspath` when you don't mean to.

By default `lsos.list_subfolders_recursively` work like Windows's `dir /b/s` which do not include the requested folder. It's more flexible for developers to add the root path back if they need it than trying to reliably identify and remove the unwanted root path. 

By default `is_self_included=True` everywhere in `pypath`. This means the input path is included in the crawled output only in `pypath`. The use case for `pypath` is 'Load everything you can find in this path', so obviously the requested path itself is intended too. You can override it if you have a good reason to do so.

## Limitations
`lsos` is currently hardcoded to Unicode filenames, which is the default in modern POSIX and but some `chcp` (codepage) gymanastics is needed to capture Windows' `stdout` in Unicode. If somebody needed more general codepage support, please let me know.

`pypath` uses `lsos` so they share the same filename encoding behavior

## Self-documenting code
Many advanced uses can be found in the code with self-explanatory names and structure. Optional parameters can found by the function declarations. It'd take less time to read the code than detailed docs once you get the basic ideas here.
