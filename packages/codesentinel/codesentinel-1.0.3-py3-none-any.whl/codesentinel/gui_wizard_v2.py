#!/usr/bin/env python3
"""
CodeSentinel Setup Wizard (Modular, Minimal)

A compact, secure-first, multi-step GUI wizard that ports the tested legacy
features in a clean architecture:

- Welcome (auto-starting flow)
- Install Location with smart Git repo detection
- Alerts (console/file/email/slack) with compact layout
- GitHub Integration options (init/clone/connect) — configuration only
- IDE Detection (8 popular IDEs) with guidance
- Optional Features (scheduler, git hooks, CI templates)
- Summary + Save (writes codesentinel.json)

This wizard intentionally avoids side effects beyond config writes and simple
git init; integration steps that require credentials or network calls are
captured as configuration for follow-up commands handled by the CLI.
"""

from __future__ import annotations

import glob
import os
import shutil
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Tuple, Callable

from .utils.config import ConfigManager
from . import __version__ as CS_VERSION


class ScrollableFrame(ttk.Frame):
    """Scrollable frame with optional content centering."""
    def __init__(self, master, center_content=False, max_width=700, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.center_content = center_content
        self.max_width = max_width
        
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg='white')
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        if center_content:
            # Container for centered content
            container = ttk.Frame(canvas)
            self.inner = ttk.Frame(container)
            self.inner.pack(padx=20, pady=20)
            canvas.create_window((0, 0), window=container, anchor="n", width=max_width)
            
            def _on_configure(event):
                # Center the content horizontally
                canvas_width = canvas.winfo_width()
                x_position = max(0, (canvas_width - max_width) // 2)
                canvas.coords(canvas.find_withtag("all")[0], x_position, 0)
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            canvas.bind("<Configure>", _on_configure)
            container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        else:
            # Standard layout
            self.inner = ttk.Frame(canvas)
            self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=self.inner, anchor="nw")
        
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)


