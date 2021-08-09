import cx_Freeze

executables = [cx_Freeze.Executable("main.py")]

cx_Freeze.setup(
    name="A* Pathfinding Visualizer",
    options={"build_exe": {"packages":["pygame"]}},
    executables = executables
)