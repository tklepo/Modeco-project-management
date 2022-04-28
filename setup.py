import cx_Freeze
import sys


base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [cx_Freeze.Executable("Main.py", base=base)]

cx_Freeze.setup(
    name='Modeco-project_management',
    options={"build_exe": {"packages": ["tkinter", "reportlab", "sqlite3", "tkcalendar"],
                           "include_files": ["modeco_logo1x.png",
                                             "baza_pm.db", "C:\Python34/DLLs/tcl86t.dll",
                                             "C:\Python34/DLLs/tk86t.dll"]}},
    version="0.01",
    description="Modeco project management",
    executables=executables
)
