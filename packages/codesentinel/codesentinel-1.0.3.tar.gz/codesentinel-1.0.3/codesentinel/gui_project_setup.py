#!/usr/bin/env python3
"""
CodeSentinel Project Setup Wizard (GUI)

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

A simple, dependable project setup wizard that helps you:
- Pick a project directory
- Detect Git and optionally initialize it
- Create a starter codesentinel.json configuration

This is intentionally minimal but functional; it can be extended with
additional steps (alerts, IDE integration, GitHub linking) later.
"""

from __future__ import annotations

import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional

from .utils.config import ConfigManager


class ProjectSetupWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CodeSentinel Project Setup")
        self.root.geometry("800x500")
        self.root.resizable(True, True)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"800x500+{x}+{y}")

        self.project_dir = tk.StringVar(value=str(Path.cwd()))
        self.git_status = tk.StringVar(value="Unknown")

        self._build_ui()
        self._update_git_status()

    def _build_ui(self):
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=16, pady=16)
        ttk.Label(header, text="CodeSentinel Project Setup Wizard", font=("Segoe UI", 16, "bold")).pack()
        ttk.Label(header, text="Guided configuration for a new or existing project.", foreground="gray").pack(pady=(4, 0))

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Project directory selection
        dir_frame = ttk.LabelFrame(main, text="Project Directory", padding=12)
        dir_frame.pack(fill="x")
        dir_row = ttk.Frame(dir_frame)
        dir_row.pack(fill="x")
        ttk.Entry(dir_row, textvariable=self.project_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(dir_row, text="Browse...", command=self._choose_directory).pack(side="left", padx=(8, 0))
        ttk.Label(dir_frame, textvariable=self.git_status, foreground="gray").pack(anchor="w", pady=(6, 0))

        # Actions
        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(12, 0))
        self.init_git_btn = ttk.Button(actions, text="Initialize Git", command=self._init_git)
        self.init_git_btn.pack(side="left")
        ttk.Button(actions, text="Create Config", command=self._create_config).pack(side="left", padx=(8, 0))

        # Footer
        footer = ttk.Frame(self.root)
        footer.pack(fill="x", padx=16, pady=16)
        ttk.Button(footer, text="Close", command=self.root.destroy).pack(side="right")
        ttk.Button(footer, text="Finish", command=self._finish).pack(side="right", padx=(0, 8))

    def _choose_directory(self):
        selected = filedialog.askdirectory(initialdir=self.project_dir.get() or str(Path.home()))
        if selected:
            self.project_dir.set(selected)
            self._update_git_status()

    def _update_git_status(self):
        path = Path(self.project_dir.get())
        is_git = (path / ".git").exists()
        if is_git:
            self.git_status.set("✓ Git repository detected")
            self.init_git_btn.state(["disabled"])  # disable init if already a repo
        else:
            self.git_status.set("Not a Git repository")
            self.init_git_btn.state(["!disabled"])  # enable

    def _init_git(self):
        path = Path(self.project_dir.get())
        try:
            result = subprocess.run(["git", "init"], cwd=str(path), capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Git", "Repository initialized successfully.")
            else:
                messagebox.showwarning("Git", f"Git init failed:\n{result.stderr.strip()}")
        except FileNotFoundError:
            messagebox.showwarning("Git", "Git is not installed or not on PATH.")
        finally:
            self._update_git_status()

    def _create_config(self):
        path = Path(self.project_dir.get())
        cfg_path = path / "codesentinel.json"
        try:
            cm = ConfigManager(config_path=cfg_path)
            # Start from defaults and set a couple of basic fields
            cfg = cm._create_default_config()
            cfg["project_dir"] = str(path)
            cm.save_config(cfg)
            messagebox.showinfo("Configuration", f"Created {cfg_path}")
        except Exception as e:
            messagebox.showerror("Configuration", f"Failed to create config:\n{e}")

    def _finish(self):
        # Ensure a config exists; if not, create a default one silently
        path = Path(self.project_dir.get())
        cfg_path = path / "codesentinel.json"
        if not cfg_path.exists():
            try:
                cm = ConfigManager(config_path=cfg_path)
                cm.save_config(cm._create_default_config())
            except Exception:
                pass
        messagebox.showinfo("Setup Complete", "CodeSentinel project setup is complete. You can now run 'codesentinel' or enable scheduled maintenance.")
        self.root.destroy()


def main():
    app = ProjectSetupWizard()
    app.root.mainloop()


if __name__ == "__main__":
    main()
