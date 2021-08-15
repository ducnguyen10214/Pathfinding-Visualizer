import cx_Freeze
import os
import sys

executables = [cx_Freeze.Executable("main.py")]

cx_Freeze.setup(
    name="Pathfinding Visualizer",
    options={"build_exe": {"packages":["main"]}},
    executables = executables
)