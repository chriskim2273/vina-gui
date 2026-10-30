"""Super simple GUI for AutoDock Vina (vina.exe).

Docs grounded in:
- https://autodock-vina.readthedocs.io/en/latest/docking_basic.html
- https://autodock-vina.readthedocs.io/en/latest/installation.html
  (`vina --help` via `./vina_<version>_<OS>_<arch> --help`)

Typical run (from official basic-docking tutorial):
    vina --receptor 1iep_receptor.pdbqt --ligand 1iep_ligand.pdbqt \
        --config 1iep_receptor.box.txt \
        --exhaustiveness=32 --out 1iep_ligand_vina_out.pdbqt

where the config/box file contains:
    center_x = 15.190
    center_y = 53.903
    center_z = 16.917
    size_x = 20.0
    size_y = 20.0
    size_z = 20.0

Defaults used here match Vina: exhaustiveness=8, num_modes=9,
energy_range=3.0, cpu=0 (use all CPUs), seed random when blank.
"""

import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def build_vina_command(
    vina_exe="vina.exe",
    receptor="",
    ligand="",
    out="",
    center_x="0",
    center_y="0",
    center_z="0",
    size_x="20",
    size_y="20",
    size_z="20",
    exhaustiveness="8",
    num_modes="9",
    energy_range="3",
    cpu="0",
    seed="",
    scoring="vina",
    config="",
):
    """Build the vina command list. Pure function (no GUI) so it is testable.

    If a config file is given, Vina reads the box from it
    (center_x/y/z + size_x/y/z), so we still pass explicit box flags
    only when no config is used — matching the official tutorial which
    uses either --config <box.txt> OR explicit --center_* --size_* flags.
    """
    cmd = [vina_exe]
    if receptor:
        cmd += ["--receptor", receptor]
    if ligand:
        cmd += ["--ligand", ligand]
    if config:
        cmd += ["--config", config]
    else:
        if str(center_x) != "":
            cmd += ["--center_x", str(center_x)]
        if str(center_y) != "":
            cmd += ["--center_y", str(center_y)]
        if str(center_z) != "":
            cmd += ["--center_z", str(center_z)]
        if str(size_x) != "":
            cmd += ["--size_x", str(size_x)]
        if str(size_y) != "":
            cmd += ["--size_y", str(size_y)]
        if str(size_z) != "":
            cmd += ["--size_z", str(size_z)]
    if exhaustiveness not in ("", None):
        cmd += ["--exhaustiveness", str(exhaustiveness)]
    if num_modes not in ("", None):
        cmd += ["--num_modes", str(num_modes)]
    if energy_range not in ("", None):
        cmd += ["--energy_range", str(energy_range)]
    if cpu not in ("", None):
        cmd += ["--cpu", str(cpu)]
    if seed not in ("", None) and str(seed).strip() != "":
        cmd += ["--seed", str(seed).strip()]
    if scoring and scoring != "vina":
        cmd += ["--scoring", scoring]
    if out:
        cmd += ["--out", out]
    return cmd


