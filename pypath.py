# -*- coding: utf-8 -*-
"""
pypath provides tools to add a folder and every path under it recursively
with optimizations to reduce the overheads for a large number of paths and
prevent bloating sys.path with duplicate new entries.

This is functionally similar to MATLAB's addpath(genpath()) idiom.

Add from the top if the new paths takes priority and add from
the bottom if the new paths should not shadow what's already out there

Unlike MATLAB that natively stores the path in strings so it can be manipulated
without a cellstr overhead, Python's sys.path is natively stored as a list so
adding new entries is not fast like appending to a string.

By default pypath removes existing paths from new paths before adding them for 
perforamnce. 

Set excludeExisting=False if 
1) you think the set difference overhead outweights the redundant paths 
sys.path has to carry. 
2) you want unconditionally give priority to all new paths, including those
that already existed, by adding them from the top. (Logically repeated paths
added to the bottom are ignored anyway.)
3) Set diffing might reorder the new paths. If you rely on the order of
the new paths to add, you might not want the default behavior. 

It's bad programming practice to allow shadowing so that the path orders in 
sys.path mattered. You want to avoid name collisions.

The first entry in sys.path is an empty string '' to make sure the current
directory is searched first. The default behavior is to keep the current
directory being the first even when new paths are added from the top.

If you do not want the current directory to be always searched first, set
keepFirstEmptyPath=False. This special case doesn't apply to new paths added 
from the bottom for obvious reasons (duh).

Internally pypath uses the lsos module which does fast folder recursions using
native OS programs ('dir' for Windows and 'find' for POSIX) to keep the 
overhead processing large number of paths down.

By default the requested path is included in the output in pypath but not in
lsos because lsos is meant to be flexible (adding things later is easier than
hunting down things you don't want) yet pypath naturally wants to get 
everything in the specified path.

"""

import sys
import lsos
        
def keep_only_new_set_of_paths(list_of_paths):
    if not isinstance(list_of_paths, list | tuple | set):
        # The check is incomplete since it doesn't check the elements for non-string
        # But for performance it's not worth overchecking it.
        raise TypeError('list_of_paths should be a list/tuple/set of strings')        
    return set(list_of_paths)-set(sys.path)

def recurse_subfolders_for_syspath(p, excludeExisting=True, is_self_included=True):
    new_subfolders = lsos.list_subfolders_recursively(p, is_self_included)
    if excludeExisting:
        new_subfolders = keep_only_new_set_of_paths( new_subfolders )        
    return new_subfolders

# MATLAB comfort wrapper
def genpath(p, excludeExisting=False, is_self_included=True):
    return recurse_subfolders_for_syspath(p, excludeExisting, is_self_included)

# In case if users passed strings (one path)
def ensure_list(x):
    if isinstance(x, list|set|tuple):
        x = list(x)
    else:
        x = [x]                      
    return x



# Equivalent to MATLAB's addpath(..., '-end')
def addpath_bottom(p):
    sys.path.extend(ensure_list(p))
    
# Equivalent to MATLAB's addpath(..., '-begin')
def addpath_top(p, keepFirstEmptyPath=True):
    insert_index = int(keepFirstEmptyPath)
    sys.path[insert_index:insert_index] = ensure_list(p)

# MATLAB comfort wrapper
# side='-end' if you want to add from the bottom
def addpath(p, side='-begin'):
    # MATLAB's default behavior is to add to the front/top
    if 'end' in side:
        addpath_bottom(p)
    else:
        # MATLAB always search current directory first
        addpath_top(p)    



# The default behavior is to exclude already existing paths from the new paths.
def addpath_recursive_bottom(p, excludeExisting=True, is_self_included=True):
    addpath_bottom(recurse_subfolders_for_syspath(p, excludeExisting, is_self_included))

def addpath_recursive_top(p, excludeExisting=True, keepFirstEmptyPath=True, is_self_included=True):
    addpath_top(recurse_subfolders_for_syspath(p, excludeExisting, is_self_included), keepFirstEmptyPath)

# Typical use case (search current directory first)
def addpath_recursive(p, side='-begin', excludeExisting=True, is_self_included=True):
    new_folders = recurse_subfolders_for_syspath(p, excludeExisting, is_self_included)
    addpath(new_folders, side)
        
# MATLAB comfort wrapper (genpath does not filter duplicates)
def addpath_genpath(p, side='-begin', excludeExisting=False, is_self_included=True):
    new_folders = recurse_subfolders_for_syspath(p, excludeExisting, is_self_included)
    addpath(new_folders, side)
    
# MATLAB's addpath(genpath()) without any modifier is equivalent to
# pypath.addpath_recursive_top(p, excludeExisting=False)