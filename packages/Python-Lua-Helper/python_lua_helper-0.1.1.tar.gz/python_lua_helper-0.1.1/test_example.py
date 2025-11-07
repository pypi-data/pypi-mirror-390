#!/usr/bin/env python3

import os
import sys
from py_lua_helper import PyLuaHelper

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

print("example.py: creating PyLuaHelper instance")

# Create PyLuaHelper instance with same parameters as example.bash
cfg = PyLuaHelper(
    lua_config_script=os.path.join(script_dir, "test_example", "example.cfg.lua"),
    export_vars=["config.sub", "config.paths", "config.empty", "wrong.table", "empty"],
    extra_strings=["test1", "test2"],
    pre_script=os.path.join(script_dir, "test_example", "example.pre.lua"),
    post_script=os.path.join(script_dir, "test_example", "example.post.lua"),
    work_dir=script_dir,
    lua_args=sys.argv[1:]
)

print("example.py: PyLuaHelper complete")
print(f"example.py: my own cmdline params={sys.argv[1:]}")
print("")
print("example.py: names of all global variables exported from lua script:")
print(cfg.keys())
print("")

# Check variable availability
print("example.py: check for config.empty variable availability is ", end="")
try:
    if "config.empty" in cfg:
        print("passed, but should fail !!!")
    else:
        print("failed, as expected")
except Exception:
    print("failed, as expected")

print("example.py: check for wrong.table variable availability is ", end="")
try:
    if "wrong.table" in cfg:
        print("passed, but should fail !!!")
    else:
        print("failed, as expected")
except Exception:
    print("failed, as expected")

print("example.py: check for empty variable availability is ", end="")
try:
    if "empty" in cfg:
        print("passed, but should fail !!!")
    else:
        print("failed, as expected")
except Exception:
    print("failed, as expected")

print("example.py: check for config.value variable availability is ", end="")
try:
    if "config.value" in cfg:
        print("passed, but should fail !!!")
    else:
        print("failed, as expected")
except Exception:
    print("failed, as expected")

print("example.py: check for config.sub.string variable availability is ", end="")
try:
    if "config.sub.string" in cfg:
        print("passed, as expected")
    else:
        print("failed, but should pass !!!")
except Exception:
    print("failed, but should pass !!!")

print("example.py: check for config.sub variable availability is ", end="")
try:
    if "config.sub" in cfg:
        print("passed, as expected")
    else:
        print("failed, but should pass !!!")
except Exception:
    print("failed, but should pass !!!")

print(f"example.py: config.value is not selected for export, so cfg['config.value'] = {cfg.get('config.value', 'NOT_FOUND')}")
print(f"example.py: config.empty is not found in lua config file, so cfg['config.empty'] = {cfg.get('config.empty', 'NOT_FOUND')}")
print(f"example.py: cfg['config.paths.tempdir'] = {cfg.get('config.paths.tempdir', 'NOT_FOUND')}")
print(f"example.py: cfg['config.paths.workdir'] = {cfg.get('config.paths.workdir', 'NOT_FOUND')}")
print(f"example.py: cfg['config.paths.dynpath'] = {cfg.get('config.paths.dynpath', 'NOT_FOUND')}")
print(f"example.py: cfg['config.paths.tempdir_raw'] = {cfg.get('config.paths.tempdir_raw', 'NOT_FOUND')}")
print(f"example.py: cfg['config.paths.workdir_raw'] = {cfg.get('config.paths.workdir_raw', 'NOT_FOUND')}")
print(f"example.py: cfg['config.paths.dynpath_raw'] = {cfg.get('config.paths.dynpath_raw', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.lua_v1'] = {cfg.get('config.sub.lua_v1', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.lua_v2'] = {cfg.get('config.sub.lua_v2', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.lua_v3'] = {cfg.get('config.sub.lua_v3', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.lua_num'] = {cfg.get('config.sub.lua_num', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.extra_1'] = {cfg.get('config.sub.extra_1', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.extra_2'] = {cfg.get('config.sub.extra_2', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.number1'] = {cfg.get('config.sub.number1', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.string'] = {cfg.get('config.sub.string', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.problematic_string'] = {cfg.get('config.sub.problematic_string', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.non_latin_string'] = {cfg.get('config.sub.non_latin_string', 'NOT_FOUND')}")
print(f"example.py: (should be empty regardless of fallback value, because it is a container: cfg['config.sub.sub']) = {cfg.get('config.sub.sub', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.sub'] as int with fallback value -1) = {cfg.get_int('config.sub.sub',-1)}")
print(f"example.py: cfg['config.sub.sub'] as int with fallback value -1.6) = {cfg.get_int('config.sub.sub',-1.6)}")
print(f"example.py: cfg['config.sub.sub'] as float with fallback value -1.5) = {cfg.get_float('config.sub.sub',-1.5)}")
print(f"example.py: cfg['config.sub.sub.message'] = {cfg.get('config.sub.sub.message', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.sub.message2'] = {cfg.get('config.sub.sub.message2', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.multiline_string'] = {cfg.get('config.sub.multiline_string', 'NOT_FOUND')}")

# Test mixed table access (indexed and named elements)
print(f"example.py: table start for config.sub.mixed: {cfg.get_table_start('config.sub.mixed')}")
print(f"example.py: table end for config.sub.mixed: {cfg.get_table_end('config.sub.mixed')}")
print(f"example.py: table indices sequence for config.sub.mixed: {cfg.get_table_seq('config.sub.mixed')}")
print(f"example.py: cfg['config.sub.mixed.1'] = {cfg.get('config.sub.mixed.1', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.mixed.2'] = {cfg.get('config.sub.mixed.2', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.mixed.3'] = {cfg.get('config.sub.mixed.3', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.mixed.4'] = {cfg.get('config.sub.mixed.4', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.mixed.key'] = {cfg.get('config.sub.mixed.key', 'NOT_FOUND')}")

# Show extra cmdline parameters passed to lua script as loader.args table and assigned to config.sub.loader_args
print(f"example.py: config.sub.loader_args indices sequence: {cfg.get_table_seq('config.sub.loader_args')}")
for i in cfg.get_table_seq('config.sub.loader_args'):
    print(f"example.py: cfg['config.sub.loader_args.{i}'] = {cfg.get(f'config.sub.loader_args.{i}', 'NOT_FOUND')}")