class WizardApp:
    WIDTH, HEIGHT = 900, 750

    def __init__(self):
        self.root = tk.Tk()
        # Window title shows product name and version only
        self.root.title(f"CodeSentinel Setup Wizard v{CS_VERSION}")
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.root.resizable(True, True)
        self._center()

        # Style configuration (legacy-inspired)
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Step.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Section.TLabel', font=('Arial', 11, 'bold'))
        
        # Color scheme for status indicators
        self.colors = {
            'success': '#2e7d32',  # green
            'error': '#d32f2f',    # red
            'warning': '#f57c00',  # orange
            'info': '#0366d6',     # blue
            'processing': '#1976d2', # darker blue
            'disabled': '#9e9e9e'  # gray
        }

        self.data: Dict[str, Any] = {
            "install_location": str(Path.cwd()),
            "alerts": {
                "console": {"enabled": True},
                "file": {"enabled": True, "log_file": "codesentinel.log"},
                "email": {"enabled": False, "smtp_server": "", "smtp_port": 587, "username": "", "password": "", "from_email": "", "to_emails": []},
                "slack": {"enabled": False, "webhook_url": "", "channel": "#maintenance-alerts"},
            },
            "github": {"mode": "connect", "repo_url": "", "create": False},
            "ide": {},
            "copilot": {"enabled": False, "install_vscode_extension": False, "generate_instructions": True, "enable_agent_mode": True},
            "optional": {"scheduler": False, "git_hooks": True, "ci": False},
        }
        
        # Validation states
        self.validations = {
            'email': False,
            'slack': False,
            'github': False
        }

        self.steps: List[Tuple[str, Callable[[], ttk.Frame]]] = []
        self._active_frame: ttk.Frame | None = None
        self._build_ui()
        self._build_steps()
        self._show_step(0)

    # ---- window layout ----
    def _center(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.HEIGHT // 2)
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

    def _build_ui(self):
        # Header with title
        self.header = ttk.Frame(self.root)
        self.header.pack(fill="x", padx=20, pady=(16, 8))
        ttk.Label(self.header, text="CodeSentinel Setup Wizard", style='Title.TLabel').pack()
        ttk.Label(self.header, text="SECURITY > EFFICIENCY > MINIMALISM", font=('Arial', 9), foreground=self.colors['info']).pack(pady=(2, 0))
        # Subtle attribution and version line
        ttk.Label(
            self.header,
            text=f"by Polymath • v{CS_VERSION}",
            font=('Arial', 8),
            foreground='#666666'
        ).pack(pady=(2, 0))
        
        # Progress bar
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill="x", padx=20, pady=(0, 8))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=8)
        self.progress_bar.pack(fill="x")
        
        # Step indicator
        self.step_label = ttk.Label(self.root, text="", style='Step.TLabel')
        self.step_label.pack(padx=20, pady=(8, 12))

        # Body (scrollable content area)
        self.body = ttk.Frame(self.root)
        self.body.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        # Footer with navigation
        self.footer = ttk.Frame(self.root)
        self.footer.pack(fill="x", padx=20, pady=16)
        
        # Cancel button on the left
        self.cancel_btn = ttk.Button(self.footer, text="Cancel", command=self.root.destroy)
        self.cancel_btn.pack(side="left")
        
        # Back and Next buttons side by side on the right
        self.next_btn = ttk.Button(self.footer, text="Next →", command=self._next)
        self.next_btn.pack(side="right")
        
        self.back_btn = ttk.Button(self.footer, text="← Back", command=self._back)
        self.back_btn.pack(side="right", padx=(0, 8))
        
        # Bottom margin branding (suppressed on summary step)
        self.bottom_margin = ttk.Frame(self.root)
        self.bottom_margin.pack(fill="x", padx=20, pady=(0, 8))
        self.bottom_brand = ttk.Label(
            self.bottom_margin,
            text="",
            font=('Arial', 7),
            foreground='#999999'
        )
        self.bottom_brand.pack(anchor="center")

    def _clear_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    def _show_step(self, idx: int):
        self.current = idx
        self._clear_body()
        title, builder = self.steps[idx]
        
        # Update progress indicators
        self.progress_var.set(idx + 1)
        self.step_label.config(text=f"Step {idx + 1} of {len(self.steps)}: {title}")
        
        # Build step content - skip adding title label for Welcome page
        if idx != 0:  # Don't add extra title for Welcome page
            ttk.Label(self.body, text=title, style='Section.TLabel', foreground=self.colors['info']).pack(anchor="w", pady=(0, 12))
        
        self._active_frame = builder()
        self._active_frame.pack(fill="both", expand=True)
        
        # Update navigation buttons
        self.back_btn.state(["!disabled"] if idx > 0 else ["disabled"])
        is_last = idx == len(self.steps) - 1
        self.next_btn.config(text="Finish" if is_last else "Next →")

        # Update bottom branding visibility
        if is_last:
            self.bottom_brand.config(text="")
        else:
            self.bottom_brand.config(text="joediggidyyy")
        
        # Update navigation state after UI is ready
        self.root.after(50, self._update_nav_state)

    def _next(self):
        # Collect data from current step
        frame = self._active_frame
        if frame is not None and hasattr(frame, "collect"):
            if frame.collect() is False:  # type: ignore[attr-defined]
                return
        
        # Check validation requirements before proceeding
        if not self._check_nav_lock():
            return
        
        if self.current == len(self.steps) - 1:
            self._save_and_finish()
            return
        self._show_step(self.current + 1)
    
    def _check_nav_lock(self) -> bool:
        """Check if navigation should be locked due to required validations."""
        # Step 2 (Project Setup) - check GitHub
        if self.current == 1:
            if hasattr(self, 'github_enabled_var') and self.github_enabled_var.get():
                if not self.validations.get('github', False):
                    messagebox.showwarning("Validation Required",
                                         "Please validate GitHub connection before proceeding,\n"
                                         "or disable GitHub integration.")
                    return False
        
        # Step 3 (Alert Preferences) - check email/slack
        if self.current == 2:
            if hasattr(self, 'email_var') and self.email_var.get():
                if not self.validations.get('email', False):
                    messagebox.showwarning("Validation Required", 
                                         "Please test and validate email configuration before proceeding,\n"
                                         "or uncheck the email option.")
                    return False
            
            if hasattr(self, 'slack_var') and self.slack_var.get():
                if not self.validations.get('slack', False):
                    messagebox.showwarning("Validation Required",
                                         "Please test and validate Slack configuration before proceeding,\n"
                                         "or uncheck the Slack option.")
                    return False
        
        return True
    
    def _update_nav_state(self):
        """Update navigation button states based on validation requirements."""
        if self.current == 1:  # Project Setup step (GitHub)
            # Check if GitHub validation is needed
            github_needs_validation = (hasattr(self, 'github_enabled_var') and self.github_enabled_var.get() and 
                                      not self.validations.get('github', False))
            
            if github_needs_validation:
                self.next_btn.config(state="disabled")
                self.next_btn.config(text="⚠️ Validate GitHub →")
            else:
                self.next_btn.config(state="normal")
                self.next_btn.config(text="Next →")
        
        elif self.current == 2:  # Alert step
            # Check if validation is needed
            email_needs_validation = (hasattr(self, 'email_var') and self.email_var.get() and 
                                     not self.validations.get('email', False))
            slack_needs_validation = (hasattr(self, 'slack_var') and self.slack_var.get() and 
                                     not self.validations.get('slack', False))
            
            if email_needs_validation or slack_needs_validation:
                self.next_btn.config(state="disabled")
                if email_needs_validation:
                    self.next_btn.config(text="⚠️ Validate Email")
                elif slack_needs_validation:
                    self.next_btn.config(text="⚠️ Validate Slack")
            else:
                self.next_btn.config(state="normal", text="Next →")
        
        else:
            # Normal navigation for other steps
            is_last = self.current == len(self.steps) - 1
            self.next_btn.config(state="normal", text="Finish" if is_last else "Next →")

    def _back(self):
        if self.current > 0:
            self._show_step(self.current - 1)

    # ---- step builders ----
    def _build_steps(self):
        self.steps = [
            ("Welcome", self._step_welcome),
            ("Project Setup", self._step_location),
            ("Alert Preferences", self._step_alerts),
            ("IDE Integration", self._step_ide),
            ("GitHub Copilot Integration", self._step_copilot),
            ("Optional Features", self._step_optional),
            ("Summary", self._step_summary),
        ]

    def _step_welcome(self):
        # Use regular Frame instead of ScrollableFrame for Welcome page
        f = ttk.Frame(self.body)
        
        # Compact welcome header
        ttk.Label(f, text="Welcome to CodeSentinel! This wizard will guide you through project setup and configuration.", 
                 font=('Arial', 9), justify="left", foreground="#333333", wraplength=850).pack(
                     anchor="w", pady=(0, 10))
        
        # Two-column layout
        columns_container = ttk.Frame(f)
        columns_container.pack(fill="both", expand=True)
        
        # Left column
        left_column = ttk.Frame(columns_container)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 6))
        
        # Installation Progress
        progress_frame = ttk.LabelFrame(left_column, text="⚙️ Installation Progress", padding=10)
        progress_frame.pack(fill="both", expand=True, pady=(0, 6))
        
        self.install_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.install_progress.pack(fill="x", pady=(0, 4))
        self.install_progress['value'] = 100
        
        ttk.Label(progress_frame, text="✓ Installation complete!", 
                 font=('Arial', 9, 'bold'), foreground=self.colors['success']).pack(anchor="w", pady=(0, 4))
        
        ttk.Label(progress_frame, text="Available commands:\n  codesentinel-setup  - Setup wizard\n  codesentinel        - Main CLI\n  codesentinel !!!!   - Audit mode", 
                 font=('Courier New', 8), justify="left", foreground="#424242").pack(anchor="w")
        
        # What CodeSentinel Provides
        provides_frame = ttk.LabelFrame(left_column, text="🛡️ What CodeSentinel Provides", padding=10)
        provides_frame.pack(fill="both", expand=True, pady=(6, 0))
        
        features_text = "• Automated security monitoring\n• Multi-channel alert system\n• GitHub & Copilot AI integration\n• IDE integration support\n• Intelligent audit with '!!!!' command\n• Non-destructive automation"
        ttk.Label(provides_frame, text=features_text, font=('Arial', 9), 
                 justify="left", foreground="#333333").pack(anchor="w")
        
        # Right column
        right_column = ttk.Frame(columns_container)
        right_column.pack(side="left", fill="both", expand=True, padx=(6, 0))
        
        # Environment Information
        env_frame = ttk.LabelFrame(right_column, text="📂 Environment Information", padding=10)
        env_frame.pack(fill="both", expand=True, pady=(0, 6))
        
        current_dir = Path.cwd()
        install_loc = self.data.get("install_location", str(current_dir))
        is_git_repo = (current_dir / ".git").exists()
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        env_items = [
            ("Current Directory:", str(current_dir)),
            ("Install Location:", install_loc),
            ("Git Repository:", "✓ Detected" if is_git_repo else "Not detected"),
            ("Mode:", "Repository Integration" if is_git_repo else "Standalone"),
            ("Python Version:", python_version),
        ]
        
        for label, value in env_items:
            item_frame = ttk.Frame(env_frame)
            item_frame.pack(fill="x", pady=1)
            ttk.Label(item_frame, text=label, font=('Arial', 9, 'bold'), 
                     width=18).pack(side="left", anchor="w")
            color = self.colors['success'] if "✓" in value else "#424242"
            ttk.Label(item_frame, text=value, font=('Arial', 9), 
                     foreground=color, wraplength=350).pack(side="left", anchor="w", fill="x", expand=True)
        
        # Getting Started
        start_frame = ttk.LabelFrame(right_column, text="🚀 Getting Started", padding=10)
        start_frame.pack(fill="both", expand=True, pady=(6, 0))
        
        start_text = "This wizard will help you configure:\n\n1. Project location and GitHub setup\n2. Alert channel preferences\n3. IDE integration options\n4. GitHub Copilot integration\n5. Optional automation features\n\nClick 'Next' to begin configuration."
        
        ttk.Label(start_frame, text=start_text, font=('Arial', 9), 
                 justify="left", foreground="#333333").pack(anchor="w")

        # Repository link (clickable)
        repo_url = "https://github.com/joediggidy/CodeSentinel"
        link = ttk.Label(start_frame, text="View repository on GitHub", foreground=self.colors['info'], cursor="hand2")
        link.pack(anchor="w", pady=(8, 0))
        link.bind("<Button-1>", lambda e, url=repo_url: webbrowser.open_new(url))
        
        return f

    def _step_location(self):
        """Combined Installation Location and GitHub Integration step."""
        f = ttk.Frame(self.body)
        
        # Compact header
        ttk.Label(f, text="Configure your installation location and GitHub integration.", 
                 font=('Arial', 9), foreground='gray').pack(anchor="w", pady=(0, 10))
        
        # Two-column layout
        columns_container = ttk.Frame(f)
        columns_container.pack(fill="both", expand=True)
        
        # Left column - Installation Location
        left_column = ttk.Frame(columns_container)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 6))
        
        location_frame = ttk.LabelFrame(left_column, text="📂 Installation Location", padding=10)
        location_frame.pack(fill="both", expand=True)
        
        self.loc_var = tk.StringVar(value=self.data["install_location"])
        
        # Install location entry
        ttk.Label(location_frame, text="Install location (project root):", 
                 font=('Arial', 9)).pack(anchor="w", pady=(0, 4))
        
        entry_row = ttk.Frame(location_frame)
        entry_row.pack(fill="x", pady=(0, 8))
        ttk.Entry(entry_row, textvariable=self.loc_var, font=('Arial', 9)).pack(side="left", fill="x", expand=True)
        ttk.Button(entry_row, text="Browse...", command=self._browse_location).pack(side="left", padx=(8, 0))
        
        # Detected repositories section
        detected_repos = self._detect_git_repos()
        if detected_repos:
            ttk.Label(location_frame, text="Detected Git Repositories:", 
                     font=('Arial', 9, 'bold')).pack(anchor="w", pady=(8, 4))
            
            self.repo_list = tk.Listbox(location_frame, height=8, font=('Arial', 9))
            self.repo_list.pack(fill="both", expand=True, pady=(0, 6))
            for p in detected_repos:
                self.repo_list.insert(tk.END, str(p))
            
            ttk.Button(location_frame, text="Use Selected Repository", 
                      command=self._use_selected_repo).pack(anchor="e")
        
        # Right column - GitHub Integration
        right_column = ttk.Frame(columns_container)
        right_column.pack(side="left", fill="both", expand=True, padx=(6, 0))
        
        github_frame = ttk.LabelFrame(right_column, text="🔗 GitHub Integration", padding=10)
        github_frame.pack(fill="both", expand=True)
        
        # Enable GitHub checkbox
        self.github_enabled_var = tk.BooleanVar(value=self.data["github"].get("enabled", False))
        ttk.Checkbutton(github_frame, text="✓ Enable GitHub Integration", 
                       variable=self.github_enabled_var,
                       command=self._on_github_toggle).pack(anchor="w", pady=(0, 8))
        
        # GitHub configuration frame
        self.github_config_frame = ttk.Frame(github_frame)
        self.github_config_frame.pack(fill="both", expand=True)
        
        # Integration mode - compact
        ttk.Label(self.github_config_frame, text="Integration Mode:", 
                 font=('Arial', 9, 'bold')).pack(anchor="w", pady=(0, 4))
        
        self.gh_mode = tk.StringVar(value=self.data["github"].get("mode", "connect"))
        modes = [
            ("initialize", "📝 Initialize New Repository"),
            ("clone", "📥 Clone Existing Repository"),
            ("connect", "🔗 Connect to Existing Remote")
        ]
        
        for value, label in modes:
            ttk.Radiobutton(self.github_config_frame, text=label, 
                          variable=self.gh_mode, value=value).pack(anchor="w", pady=2)
        
        # Repository URL
        ttk.Label(self.github_config_frame, text="Repository URL:", 
                 font=('Arial', 9)).pack(anchor="w", pady=(8, 4))
        self.gh_url = tk.StringVar(value=self.data["github"].get("repo_url", ""))
        ttk.Entry(self.github_config_frame, textvariable=self.gh_url, 
                 font=('Arial', 9)).pack(fill="x", pady=(0, 2))
        ttk.Label(self.github_config_frame, text="Example: https://github.com/username/repo", 
                 font=('Arial', 8), foreground='gray').pack(anchor="w", pady=(0, 6))
        
        # Access Token
        ttk.Label(self.github_config_frame, text="Personal Access Token (optional):", 
                 font=('Arial', 9)).pack(anchor="w", pady=(0, 4))
        self.gh_token = tk.StringVar(value=self.data["github"].get("access_token", ""))
        ttk.Entry(self.github_config_frame, textvariable=self.gh_token, 
                 font=('Arial', 9), show="*").pack(fill="x", pady=(0, 2))
        ttk.Label(self.github_config_frame, text="Generate at: github.com/settings/tokens", 
                 font=('Arial', 8), foreground='gray').pack(anchor="w", pady=(0, 8))
        
        # Validation
        validation_frame = ttk.Frame(self.github_config_frame)
        validation_frame.pack(fill="x")
        ttk.Button(validation_frame, text="🔍 Validate", 
                  command=self._validate_github).pack(side="left")
        self.github_status = ttk.Label(validation_frame, text="", font=('Arial', 9))
        self.github_status.pack(side="left", padx=(10, 0))
        
        # Set initial state
        self._on_github_toggle()
        
        def collect():
            self.data["install_location"] = self.loc_var.get().strip() or str(Path.cwd())
            self.data["github"]["enabled"] = bool(self.github_enabled_var.get())
            self.data["github"]["mode"] = self.gh_mode.get()
            self.data["github"]["repo_url"] = self.gh_url.get().strip()
            self.data["github"]["access_token"] = self.gh_token.get().strip()
        f.collect = collect  # type: ignore
        return f

    def _step_alerts(self):
        f = ttk.Frame(self.body)
        alerts = self.data["alerts"]

        # Alert Channels - Horizontal Layout
        channels = ttk.LabelFrame(f, text="📢 Alert Channels", padding=12)
        channels.pack(fill="x", pady=(0, 12))
        
        self.console_var = tk.BooleanVar(value=alerts["console"]["enabled"]) 
        self.file_var = tk.BooleanVar(value=alerts["file"]["enabled"]) 
        self.email_var = tk.BooleanVar(value=alerts["email"]["enabled"]) 
        self.slack_var = tk.BooleanVar(value=alerts["slack"]["enabled"]) 
        
        # Arrange checkboxes in a 2x2 grid
        ttk.Checkbutton(channels, text="✓ Console Output", variable=self.console_var).grid(
            row=0, column=0, sticky="w", padx=(0, 30), pady=4)
        ttk.Checkbutton(channels, text="📁 File Logging", variable=self.file_var).grid(
            row=0, column=1, sticky="w", padx=(0, 30), pady=4)
        ttk.Checkbutton(channels, text="📧 Email Alerts", variable=self.email_var, 
                       command=self._on_email_toggle).grid(row=1, column=0, sticky="w", padx=(0, 30), pady=4)
        ttk.Checkbutton(channels, text="💬 Slack Integration", variable=self.slack_var, 
                       command=self._on_slack_toggle).grid(row=1, column=1, sticky="w", pady=4)

        # Two-column layout for configurations
        config_container = ttk.Frame(f)
        config_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Left Column
        left_column = ttk.Frame(config_container)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 6))
        
        # File Logging Configuration
        filebox = ttk.LabelFrame(left_column, text="📁 File Logging Configuration", padding=12)
        filebox.pack(fill="x", pady=(0, 12))
        self.log_file_var = tk.StringVar(value=alerts["file"]["log_file"]) 
        ttk.Label(filebox, text="Log file path:", font=('Arial', 9)).pack(anchor="w", pady=(0, 4))
        ttk.Entry(filebox, textvariable=self.log_file_var, font=('Arial', 9)).pack(fill="x")
        
        # Email Configuration
        email = ttk.LabelFrame(left_column, text="📧 Email Alert Configuration", padding=12)
        email.pack(fill="both", expand=True)
        
        self.smtp_server_var = tk.StringVar(value=alerts["email"].get("smtp_server", "smtp.gmail.com"))
        self.smtp_port_var = tk.StringVar(value=str(alerts["email"].get("smtp_port", 587)))
        self.email_user_var = tk.StringVar(value=alerts["email"].get("username", ""))
        self.email_pass_var = tk.StringVar(value=alerts["email"].get("password", ""))
        self.from_email_var = tk.StringVar(value=alerts["email"].get("from_email", ""))
        self.to_emails_var = tk.StringVar(value=",".join(alerts["email"].get("to_emails", [])))
        
        email_fields = [
            ("SMTP Server:", self.smtp_server_var, False),
            ("Port:", self.smtp_port_var, False),
            ("Username:", self.email_user_var, False),
            ("Password:", self.email_pass_var, True),
            ("From Address:", self.from_email_var, False),
            ("To (comma-separated):", self.to_emails_var, False),
        ]
        
        for lbl, var, is_password in email_fields:
            row_frame = ttk.Frame(email)
            row_frame.pack(fill="x", pady=2)
            ttk.Label(row_frame, text=lbl, font=('Arial', 9), width=20).pack(side="left", anchor="w")
            ttk.Entry(row_frame, textvariable=var, font=('Arial', 9), 
                     show='*' if is_password else '').pack(side="left", fill="x", expand=True)
        
        # Email validation
        email_val_frame = ttk.Frame(email)
        email_val_frame.pack(fill="x", pady=(8, 0))
        ttk.Button(email_val_frame, text="🔍 Test Configuration", 
                  command=self._validate_email).pack(side="left")
        self.email_status = ttk.Label(email_val_frame, text="", font=('Arial', 9))
        self.email_status.pack(side="left", padx=(10, 0))
        
        # Right Column
        right_column = ttk.Frame(config_container)
        right_column.pack(side="left", fill="both", expand=True, padx=(6, 0))
        
        # Slack Configuration
        slack = ttk.LabelFrame(right_column, text="💬 Slack Integration Configuration", padding=12)
        slack.pack(fill="x")
        
        self.slack_url_var = tk.StringVar(value=alerts["slack"].get("webhook_url", ""))
        self.slack_channel_var = tk.StringVar(value=alerts["slack"].get("channel", "#maintenance-alerts"))
        
        # Webhook URL
        url_frame = ttk.Frame(slack)
        url_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(url_frame, text="Webhook URL:", font=('Arial', 9)).pack(anchor="w", pady=(0, 4))
        ttk.Entry(url_frame, textvariable=self.slack_url_var, font=('Arial', 9)).pack(fill="x")
        
        # Channel
        channel_frame = ttk.Frame(slack)
        channel_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(channel_frame, text="Channel:", font=('Arial', 9)).pack(anchor="w", pady=(0, 4))
        ttk.Entry(channel_frame, textvariable=self.slack_channel_var, font=('Arial', 9)).pack(fill="x")
        
        # Slack validation
        slack_val_frame = ttk.Frame(slack)
        slack_val_frame.pack(fill="x", pady=(8, 0))
        ttk.Button(slack_val_frame, text="🔍 Test Connection", 
                  command=self._validate_slack).pack(side="left")
        self.slack_status = ttk.Label(slack_val_frame, text="", font=('Arial', 9))
        self.slack_status.pack(side="left", padx=(10, 0))

        def collect():
            alerts["console"]["enabled"] = bool(self.console_var.get())
            alerts["file"]["enabled"] = bool(self.file_var.get())
            alerts["file"]["log_file"] = self.log_file_var.get().strip() or "codesentinel.log"
            alerts["email"]["enabled"] = bool(self.email_var.get())
            alerts["email"].update({
                "smtp_server": self.smtp_server_var.get().strip(),
                "smtp_port": int(self.smtp_port_var.get() or 587),
                "username": self.email_user_var.get().strip(),
                "password": self.email_pass_var.get(),
                "from_email": self.from_email_var.get().strip(),
                "to_emails": [e.strip() for e in self.to_emails_var.get().split(',') if e.strip()],
            })
            alerts["slack"]["enabled"] = bool(self.slack_var.get())
            alerts["slack"].update({
                "webhook_url": self.slack_url_var.get().strip(),
                "channel": self.slack_channel_var.get().strip() or "#maintenance-alerts",
            })
        f.collect = collect  # type: ignore
        return f
    
    def _validate_email(self):
        """Validate email configuration."""
        self.email_status.config(text="🔍 Testing...", foreground=self.colors['processing'])
        self.root.update()
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            server = self.smtp_server_var.get().strip()
            port = int(self.smtp_port_var.get() or 587)
            username = self.email_user_var.get().strip()
            password = self.email_pass_var.get()
            from_addr = self.from_email_var.get().strip()
            
            if not all([server, username, password, from_addr]):
                self.email_status.config(text="❌ Missing required fields", foreground=self.colors['error'])
                self.validations['email'] = False
                self._update_nav_state()
                return
            
            # Test connection
            smtp = smtplib.SMTP(server, port, timeout=10)
            smtp.starttls()
            smtp.login(username, password)
            smtp.quit()
            
            self.email_status.config(text="✓ Configuration valid", foreground=self.colors['success'])
            self.validations['email'] = True
            self._update_nav_state()
        except Exception as e:
            self.email_status.config(text=f"❌ Error: {str(e)[:30]}...", foreground=self.colors['error'])
            self.validations['email'] = False
            self._update_nav_state()
    
    def _validate_slack(self):
        """Validate Slack webhook."""
        self.slack_status.config(text="🔍 Testing...", foreground=self.colors['processing'])
        self.root.update()
        
        try:
            import json
            import urllib.request
            from urllib.parse import urlparse

            webhook_url = self.slack_url_var.get().strip()

            if not webhook_url:
                self.slack_status.config(text="❌ Webhook URL required", foreground=self.colors['error'])
                self.validations['slack'] = False
                self._update_nav_state()
                return

            # Basic allowlist validation to prevent SSRF: only allow Slack webhooks
            parsed = urlparse(webhook_url)
            host = (parsed.hostname or "").lower()
            if not (parsed.scheme == "https" and host and (host == "hooks.slack.com" or host.endswith(".slack.com")) and "/services/" in parsed.path):
                self.slack_status.config(text="❌ Invalid Slack webhook URL", foreground=self.colors['error'])
                self.validations['slack'] = False
                self._update_nav_state()
                return

            # Test webhook with a test message
            data = json.dumps({"text": "CodeSentinel test message"}).encode('utf-8')
            req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json'})
            response = urllib.request.urlopen(req, timeout=10)

            if response.status == 200:
                self.slack_status.config(text="✓ Webhook valid", foreground=self.colors['success'])
                self.validations['slack'] = True
                self._update_nav_state()
            else:
                self.slack_status.config(text=f"❌ HTTP {response.status}", foreground=self.colors['error'])
                self.validations['slack'] = False
                self._update_nav_state()
        except Exception as e:
            self.slack_status.config(text=f"❌ Error: {str(e)[:30]}...", foreground=self.colors['error'])
            self.validations['slack'] = False
            self._update_nav_state()

    def _on_email_toggle(self):
        """Handle email checkbox toggle - reset validation state."""
        if self.email_var.get():
            # Just enabled - mark as needing validation
            self.validations['email'] = False
            self.email_status.config(text="⚠️ Not validated", foreground=self.colors['warning'])
        else:
            # Disabled - no validation needed
            self.validations['email'] = True
            self.email_status.config(text="", foreground="black")
        self._update_nav_state()
    
    def _on_slack_toggle(self):
        """Handle Slack checkbox toggle - reset validation state."""
        if self.slack_var.get():
            # Just enabled - mark as needing validation
            self.validations['slack'] = False
            self.slack_status.config(text="⚠️ Not validated", foreground=self.colors['warning'])
        else:
            # Disabled - no validation needed
            self.validations['slack'] = True
            self.slack_status.config(text="", foreground="black")
        self._update_nav_state()

    
    def _on_github_toggle(self):
        """Handle GitHub enable/disable toggle."""
        enabled = self.github_enabled_var.get()
        state = "normal" if enabled else "disabled"
        
        # Enable/disable all widgets in the config frame
        for child in self.github_config_frame.winfo_children():
            self._set_widget_state_recursive(child, state)
        
        # Update validation state
        if not enabled:
            self.validations['github'] = True  # Not required if disabled
            self.github_status.config(text="")
        else:
            # If enabled, mark as needing validation
            self.validations['github'] = False
            self.github_status.config(text="⚠️ Not validated", foreground=self.colors['warning'])
        
        # Update navigation
        self.root.after(10, self._update_nav_state)
    
    def _set_widget_state_recursive(self, widget, state):
        """Recursively set state of all child widgets."""
        try:
            if isinstance(widget, (ttk.Button, ttk.Radiobutton, ttk.Entry, ttk.Checkbutton)):
                widget.configure(state=state)
        except:
            pass
        
        for child in widget.winfo_children():
            self._set_widget_state_recursive(child, state)
    
    def _validate_github(self):
        """Validate GitHub repository connection."""
        self.github_status.config(text="🔍 Validating...", foreground=self.colors['processing'])
        self.root.update()
        
        try:
            import urllib.request
            import urllib.error
            
            url = self.gh_url.get().strip()
            token = self.gh_token.get().strip()
            
            if not url:
                self.github_status.config(text="❌ Please enter a repository URL", foreground=self.colors['error'])
                self.validations['github'] = False
                self._update_nav_state()
                return
            
            # Validate GitHub URL format
            if not ('github.com' in url.lower()):
                self.github_status.config(text="❌ Please enter a valid GitHub URL", foreground=self.colors['error'])
                self.validations['github'] = False
                self._update_nav_state()
                return
            
            # Extract owner/repo from URL
            parts = url.rstrip('/').split('/')
            if len(parts) >= 2:
                owner, repo = parts[-2], parts[-1].replace('.git', '')
                api_url = f"https://api.github.com/repos/{owner}/{repo}"
                
                req = urllib.request.Request(api_url)
                req.add_header('User-Agent', 'CodeSentinel-Setup')
                
                # Add authorization header if token provided
                if token:
                    req.add_header('Authorization', f'token {token}')
                
                try:
                    response = urllib.request.urlopen(req, timeout=10)
                    if response.status == 200:
                        self.github_status.config(text="✓ Repository accessible", foreground=self.colors['success'])
                        self.validations['github'] = True
                    else:
                        self.github_status.config(text=f"❌ HTTP {response.status}", foreground=self.colors['error'])
                        self.validations['github'] = False
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        self.github_status.config(text="❌ Repository not found", foreground=self.colors['error'])
                    elif e.code == 401:
                        self.github_status.config(text="❌ Invalid access token", foreground=self.colors['error'])
                    else:
                        self.github_status.config(text=f"❌ HTTP {e.code}", foreground=self.colors['error'])
                    self.validations['github'] = False
            else:
                self.github_status.config(text="❌ Invalid URL format", foreground=self.colors['error'])
                self.validations['github'] = False
                
        except Exception as e:
            self.github_status.config(text=f"❌ Error: {str(e)[:30]}...", foreground=self.colors['error'])
            self.validations['github'] = False
        
        self._update_nav_state()

    def _step_ide(self):
        # Compact, non-scroll implementation to avoid occluding footer
        f = ttk.Frame(self.body)
        
        # Compact header
        ttk.Label(f, text="Configure integration with your development environment.", 
                 font=('Arial', 9), foreground='gray').pack(anchor="w", pady=(0, 8))
        
        # IDE Support Section
        ide_frame = ttk.LabelFrame(f, text="🔍 Detected IDEs", padding=10)
        # Do not expand to avoid pushing into footer; allow wrapping into two columns
        ide_frame.pack(fill="x", expand=False, pady=(0, 6))
        grid_frame = ttk.Frame(ide_frame)
        grid_frame.pack(fill="x", expand=False)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        
        # Define IDE configurations with detection commands
        ide_configs = [
            {
                'name': 'Visual Studio Code',
                'key': 'VS Code',
                'description': 'Lightweight, extensible code editor',
                'commands': ['code'],
                'paths': [
                    'C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe',
                    'C:\\Program Files\\Microsoft VS Code\\Code.exe',
                    'C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe'
                ],
                'icon': '📝',
                'url': 'https://code.visualstudio.com/'
            },
            {
                'name': 'Visual Studio',
                'key': 'Visual Studio',
                'description': 'Full-featured IDE for .NET and C++',
                'commands': ['devenv'],
                'paths': [
                    'C:\\Program Files\\Microsoft Visual Studio\\2022\\*\\Common7\\IDE\\devenv.exe',
                    'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\*\\Common7\\IDE\\devenv.exe',
                    'C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\*\\Common7\\IDE\\devenv.exe'
                ],
                'icon': '🏢',
                'url': 'https://visualstudio.microsoft.com/'
            },
            {
                'name': 'PyCharm',
                'key': 'PyCharm',
                'description': 'Python-focused IDE by JetBrains',
                'commands': ['pycharm64', 'charm', 'pycharm'],
                'paths': [
                    'C:\\Users\\{username}\\AppData\\Local\\JetBrains\\Toolbox\\apps\\PyCharm-P\\*\\bin\\pycharm64.exe',
                    'C:\\Program Files\\JetBrains\\PyCharm*\\bin\\pycharm64.exe',
                    'C:\\Users\\{username}\\AppData\\Local\\JetBrains\\PyCharm*\\bin\\pycharm64.exe',
                    'C:\\Program Files\\JetBrains\\PyCharm*\\bin\\pycharm.exe'
                ],
                'icon': '🐍',
                'url': 'https://www.jetbrains.com/pycharm/'
            },
            {
                'name': 'IntelliJ IDEA',
                'key': 'IntelliJ IDEA',
                'description': 'Java IDE with multi-language support',
                'commands': ['idea64', 'idea'],
                'paths': [
                    'C:\\Users\\{username}\\AppData\\Local\\JetBrains\\Toolbox\\apps\\IDEA-U\\*\\bin\\idea64.exe',
                    'C:\\Program Files\\JetBrains\\IntelliJ IDEA*\\bin\\idea64.exe'
                ],
                'icon': '☕',
                'url': 'https://www.jetbrains.com/idea/'
            },
            {
                'name': 'RStudio',
                'key': 'RStudio',
                'description': 'IDE for R statistical computing and graphics',
                'commands': ['rstudio'],
                'paths': [
                    'C:\\Program Files\\RStudio\\rstudio.exe',
                    'C:\\Program Files\\RStudio\\bin\\rstudio.exe',
                    'C:\\Users\\{username}\\AppData\\Local\\RStudio\\rstudio.exe'
                ],
                'icon': '📊',
                'url': 'https://posit.co/download/rstudio-desktop/'
            },
            {
                'name': 'Sublime Text',
                'key': 'Sublime Text',
                'description': 'Fast, lightweight text editor',
                'commands': ['sublime_text', 'subl'],
                'paths': [
                    'C:\\Program Files\\Sublime Text*\\sublime_text.exe',
                    'C:\\Users\\{username}\\AppData\\Local\\Sublime Text*\\sublime_text.exe'
                ],
                'icon': '📄',
                'url': 'https://www.sublimetext.com/'
            },
            {
                'name': 'Atom',
                'key': 'Atom',
                'description': 'Hackable text editor (deprecated)',
                'commands': ['atom'],
                'paths': [
                    'C:\\Users\\{username}\\AppData\\Local\\atom\\atom.exe'
                ],
                'icon': '⚛️',
                'url': 'https://atom.io/'
            },
            {
                'name': 'Notepad++',
                'key': 'Notepad++',
                'description': 'Enhanced notepad with syntax highlighting',
                'commands': ['notepad++'],
                'paths': [
                    'C:\\Program Files\\Notepad++\\notepad++.exe',
                    'C:\\Program Files (x86)\\Notepad++\\notepad++.exe'
                ],
                'icon': '📋',
                'url': 'https://notepad-plus-plus.org/'
            },
            {
                'name': 'Eclipse',
                'key': 'Eclipse',
                'description': 'Java development environment',
                'commands': ['eclipse'],
                'paths': [
                    'C:\\eclipse\\eclipse.exe',
                    'C:\\Program Files\\Eclipse\\*\\eclipse.exe'
                ],
                'icon': '🌙',
                'url': 'https://www.eclipse.org/'
            }
        ]
        
        # Detect IDEs using both PATH commands and file system checks
        import glob
        username = os.getenv('USERNAME', 'User')
        
        statuses = {}
        self.ide_vars = {}  # Store checkbox variables
        
        for idx, config in enumerate(ide_configs):
            found = False
            
            # First try PATH-based detection
            if any(shutil.which(cmd) for cmd in config['commands']):
                found = True
            
            # If not found, try file system paths
            if not found and 'paths' in config:
                for pattern in config['paths']:
                    # Replace username placeholder
                    pattern = pattern.replace('{username}', username)
                    try:
                        # Use glob to handle wildcard patterns
                        matches = glob.glob(pattern)
                        if matches:
                            found = True
                            break
                    except Exception:
                        continue
            
            statuses[config['key']] = found
            
            # Create IDE cell in a 2-column grid to reduce height
            row, col = divmod(idx, 2)
            ide_row = ttk.Frame(grid_frame)
            ide_row.grid(row=row, column=col, sticky="nsew", padx=(0, 6) if col == 0 else (6, 0), pady=2)
            
            # Checkbox for selection (default: enabled if detected)
            self.ide_vars[config['key']] = tk.BooleanVar(value=found)
            checkbox = ttk.Checkbutton(ide_row, variable=self.ide_vars[config['key']])
            checkbox.pack(side="left", padx=(0, 8))
            
            # Left side: icon, name, and status
            left_frame = ttk.Frame(ide_row)
            left_frame.pack(side="left", fill="x", expand=True)
            
            if found:
                status_text = f"{config['icon']} {config['name']}"
                status_color = self.colors['success']
                status_label = "✓ Detected"
            else:
                status_text = f"{config['icon']} {config['name']}"
                status_color = self.colors['disabled']
                status_label = "Not detected"
            
            # IDE name with icon
            name_frame = ttk.Frame(left_frame)
            name_frame.pack(anchor="w")
            ttk.Label(name_frame, text=status_text, font=('Arial', 9, 'bold'), 
                     foreground=status_color).pack(side="left")
            ttk.Label(name_frame, text=f" - {status_label}", font=('Arial', 9), 
                     foreground=status_color).pack(side="left")
            
            # Description - more compact
            ttk.Label(left_frame, text=f"  {config['description']}", 
                     font=('Arial', 8), foreground='gray').pack(anchor="w", padx=(20, 0))
            
            # Right side: Download button for not detected IDEs
            if not found:
                def open_url(url=config['url']):
                    import webbrowser
                    webbrowser.open(url)
                
                ttk.Button(ide_row, text="Download", 
                          command=open_url).pack(side="right", padx=(6, 0))
        
        # Store IDE detection results and selections
        def collect():
            # Store both detection status and user selection
            ide_data = {}
            for key, var in self.ide_vars.items():
                ide_data[key] = {
                    'detected': statuses[key],
                    'enabled': var.get()
                }
            self.data["ide"] = ide_data
        
        f.collect = collect  # type: ignore

        # Compact note about installation
        note_frame = ttk.Frame(f)
        note_frame.pack(fill="x", pady=(8, 0))
        ttk.Label(
            note_frame,
            text="ℹ️ IDE integration files will be created during final installation.",
            font=('Arial', 8),
            foreground='gray'
        ).pack(anchor="w")

        return f

    def _step_copilot(self):
        """GitHub Copilot integration configuration."""
        f = ttk.Frame(self.body)
        
        # Compact header
        ttk.Label(f, text="Configure AI-powered code assistance and intelligent automation.", 
                 font=('Arial', 9), foreground="gray").pack(anchor="w", pady=(0, 10))
        
        # Two-column layout
        columns_container = ttk.Frame(f)
        columns_container.pack(fill="both", expand=True)
        
        # Left column
        left_column = ttk.Frame(columns_container)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 6))
        
        # Copilot detection status
        has_vscode = self.data["ide"].get("VS Code", False)
        copilot_detected = has_vscode and shutil.which("code") is not None
        
        detection_frame = ttk.LabelFrame(left_column, text="🔍 IDE Detection", padding=10)
        detection_frame.pack(fill="x", pady=(0, 8))
        
        if copilot_detected:
            ttk.Label(detection_frame, text="✓ VS Code detected - Copilot integration available", 
                     font=('Arial', 9), foreground=self.colors['success']).pack(anchor="w")
        else:
            ttk.Label(detection_frame, text="⚠ VS Code not detected - Install for full integration", 
                     font=('Arial', 9), foreground=self.colors['warning']).pack(anchor="w")
        
        # Integration options
        options_frame = ttk.LabelFrame(left_column, text="⚙️ Integration Options", padding=10)
        options_frame.pack(fill="both", expand=True)
        
        self.copilot_enabled = tk.BooleanVar(value=self.data["copilot"]["enabled"])
        self.copilot_vscode_ext = tk.BooleanVar(value=self.data["copilot"]["install_vscode_extension"])
        self.copilot_instructions = tk.BooleanVar(value=self.data["copilot"]["generate_instructions"])
        self.copilot_agent_mode = tk.BooleanVar(value=self.data["copilot"]["enable_agent_mode"])
        
        # Main enable checkbox
        ttk.Checkbutton(options_frame, text="✓ Enable GitHub Copilot Integration",
                       variable=self.copilot_enabled, command=self._toggle_copilot_options).pack(anchor="w", pady=(0, 6))
        
        # Sub-options frame
        self.copilot_sub_frame = ttk.Frame(options_frame)
        self.copilot_sub_frame.pack(fill="x", padx=(20, 0))
        
        ttk.Checkbutton(self.copilot_sub_frame, text="📦 Install VS Code Extension",
                       variable=self.copilot_vscode_ext, 
                       state="normal" if self.copilot_enabled.get() else "disabled").pack(anchor="w", pady=2)
        
        ttk.Checkbutton(self.copilot_sub_frame, text="📝 Generate Copilot Instructions",
                       variable=self.copilot_instructions,
                       state="normal" if self.copilot_enabled.get() else "disabled").pack(anchor="w", pady=2)
        
        ttk.Checkbutton(self.copilot_sub_frame, text="🤖 Enable Agent Mode",
                       variable=self.copilot_agent_mode,
                       state="normal" if self.copilot_enabled.get() else "disabled").pack(anchor="w", pady=2)
        
        # Right column
        right_column = ttk.Frame(columns_container)
        right_column.pack(side="left", fill="both", expand=True, padx=(6, 0))
        
        # Benefits section
        benefits_frame = ttk.LabelFrame(right_column, text="✨ What You Get", padding=10)
        benefits_frame.pack(fill="both", expand=True, pady=(0, 8))
        
        benefits = [
            "🔍 AI-powered code review",
            "🤖 Intelligent audit remediation",
            "📝 Context-aware code generation",
            "🛡️ Security-first automation",
            "📊 Smart analysis with remediation",
            "🎯 Automated cleanup"
        ]
        
        for benefit in benefits:
            ttk.Label(benefits_frame, text=benefit, font=('Arial', 9), 
                     foreground="#424242").pack(anchor="w", pady=2)
        
        # Installation notes
        note_frame = ttk.LabelFrame(right_column, text="ℹ️ Installation Notes", padding=10)
        note_frame.pack(fill="x")
        
        notes = [
            "• Extension installs via code command",
            "• Instructions at .github/copilot-instructions.md",
            "• GitHub Copilot from VS Code marketplace"
        ]
        
        for note in notes:
            ttk.Label(note_frame, text=note, font=('Arial', 8), 
                     foreground="gray").pack(anchor="w", pady=1)
        
        self._toggle_copilot_options()
        
        def collect():
            self.data["copilot"].update({
                "enabled": bool(self.copilot_enabled.get()),
                "install_vscode_extension": bool(self.copilot_vscode_ext.get()),
                "generate_instructions": bool(self.copilot_instructions.get()),
                "enable_agent_mode": bool(self.copilot_agent_mode.get()),
            })
        
        f.collect = collect  # type: ignore
        return f
    
    def _toggle_copilot_options(self):
        """Enable/disable sub-options based on main checkbox."""
        state = "normal" if self.copilot_enabled.get() else "disabled"
        for child in self.copilot_sub_frame.winfo_children():
            if isinstance(child, ttk.Checkbutton):
                child.configure(state=state)

    def _step_optional(self):
        f = ttk.Frame(self.body)
        
        # Compact header
        ttk.Label(f, text="Configure additional automation features that enhance security and workflow.", 
                 font=('Arial', 9), foreground="gray").pack(anchor="w", pady=(0, 10))
        
        # Initialize variables
        self.opt_scheduler = tk.BooleanVar(value=self.data["optional"]["scheduler"]) 
        self.opt_hooks = tk.BooleanVar(value=self.data["optional"]["git_hooks"]) 
        self.opt_ci = tk.BooleanVar(value=self.data["optional"]["ci"])
        
        # Features frame
        features_frame = ttk.LabelFrame(f, text="🚀 Automation & Integration Features", padding=10)
        features_frame.pack(fill="both", expand=True, pady=(0, 8))
        
        # Feature 1: Scheduled Maintenance
        self._create_optional_feature(
            features_frame, 
            self.opt_scheduler,
            "Automated Maintenance Scheduling",
            "Cron jobs for scheduled maintenance",
            "Daily/weekly/monthly automation:\n"
            "• Security scans, dependency checks\n"
            "• Performance analysis, audits\n"
            "Requires: System task scheduling permissions",
            recommended=False,
            complexity="Advanced",
            impact="Hands-off automation",
            show_separator=True
        )
        
        # Feature 2: Git Hooks
        self._create_optional_feature(
            features_frame,
            self.opt_hooks,
            "Git Hooks Integration (Recommended)",
            "Pre-commit and pre-push validation",
            "Automatic checks before commits:\n"
            "• Code formatting, lint checks, security scans\n"
            "• Test suite, dependency validation\n"
            "Requires: Git repository (auto-detected)",
            recommended=True,
            complexity="Beginner",
            impact="Catch issues early",
            show_separator=True
        )
        
        # Feature 3: CI/CD Templates
        self._create_optional_feature(
            features_frame,
            self.opt_ci,
            "CI/CD Workflow Templates",
            "GitHub Actions and pipeline configurations",
            "Workflow templates for CI:\n"
            "• GitHub Actions, GitLab CI, Azure DevOps\n"
            "• Automated testing, security scanning\n"
            "Requires: Git repository with remote",
            recommended=False,
            complexity="Intermediate",
            impact="Professional workflows",
            show_separator=False
        )
        
        # Recommendations section
        recommendations_frame = ttk.LabelFrame(f, text="💡 Smart Recommendations", padding=10)
        recommendations_frame.pack(fill="x")
        
        # Generate context-aware recommendations
        recommendations = []
        try:
            if (Path.cwd() / ".git").exists():
                recommendations.append("Git Hooks highly recommended for your Git repository")
            if self.data.get("github", {}).get("enabled", False):
                recommendations.append("CI/CD templates complement your GitHub integration")
            if not recommendations:
                recommendations.append("Git Hooks provide immediate value with minimal setup")
        except:
            recommendations.append("Review each feature to choose what fits your workflow")
        
        rec_text = "Based on your configuration:\n" + "\n".join(f"• {rec}" for rec in recommendations)
        ttk.Label(recommendations_frame, text=rec_text, font=('Arial', 9), 
                 justify="left", foreground="#424242").pack(anchor="w")

        def collect():
            self.data["optional"].update({
                "scheduler": bool(self.opt_scheduler.get()),
                "git_hooks": bool(self.opt_hooks.get()),
                "ci": bool(self.opt_ci.get()),
            })
        f.collect = collect  # type: ignore
        return f
    
    def _create_optional_feature(self, parent, var, title, subtitle, description, 
                                 recommended, complexity, impact, show_separator):
        """Create a detailed feature section with expandable information."""
        # Main feature frame
        feature_frame = ttk.Frame(parent)
        feature_frame.pack(fill="x", pady=3)
        
        # Header frame with checkbox and badges
        header_frame = ttk.Frame(feature_frame)
        header_frame.pack(fill="x")
        
        # Checkbox with title
        checkbox = ttk.Checkbutton(header_frame, text=f"✓ {title}", variable=var)
        checkbox.pack(side="left", anchor="w")
        
        # Badges
        badge_frame = ttk.Frame(header_frame)
        badge_frame.pack(side="right")
        
        complexity_colors = {'Beginner': self.colors['success'], 
                            'Intermediate': self.colors['warning'], 
                            'Advanced': self.colors['error']}
        
        ttk.Label(badge_frame, text=f"📊 {complexity}", font=('Arial', 8), 
                 foreground=complexity_colors.get(complexity, 'black')).pack(side="right", padx=(8, 0))
        
        ttk.Label(badge_frame, text=f"🎯 {impact}", font=('Arial', 8), 
                 foreground="#424242").pack(side="right", padx=(8, 0))
        
        # Subtitle
        ttk.Label(feature_frame, text=subtitle, font=('Arial', 9, 'italic'), 
                 foreground="gray").pack(anchor="w", pady=(1, 3), padx=(20, 0))
        
        # Description (collapsible)
        desc_frame = ttk.Frame(feature_frame)
        desc_frame.pack(fill="x", padx=(20, 0))
        
        desc_var = tk.BooleanVar(value=False)
        desc_label = ttk.Label(desc_frame, text=description, font=('Arial', 8), 
                              justify="left", foreground='#333333')
        
        def toggle_description():
            desc_var.set(not desc_var.get())
            if desc_var.get():
                desc_label.pack(fill="x", pady=(3, 3))
                toggle_btn.config(text="ℹ️ Hide Details")
            else:
                desc_label.pack_forget()
                toggle_btn.config(text="ℹ️ Show Details")
        
        toggle_btn = ttk.Button(desc_frame, text="ℹ️ Show Details", command=toggle_description)
        toggle_btn.pack(anchor="w", pady=(0, 3))
        
        # Separator
        if show_separator:
            ttk.Separator(feature_frame, orient='horizontal').pack(fill="x", pady=(6, 0))

    def _step_summary(self):
        f = ttk.Frame(self.body)
        
        # Header
        ttk.Label(f, text="Review your configuration, then click Finish to save.", 
                 font=('Arial', 9), foreground="gray").pack(anchor="w", pady=(0, 10))
        
        # Summary display in a styled Text widget with scrollbar
        text_frame = ttk.Frame(f)
        text_frame.pack(fill="both", expand=True)
        
        # Text widget with scrollbar
        text_scrollbar = ttk.Scrollbar(text_frame)
        text_scrollbar.pack(side="right", fill="y")
        
        self.summary_text = tk.Text(text_frame, 
                                    wrap="word",
                                    font=('Consolas', 9),
                                    bg="#f5f5f5",
                                    relief="solid",
                                    borderwidth=1,
                                    yscrollcommand=text_scrollbar.set)
        self.summary_text.pack(side="left", fill="both", expand=True)
        text_scrollbar.config(command=self.summary_text.yview)

        # Footer area with repo link and attribution (Polymath venture)
        footer = ttk.Frame(f)
        footer.pack(fill="x", pady=(8, 0))
        repo_url = "https://github.com/joediggidy/CodeSentinel"
        repo_link = ttk.Label(footer, text="View repository on GitHub", foreground=self.colors['info'], cursor="hand2")
        repo_link.pack(anchor="w")
        repo_link.bind("<Button-1>", lambda e, url=repo_url: webbrowser.open_new(url))

        # Centered thumbnail + tagline
        venture_container = ttk.Frame(footer)
        venture_container.pack(anchor="center", pady=(6, 0))
        
        # Caption above thumbnail
        ttk.Label(venture_container, text="a Polymath venture", 
                 font=('Arial', 8, 'italic'), foreground="#666666").pack(anchor="center", pady=(0, 2))
        
        # Thumbnail (scaled down)
        try:
            from pathlib import Path as _P
            _here = _P(__file__).resolve().parent
            candidate_paths = [
                _here / "assets" / "polymath.png",
                _here.parent / "docs" / "polymath.png",
            ]
            self._polymath_img = None
            for _p in candidate_paths:
                if _p.exists():
                    full_img = tk.PhotoImage(file=str(_p))
                    target_w, target_h = 50, 40
                    # Determine scaling factor to keep aspect ratio within target bounds
                    width_factor = max(1, (full_img.width() + target_w - 1) // target_w)
                    height_factor = max(1, (full_img.height() + target_h - 1) // target_h)
                    scale = max(width_factor, height_factor)
                    self._polymath_img = full_img.subsample(scale, scale)  # type: ignore
                    break
            if self._polymath_img is not None:
                img_label = ttk.Label(venture_container, image=self._polymath_img)
                img_label.pack(anchor="center")
        except Exception:
            # Image optional; proceed without it
            self._polymath_img = None

        def collect():
            """Generate formatted summary of configuration."""
            try:
                self.summary_text.config(state="normal")  # Enable editing
                self.summary_text.delete("1.0", tk.END)
                
                # Build readable summary
                summary = []
                summary.append("╔" + "═" * 58 + "╗")
                summary.append("║" + "  CODESENTINEL CONFIGURATION SUMMARY".center(58) + "║")
                summary.append("╚" + "═" * 58 + "╝")
                summary.append("")
                
                # Installation Location
                summary.append("📁 INSTALLATION")
                summary.append("   ─────────────────────────────────────────────")
                summary.append(f"   Location: {self.data.get('install_location', 'Not set')}")
                github_data = self.data.get('github', {})
                summary.append(f"   Mode:     {github_data.get('mode', 'Not set').upper()}")
                summary.append("")
                
                # GitHub Integration
                summary.append("🔗 GITHUB INTEGRATION")
                summary.append("   ─────────────────────────────────────────────")
                repo_url = github_data.get('repo_url', '')
                if repo_url:
                    summary.append("   Status:   ✓ CONFIGURED")
                    summary.append(f"   Repository: {repo_url}")
                    if github_data.get('create'):
                        summary.append("   Action: Create new repository")
                else:
                    summary.append("   Status:   ✗ Not configured")
                summary.append("")
                
                # Alerts
                summary.append("🔔 ALERT CONFIGURATION")
                summary.append("   ─────────────────────────────────────────────")
                
                # File Logging
                alerts = self.data.get('alerts', {})
                file_alerts = alerts.get('file', {})
                if file_alerts.get('enabled'):
                    summary.append("   File Logging: ✓ ENABLED")
                    summary.append(f"      • Path:  {file_alerts.get('log_file', 'codesentinel.log')}")
                else:
                    summary.append("   File Logging: ✗ Disabled")
                
                # Email
                email_alerts = alerts.get('email', {})
                if email_alerts.get('enabled'):
                    summary.append("   Email Alerts: ✓ ENABLED")
                    to_emails = email_alerts.get('to_emails', [])
                    summary.append(f"      • To:   {', '.join(to_emails) if to_emails else 'Not set'}")
                    summary.append(f"      • SMTP: {email_alerts.get('smtp_server', '')}:{email_alerts.get('smtp_port', 587)}")
                else:
                    summary.append("   Email Alerts: ✗ Disabled")
                
                # Slack
                slack_alerts = alerts.get('slack', {})
                if slack_alerts.get('enabled'):
                    summary.append("   Slack Alerts: ✓ ENABLED")
                    summary.append(f"      • Channel: {slack_alerts.get('channel', '#maintenance-alerts')}")
                else:
                    summary.append("   Slack Alerts: ✗ Disabled")
                summary.append("")
                
                # IDE Integration
                summary.append("💻 IDE INTEGRATION")
                summary.append("   ─────────────────────────────────────────────")
                ide_data = self.data.get('ide', {})
                enabled_ides = []
                for ide, data in ide_data.items():
                    # Check if it's the new format (dict with 'enabled' key) or old format (boolean)
                    if isinstance(data, dict):
                        if data.get('enabled', False):
                            enabled_ides.append(ide)
                    elif data:  # Old format: direct boolean
                        enabled_ides.append(ide)
                
                if enabled_ides:
                    for ide in enabled_ides:
                        summary.append(f"   ✓ {ide}")
                else:
                    summary.append("   No IDEs selected")
                summary.append("")
                
                # Copilot Integration
                summary.append("🤖 GITHUB COPILOT")
                summary.append("   ─────────────────────────────────────────────")
                copilot_data = self.data.get('copilot', {})
                if copilot_data.get('enabled'):
                    summary.append("   Status: ✓ ENABLED")
                    summary.append("   Features:")
                    if copilot_data.get('install_vscode_extension'):
                        summary.append("      ✓ Install VS Code Extension")
                    if copilot_data.get('generate_instructions'):
                        summary.append("      ✓ Generate Instructions File")
                    if copilot_data.get('enable_agent_mode'):
                        summary.append("      ✓ Agent Mode Enabled")
                else:
                    summary.append("   Status: ✗ Disabled")
                summary.append("")
                
                # Optional Features
                summary.append("⚙️ OPTIONAL FEATURES")
                summary.append("   ─────────────────────────────────────────────")
                optional_data = self.data.get('optional', {})
                optional_enabled = []
                if optional_data.get('scheduler'):
                    optional_enabled.append("   ✓ Automated Maintenance Scheduling")
                if optional_data.get('git_hooks'):
                    optional_enabled.append("   ✓ Git Hooks Integration")
                if optional_data.get('ci'):
                    optional_enabled.append("   ✓ CI/CD Workflow Templates")
                
                if optional_enabled:
                    summary.extend(optional_enabled)
                else:
                    summary.append("   No optional features selected")
                summary.append("")
                
                summary.append("─" * 60)
                summary.append("✓ Configuration complete - Click 'Finish' to save and exit")
                summary.append("─" * 60)
                
                self.summary_text.insert("1.0", "\n".join(summary))
                self.summary_text.config(state="disabled")  # Make read-only
                
            except Exception as e:
                # If there's an error, show it in the text widget
                self.summary_text.config(state="normal")
                self.summary_text.insert("1.0", f"Error generating summary:\n{str(e)}\n\nData: {self.data}")
                self.summary_text.config(state="disabled")
        
        f.collect = collect  # type: ignore
        
        # Populate summary immediately on page load
        collect()
        
        return f

    # ---- helpers ----
    def _browse_location(self):
        selected = filedialog.askdirectory(initialdir=self.loc_var.get() or str(Path.home()))
        if selected:
            self.loc_var.set(selected)

    def _detect_git_repos(self) -> List[Path]:
        # Search a few common roots and parents, limited depth and count
        roots = {
            Path.home() / "Documents",
            Path.home() / "Projects",
            Path.home() / "Code",
            Path.cwd().parent,
            Path.cwd(),
        }
        found: List[Path] = []
        queue: List[Tuple[Path, int]] = [(p, 0) for p in roots if p.exists()]
        max_depth, max_count = 3, 10
        seen = set()
        while queue and len(found) < max_count:
            base, depth = queue.pop(0)
            if base in seen:
                continue
            seen.add(base)
            try:
                for child in base.iterdir():
                    if child.is_dir():
                        if (child / ".git").exists():
                            found.append(child)
                            if len(found) >= max_count:
                                break
                        if depth < max_depth:
                            queue.append((child, depth + 1))
            except (PermissionError, OSError):
                continue
        return found

    def _use_selected_repo(self):
        try:
            sel = self.repo_list.curselection()
            if sel:
                self.loc_var.set(self.repo_list.get(sel[0]))
        except Exception:
            pass

    def _save_and_finish(self):
        # Save configuration to selected location
        target = Path(self.data["install_location"]) / "codesentinel.json"
        cm = ConfigManager(config_path=target)
        cm.save_config(self.data)
        
        install_path = Path(self.data["install_location"])
        
        # Optionally init git if chosen mode requires and repo missing
        if self.data.get("github", {}).get("mode") == "initialize":
            if not (install_path / ".git").exists():
                try:
                    import subprocess
                    subprocess.run(["git", "init"], cwd=str(install_path), capture_output=True)
                except Exception:
                    pass
        
        # Handle Copilot integration
        copilot_config = self.data.get("copilot", {})
        if copilot_config.get("enabled", False):
            self._install_copilot_integration(install_path, copilot_config)
        
        messagebox.showinfo("Setup Complete", f"Configuration saved to: {target}")
        self.root.destroy()

    def _install_copilot_integration(self, install_path: Path, config: Dict[str, Any]):
        """Install Copilot integration components."""
        import subprocess
        
        results = []
        
        # Generate Copilot instructions
        if config.get("generate_instructions", True):
            try:
                self._generate_copilot_instructions(install_path)
                results.append("✓ Generated .github/copilot-instructions.md")
            except Exception as e:
                results.append(f"✗ Failed to generate instructions: {e}")
        
        # Install VS Code extension
        if config.get("install_vscode_extension", False):
            try:
                # Check if 'code' command is available
                if shutil.which("code"):
                    # For now, just create a VS Code settings file with CodeSentinel config
                    # In the future, we can create an actual extension
                    vscode_dir = install_path / ".vscode"
                    vscode_dir.mkdir(exist_ok=True)
                    
                    settings_file = vscode_dir / "settings.json"
                    settings = {
                        "codesentinel.enabled": True,
                        "codesentinel.agentMode": config.get("enable_agent_mode", True),
                        "codesentinel.autoAudit": False,
                        "github.copilot.enable": {
                            "*": True,
                            "yaml": True,
                            "plaintext": False,
                            "markdown": True
                        }
                    }
                    
                    import json
                    if settings_file.exists():
                        # Merge with existing settings
                        with open(settings_file, 'r') as f:
                            existing = json.load(f)
                        existing.update(settings)
                        settings = existing
                    
                    with open(settings_file, 'w') as f:
                        json.dump(settings, f, indent=2)
                    
                    results.append("✓ Created .vscode/settings.json with CodeSentinel config")
                else:
                    results.append("✗ VS Code 'code' command not found")
            except Exception as e:
                results.append(f"✗ Failed to configure VS Code: {e}")
        
        # Show results if any
        if results:
            messagebox.showinfo("Copilot Integration", "\n".join(results))
    
    def _generate_copilot_instructions(self, install_path: Path):
        """Generate GitHub Copilot instructions file."""
        github_dir = install_path / ".github"
        github_dir.mkdir(exist_ok=True)
        
        instructions_file = github_dir / "copilot-instructions.md"
        
        instructions_content = """# CodeSentinel AI Agent Instructions

CodeSentinel is a security-first automated maintenance and monitoring system with the core principle: **SECURITY > EFFICIENCY > MINIMALISM**.

## Architecture Overview

The codebase follows a dual-architecture pattern:

- **`codesentinel/`** - Core Python package with CLI interface (`codesentinel`, `codesentinel-setup`)
- **`tools/codesentinel/`** - Comprehensive maintenance automation scripts
- **`tools/config/`** - JSON configuration files for alerts, scheduling, and policies
- **`tests/`** - Test suite using pytest with unittest fallback

## Key Commands

### Development Audit
```bash
# Run interactive audit
codesentinel !!!!

# Get agent-friendly context for remediation
codesentinel !!!! --agent
```

### Maintenance Operations
```bash
# Daily maintenance workflow
python tools/codesentinel/scheduler.py --schedule daily

# Weekly maintenance (security, dependencies, performance)
python tools/codesentinel/scheduler.py --schedule weekly
```

## Core Principles

### SECURITY
- No hardcoded credentials - Environment variables or config files only
- Audit logging - All operations logged with timestamps
- Configuration validation - Auto-creation of missing configs with secure defaults
- Dependency scanning - Automated vulnerability detection

### EFFICIENCY
- Avoid redundant code and duplicate implementations
- Consolidate multiple versions of similar functionality
- Clean up orphaned test files and unused scripts
- Optimize import structures and module organization

### MINIMALISM
- Remove unnecessary dependencies
- Archive deprecated code to quarantine_legacy_archive/
- Maintain single source of truth for each feature
- Keep codebase focused and maintainable

## Persistent Policies

When working with this codebase:

1. **NON-DESTRUCTIVE**: Never delete code without archiving first
2. **FEATURE PRESERVATION**: All existing functionality must be maintained
3. **STYLE PRESERVATION**: Respect existing code style and patterns
4. **SECURITY FIRST**: Security concerns always take priority

## Agent-Driven Remediation

When `codesentinel !!!! --agent` is run, you will receive comprehensive audit context with:

- Detected issues (security, efficiency, minimalism)
- Remediation hints with priority levels
- Safe-to-automate vs. requires-review flags
- Step-by-step suggested actions

Your role is to:

1. **ANALYZE**: Review each issue with full context
2. **PRIORITIZE**: Focus on critical/high priority items first  
3. **DECIDE**: Determine safe vs. requires-review actions
4. **PLAN**: Build step-by-step remediation plan
5. **EXECUTE**: Only perform safe, non-destructive operations
6. **REPORT**: Document all actions and decisions

## Safe Actions (can automate)

- Moving test files to proper directories
- Adding entries to .gitignore
- Removing __pycache__ directories
- Archiving confirmed-redundant files to quarantine_legacy_archive/

## Requires Review (agent decision needed)

- Deleting or archiving potentially-used code
- Consolidating multiple implementations
- Removing packaging configurations
- Modifying imports or entry points

## Forbidden Actions

- Deleting files without archiving
- Forcing code style changes
- Removing features without verification
- Modifying core functionality without explicit approval

## Integration Points

### GitHub Integration
- Repository-aware configuration detection
- Copilot instructions generation (this file)
- PR review automation capabilities

### Multi-Platform Support  
- Python 3.13/3.14 requirement with backward compatibility
- Cross-platform paths using `pathlib.Path` consistently
- PowerShell/Python dual execution support for Windows/Unix

## When Modifying This Codebase

1. **Understand the dual architecture** - Core package vs. tools scripts serve different purposes
2. **Maintain execution order** - Change detection dependency is critical
3. **Preserve configuration structure** - JSON configs have specific schemas
4. **Test both execution paths** - pytest and unittest must both work
5. **Follow security-first principle** - Never compromise security for convenience
6. **Update timeout values carefully** - Task timeouts affect workflow reliability
"""
        
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions_content)


def main():
    app = WizardApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
