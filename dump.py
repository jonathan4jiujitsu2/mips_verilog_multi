# dump_and_spawn.py   –  RUN **INSIDE** AEDT
# --------------------------------------------------------
# 1. In AEDT: Tools ▸ Run Script…  (or oDesktop.AddScript)
# 2. It writes the model history to %USERPROFILE%\Documents
# 3. It starts the external extractor below and waits
# --------------------------------------------------------
import ScriptEnv, os, datetime, subprocess

# ►  UPDATE THESE TWO PATHS ◄
PYTHON_EXE      = r"C:\Python312\python.exe"          # CPython 3.x
EXTRACT_SCRIPT  = r"C:\Scripts\hfss_extractor_pass2.py"

# initialise AEDT COM context
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
desktop = ScriptEnv.GetDesktop()
project = desktop.GetActiveProject()
design  = project.GetActiveDesign()

# export history
hist_text = design.GetModelHistory()
stamp     = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
hist_name = f"HFSS_History_{project.GetName()}_{design.GetName()}_{stamp}.vbs"
hist_path = os.path.join(os.path.expanduser("~\\Documents"), hist_name)
with open(hist_path, "w") as f:
    f.write(hist_text)
print("✓ History script written:", hist_path)

# launch external extractor
cmd = f'"{PYTHON_EXE}" "{EXTRACT_SCRIPT}" -hist "{hist_path}"'
print("▶ Launching:", cmd)
subprocess.call(cmd, shell=True)

print("✓ External extraction finished.")