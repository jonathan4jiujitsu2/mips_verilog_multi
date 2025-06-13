# ───────────── 5 ▪ analysis setups ────────────── #
existing_setups = {s.name: s for s in hfss.setups}

for s_name, s in dump["analysis_setups"].items():
    if s_name in existing_setups:
        stp = existing_setups[s_name]                 # reuse
    else:
        stp = hfss.create_setup(s_name, s["props"])   # create
        if stp is False:                              # PyAEDT returns False on failure
            print(f"⚠  setup {s_name}: creation failed — skipped its sweeps")
            continue

    # add sweeps if the object supports it
    if hasattr(stp, "add_sweep"):
        for sw_name, sw_props in s["sweeps"].items():
            stp.add_sweep(sw_name, sw_props)
    else:
        print(f"⚠  setup {s_name}: object has no add_sweep()")