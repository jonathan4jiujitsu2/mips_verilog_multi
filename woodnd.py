# -*- coding: utf-8 -*-
"""
dump_and_spawn.py  –  must be executed *inside* AEDT (Iron-Python 2.7)
 1) Dumps exact model history to  %USERPROFILE%\Documents
 2) Spawns external CPython extractor and waits
"""

import ScriptEnv
import os, datetime, subprocess, sys

# ─── EDIT ONLY THESE TWO LINES ─────────────────────────────────────────
PYTHON_EXE     = r"C:\Python312\python.exe"               # CPython 3.x path
EXTRACT_SCRIPT = r"C:\Scripts\hfss_extractor_pass2.py"    # external script
# ───────────────────────────────────────────────────────────────────────

# 0 ▪ attach to AEDT, cope with both API variants
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")

try:
    desktop = ScriptEnv.GetDesktop()      # present in most builds
except AttributeError:
    desktop = globals().get("oDesktop")   # older builds expose global
    if desktop is None:
        raise RuntimeError("Cannot obtain Desktop object "
                           "(no ScriptEnv.GetDesktop and no oDesktop)")

project = desktop.GetActiveProject()
if project is None:
    raise RuntimeError("No active project")
design  = project.GetActiveDesign()
if design is None:
    raise RuntimeError("No active design")

# 1 ▪ dump history
history = design.GetModelHistory()
stamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
hist_name = "HFSS_History_{0}_{1}_{2}.vbs".format(
               project.GetName(), design.GetName(), stamp)
out_dir   = os.path.join(os.path.expanduser("~"), "Documents")
hist_path = os.path.join(out_dir, hist_name)

with open(hist_path, "w") as f:
    f.write(history)
print("✓ History written:", hist_path)

# 2 ▪ spawn external extractor
cmd = '"{0}" "{1}" --history "{2}"'.format(PYTHON_EXE, EXTRACT_SCRIPT, hist_path)
print("▶ Launching:", cmd)
ret = subprocess.call(cmd, shell=True)
if ret != 0:
    print("⚠ External extractor returned code", ret)
else:
    print("✓ External extraction finished.")