# -*- coding: utf-8 -*-
"""
lsos is list structure (proxy) done by the OS (native commands)
whenever possible for performance. 

Major Python path tools often gets more information than needed then expect
users to filter out what they needed using Python code, which is much slower 
than a direct call to the OS's optimized tool (likely written in C) to give 
exactly what's neeed in one shot when the number of files/folders gets large

Right now the program is hard-coded to Unicode for Windows (65001) 
and Linux is assumed to be UTF-8 by default. I'm open to making it flexible
and generic later as needs arises on my end or if other people provide their
use cases detailed enough for me to test it on my end.

"""
import os
import subprocess

def assert_dir(p):
    # System call errors are slow to throw. Catch easy bad inputs first
    if not os.path.isdir(p): 
        raise NotADirectoryError('Input path does not exist or is not a folder')
    

# Windows (dir) and POSIX (find) have opposite default behavior of including
# the requested path (root) in the results or not. For performance, I'd rather
# not make all of them exclude the root and add that later (because it'd add
# unnecessary work for POSIX implementation)

# f-string is needed to interpret the escaped raw text output from text=True
 
# NOTE: Assume Unicode Codepage (65001) in Windows 
#
#       Since 'chcp' has text output that is not desired, the output needs
#       to be sent to a blackhole if I try to use '&' to run 2 'dir' after it
#
#       By using pipes(|), we take advantage of the fact 'dir' does not read
#       pipe so chcp's unwanted output piped to it gets dropped as desired when 
#       we run 'chcp' and 'dir' in one line sequentially.
#
# dir /s unconditionally shows full path 
# dir /b does not show full path if it's not recursive (with /s)
#
# Use '\n' instead of '\n\r' even in Windows because Python's universal
# newline is generated with text=True (which is also called universal_newlines)
# unifies all newlines to '\n'
def win_list_recursively_in_str(p, is_self_included=True, show_directories_only=False):    
    assert_dir(p)
    self_line = p+u'\n' if is_self_included else u''
    
    # dir /ad is attribute(a) with directory(d) set
    additional_switches = '/ad' if show_directories_only else ''
    
    return self_line+f'{subprocess.check_output(f"chcp 65001 | dir /b/s{additional_switches} {p}", shell=True, text=True)}'

def win_list_folders_recursively_in_str(p, is_self_included=True):
    return win_list_recursively_in_str(p, is_self_included, show_directories_only=True)


# Unix-like system including MacOS is POSIX (has 'find' and 'readlink')

# 0th depth is the folder p itself. This is the default.
# To exclude the self-path, start with 1 as minimum depth (-mindepth)
# use 'find -type d' because 'ls' do not check directory type

# 'find' follows relative/absolute from the input path (unlike 'dir /s')
# 'readlink -f' force absolute path for input path

def posix_list_recursively_in_str(p, is_self_included=True, show_directories_only=False): 
    assert_dir(p)
    
    min_depth = int(not is_self_included)
    
    # -name * does not work, the * must be in quotes
    additional_switches = r'-type d ' if show_directories_only else r'-name "*"'
    
    cmd_str = f'find $(readlink -f {p}) -mindepth {min_depth} {additional_switches}'
    return f'{subprocess.check_output({cmd_str}, shell=True, text=True)}'

def posix_list_folders_recursively_in_str(p, is_self_included=True):
    return posix_list_recursively_in_str(p, is_self_included=True, show_directories_only=True)


# Use this slower version only for non-mainstream OS

# The first (0th output is the root path p itself)
# Checking if the first entry is p incurs overhead. Skipped


def strip_wildcard_basename(p):
    # Any tail portion (basename) containing wildcard(s) will be discarded and
    # the chain above (dirname) above will be processed    
    p = os.path.dirname(p) if '*' in os.path.basename(p) else p            
    if '*' in p:
        raise NotADirectoryError('No shenanigans like sandwiching * wildcards in paths please.')
    return p

import glob
def _glob_recursive(p, path_join_list, is_self_included=True):
    p = strip_wildcard_basename(p)
    
    p = os.path.join(p, *path_join_list)
    index_start = None if is_self_included else 1
    return glob.glob(p, recursive=True)[index_start:]    

def list_recursively_by_glob(p, is_self_included=True):
    return _glob_recursive(p, ['*'], is_self_included)

def list_folders_recursively_by_glob(p, is_self_included=True):
    return _glob_recursive(p, ['**', ''], is_self_included)

        
def list_subfolders_recursively(p, is_self_included=False):
    # If you typed in a filename, I'll assume it's a directory named so.
    # The internal implementations will choke on the bad input
    p = strip_wildcard_basename(p)
    
    os_name = os.name    
    if os_name == 'nt':
        s = win_list_folders_recursively_in_str(p, is_self_included)
        return s.splitlines()
    elif os_name == 'posix': 
        # All linux-like OS, including Mac, that has find command
        s = posix_list_folders_recursively_in_str(p, is_self_included)
        return s.splitlines()    
    else:
        return list_folders_recursively_by_glob(p, is_self_included)

__all__ = ['list_subfolders_recursively']