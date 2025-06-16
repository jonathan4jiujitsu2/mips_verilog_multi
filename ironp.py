# -*- coding: utf-8 -*-
"""
Run INSIDE AEDT (Iron-Python 2.7).
1) Writes exact model-history script to %USERPROFILE%\Documents
2) Spawns external extractor (CPython) and passes history path
"""

import ScriptEnv
import os
import datetime
import subprocess

# ----- EDIT THESE TWO LINES ---------------------------------
PYTHON_EXE     = r"C:\Python312\python.exe"                 # CPython 3.x
EXTRACT_SCRIPT = r"C:\Scripts\hfss_extractor_pass2.py"      # pass-2 extractor
# ------------------------------------------------------------

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
desktop = ScriptEnv.GetDesktop()
project = desktop.GetActiveProject()
design  = project.GetActiveDesign()

# 1 ▪ dump history
hist_text = design.GetModelHistory()
stamp     = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
hist_name = "HFSS_History_{0}_{1}_{2}.vbs".format(
                project.GetName(), design.GetName(), stamp)
hist_path = os.path.join(os.path.expanduser("~\\Documents"), hist_name)

with open(hist_path, "w") as f:
    f.write(hist_text)

print("History written:", hist_path)

# 2 ▪ launch external extractor
cmd = '"{0}" "{1}" --history "{2}"'.format(PYTHON_EXE, EXTRACT_SCRIPT, hist_path)
print("Launching:", cmd)
subprocess.call(cmd, shell=True)

print("✓ External extraction finished.")