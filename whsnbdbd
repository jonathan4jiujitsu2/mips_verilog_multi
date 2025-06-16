# -*- coding: utf-8 -*-
"""
dump_and_spawn.py  –  Iron-Python 2.7 macro
 1) Saves the complete model history to %USERPROFILE%\Documents
 2) Starts the external CPython extractor and waits for it to finish
Edit only PYTHON_EXE and EXTRACT_SCRIPT below.
"""

import ScriptEnv
import os, datetime, subprocess

# ─── EDIT THESE TWO PATHS ───────────────────────────────────────────────
PYTHON_EXE     = r"C:\Python312\python.exe"               # CPython 3.x
EXTRACT_SCRIPT = r"C:\Scripts\hfss_extractor_pass2.py"    # external extractor
# ────────────────────────────────────────────────────────────────────────

# ▪ attach to running AEDT
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
try:
    desktop = ScriptEnv.GetDesktop()          # most builds
except AttributeError:
    desktop = globals().get("oDesktop")       # older builds
    if desktop is None:
        raise RuntimeError("Cannot obtain Desktop object")

project = desktop.GetActiveProject()
if project is None:
    raise RuntimeError("No active project")
design  = project.GetActiveDesign()
if design is None:
    raise RuntimeError("No active design")

# ▪ robust history grab
oEditor       = design.SetActiveEditor("3D Modeler")
history_text  = None

# 1) newest API
try:
    history_text = design.GetModelHistory()
    print("• history via design.GetModelHistory()")
except AttributeError:
    pass

# 2) editor API (present in every release)
if not history_text:
    try:
        history_text = oEditor.GetHistory()
        print("• history via oEditor.GetHistory()")
    except AttributeError:
        pass

# 3) stitch each operation
if not history_text:
    print("• stitching history manually (every operation)")
    lines = []
    op_names = (oEditor.GetOperationNames()
                if hasattr(oEditor, "GetOperationNames") else [])
    for op in op_names:
        try:
            lines.append(oEditor.GetScriptForOp(op))
        except Exception:
            pass
    history_text = "\n".join(lines)

if not history_text:
    raise RuntimeError("Could not retrieve model history by any method")

# ▪ write history file
stamp     = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
hist_name = "HFSS_History_{0}_{1}_{2}.vbs".format(
               project.GetName(), design.GetName(), stamp)
hist_path = os.path.join(os.path.expanduser("~\\Documents"), hist_name)
with open(hist_path, "w") as f:
    f.write(history_text)
print("✓ History written:", hist_path)

# ▪ launch external extractor
cmd = '"{0}" "{1}" --history "{2}"'.format(PYTHON_EXE, EXTRACT_SCRIPT, hist_path)
print("▶ Launching:", cmd)
ret = subprocess.call(cmd, shell=True)
if ret:
    print("⚠ External extractor exited with code", ret)
else:
    print("✓ External extraction finished.")