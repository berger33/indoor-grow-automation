# Copyright 2014-present PlatformIO <contact@platformio.org>
# Licensed under the Apache License, Version 2.0.
"""Builder oficial da plataforma Native 1.2.1, preservado para build offline."""

from SCons.Script import COMMAND_LINE_TARGETS, AlwaysBuild, Default, DefaultEnvironment

env = DefaultEnvironment()

for key in ("CC", "CXX"):
    if key in env:
        del env[key]

backup_cflags = env.get("CFLAGS", [])
backup_cxxflags = env.get("CXXFLAGS", [])
env.Tool("gcc")
env.Tool("g++")
if "compiledb" in COMMAND_LINE_TARGETS:
    env.Tool("compilation_db")
env.Append(CFLAGS=backup_cflags, CXXFLAGS=backup_cxxflags)

target_bin = env.BuildProgram()
exec_action = env.VerboseAction("$SOURCE $PROGRAM_ARGS", "Executing $SOURCE")
AlwaysBuild(env.Alias("exec", target_bin, exec_action))
AlwaysBuild(env.Alias("upload", target_bin, exec_action))
target_size = env.Alias(
    "size", target_bin, env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE")
)
AlwaysBuild(target_size)
Default([target_bin])
