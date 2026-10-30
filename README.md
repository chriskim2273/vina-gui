# Vina GUI (super simple)

Tiny Tkinter GUI for `vina.exe` (AutoDock Vina).

## Run (Windows)

```bat
python vina_gui.py
```

No extra packages needed — Tkinter ships with Python on Windows.
If Tkinter is missing on Linux: `sudo apt install python3-tk`.

On this machine a project-local env is already set up (Tk lives in
`.venv/lib` + `.venv/share`), so run it from the project dir as:

```bash
source .venv/bin/activate
LD_LIBRARY_PATH=$PWD/.venv/lib \
TK_LIBRARY=$PWD/.venv/share/tcltk/tk8.6 \
TCL_LIBRARY=/usr/share/tcltk/tcl8.6 \
python vina_gui.py
```

## What it does

- File picker for Vina exe (`vina.exe`)
- File pickers for receptor `.pdbqt` and ligand `.pdbqt`
- Save-as picker for output `.pdbqt`
- Optional config/box `.txt` picker (the `center_x = ...` file from the official tutorial)
- Inputs for `center_x/y/z`, `size_x/y/z`, `exhaustiveness` (default 8),
  `num_modes` (default 9), `energy_range` (default 3), `cpu` (default 0 = all),
  `seed` (blank = random), `scoring` (vina / ad4 / vinardo)
- Preview of the exact command + Run button with log output

Example command it builds (matches the
[official basic-docking tutorial](https://autodock-vina.readthedocs.io/en/latest/docking_basic.html)):

```text
vina.exe --receptor 1iep_receptor.pdbqt --ligand 1iep_ligand.pdbqt --center_x 15.190 --center_y 53.903 --center_z 16.917 --size_x 20 --size_y 20 --size_z 20 --exhaustiveness 32 --out 1iep_ligand_vina_out.pdbqt
```

Or with a box file:

```text
vina.exe --receptor 1iep_receptor.pdbqt --ligand 1iep_ligand.pdbqt --config 1iep_receptor.box.txt --exhaustiveness 32 --out 1iep_ligand_vina_out.pdbqt
```