class VinaGui:
    def __init__(self, root):
        self.root = root
        root.title("Vina GUI - super simple")
        root.minsize(560, 620)

        self.entries = {}
        main = ttk.Frame(root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        row = 0
        row = self._file_row(main, row, "vina_exe", "Vina exe:", "vina.exe", False)
        row = self._file_row(main, row, "receptor", "Receptor (.pdbqt):", "", True)
        row = self._file_row(main, row, "ligand", "Ligand (.pdbqt):", "", True)
        row = self._file_row(main, row, "config", "Config/box .txt (optional):", "", True)
        row = self._save_row(main, row, "out", "Output (.pdbqt):", "")

        ttk.Separator(main, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=8)
        row += 1

        # Box + params grid
        defaults = {
            "center_x": "15.190", "center_y": "53.903", "center_z": "16.917",
            "size_x": "20", "size_y": "20", "size_z": "20",
            "exhaustiveness": "8", "num_modes": "9",
            "energy_range": "3", "cpu": "0", "seed": "",
        }
        r = row
        for i, key in enumerate(["center_x", "center_y", "center_z"]):
            ttk.Label(main, text=key + ":").grid(row=r, column=0, sticky="e", padx=4, pady=2)
            e = ttk.Entry(main, width=14)
            e.insert(0, defaults[key])
            e.grid(row=r, column=1, sticky="w", padx=4, pady=2)
            self.entries[key] = e
            r += 1
        for i, key in enumerate(["size_x", "size_y", "size_z"]):
            ttk.Label(main, text=key + ":").grid(row=r - 6 + i, column=2 - 1, sticky="e", padx=4, pady=2) if False else None
        # place sizes in column 2 side-by-side: simpler stacked below
        for key in ["size_x", "size_y", "size_z", "exhaustiveness", "num_modes", "energy_range", "cpu", "seed"]:
            ttk.Label(main, text=key + ":").grid(row=r, column=0, sticky="e", padx=4, pady=2)
            e = ttk.Entry(main, width=14)
            e.insert(0, defaults[key])
            e.grid(row=r, column=1, sticky="w", padx=4, pady=2)
            self.entries[key] = e
            r += 1

        ttk.Label(main, text="scoring:").grid(row=r, column=0, sticky="e", padx=4, pady=2)
        self.scoring = tk.StringVar(value="vina")
        ttk.Combobox(main, textvariable=self.scoring, values=["vina", "ad4", "vinardo"],
                     width=11, state="readonly").grid(row=r, column=1, sticky="w", padx=4, pady=2)
        r += 1

        btns = ttk.Frame(main)
        btns.grid(row=r, column=0, columnspan=3, pady=8)
        ttk.Button(btns, text="Preview command", command=self.preview).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Run Vina", command=self.run).pack(side=tk.LEFT, padx=4)
        r += 1

        self.cmd_label = ttk.Label(main, text="", wraplength=520, foreground="#444")
        self.cmd_label.grid(row=r, column=0, columnspan=3, sticky="w", pady=4)
        r += 1

        self.log = tk.Text(main, height=12, width=70)
        self.log.grid(row=r, column=0, columnspan=3, sticky="nsew", pady=4)
        main.rowconfigure(r, weight=1)

    def _file_row(self, parent, row, key, label, initial, must_exist):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="e", padx=4, pady=2)
        e = ttk.Entry(parent, width=48)
        e.insert(0, initial)
        e.grid(row=row, column=1, sticky="ew", padx=4, pady=2)
        self.entries[key] = e
        def browse():
            if must_exist:
                p = filedialog.askopenfilename()
            else:
                p = filedialog.askopenfilename()
                if not p:
                    return
            if p:
                e.delete(0, tk.END)
                e.insert(0, p)
        ttk.Button(parent, text="Browse...", command=browse).grid(row=row, column=2, padx=4)
        return row + 1

    def _save_row(self, parent, row, key, label, initial):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="e", padx=4, pady=2)
        e = ttk.Entry(parent, width=48)
        e.insert(0, initial)
        e.grid(row=row, column=1, sticky="ew", padx=4, pady=2)
        self.entries[key] = e
        def browse():
            p = filedialog.asksaveasfilename(defaultextension=".pdbqt",
                                             filetypes=[("PDBQT", "*.pdbqt"), ("All files", "*.*")])
            if p:
                e.delete(0, tk.END)
                e.insert(0, p)
        ttk.Button(parent, text="Save as...", command=browse).grid(row=row, column=2, padx=4)
        return row + 1

    def _collect(self):
        g = lambda k: self.entries[k].get().strip()
        return {
            "vina_exe": g("vina_exe") or "vina.exe",
            "receptor": g("receptor"),
            "ligand": g("ligand"),
            "config": g("config"),
            "out": g("out"),
            "center_x": g("center_x"), "center_y": g("center_y"), "center_z": g("center_z"),
            "size_x": g("size_x"), "size_y": g("size_y"), "size_z": g("size_z"),
            "exhaustiveness": g("exhaustiveness"), "num_modes": g("num_modes"),
            "energy_range": g("energy_range"), "cpu": g("cpu"), "seed": g("seed"),
            "scoring": self.scoring.get().strip(),
        }

    def preview(self):
        cmd = build_vina_command(**self._collect())
        self.cmd_label.config(text=" ".join(cmd))
        return cmd

    def run(self):
        vals = self._collect()
        if not vals["receptor"]:
            messagebox.showerror("Missing", "Pick a receptor .pdbqt file.")
            return
        if not vals["ligand"]:
            messagebox.showerror("Missing", "Pick a ligand .pdbqt file.")
            return
        if not vals["out"]:
            messagebox.showerror("Missing", "Pick an output .pdbqt file (Save as...).")
            return
        cmd = build_vina_command(**vals)
        self.cmd_label.config(text=" ".join(cmd))
        self.log.insert(tk.END, "$ " + " ".join(cmd) + "\n")
        self.log.see(tk.END)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            self.log.insert(tk.END, proc.stdout + "\n" + proc.stderr + "\n")
            if proc.returncode == 0:
                self.log.insert(tk.END, f"Done. Wrote {vals['out']}\n")
            else:
                self.log.insert(tk.END, f"Vina exited with code {proc.returncode}\n")
        except FileNotFoundError:
            messagebox.showerror("Not found", f"Could not run {vals['vina_exe']}. Check the Vina exe path.")
        except subprocess.TimeoutExpired:
            messagebox.showerror("Timeout", "Vina run timed out after 1 hour.")
        self.log.see(tk.END)


def main():
    root = tk.Tk()
    VinaGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
