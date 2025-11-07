#!/usr/bin/env python3
"""
CodeSentinel GUI Launcher with Self-Dependency Management

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

A self-contained GUI launcher that handles its own dependency installation
and provides a 100% guided setup experience.
"""

import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
from pathlib import Path

class DependencyInstallerGUI:
    """GUI for installing dependencies with progress tracking."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CodeSentinel - Dependency Setup")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the dependency installer UI."""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ttk.Label(
            header_frame, 
            text="🚀 CodeSentinel Setup",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Installing required dependencies...",
            font=("Segoe UI", 10)
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(self.root, text="Installation Progress")
        progress_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            mode='indeterminate'
        )
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        
        self.status_label = ttk.Label(
            progress_frame,
            text="Preparing to install dependencies...",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Output log
        log_frame = ttk.LabelFrame(progress_frame, text="Installation Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            width=70,
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#212529"
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        self.install_button = ttk.Button(
            button_frame,
            text="Install Dependencies",
            command=self.start_installation
        )
        self.install_button.pack(side="left")
        
        self.skip_button = ttk.Button(
            button_frame,
            text="Skip & Continue",
            command=self.skip_installation,
            state="disabled"
        )
        self.skip_button.pack(side="left", padx=(10, 0))
        
        self.close_button = ttk.Button(
            button_frame,
            text="Close",
            command=self.root.destroy,
            state="disabled"
        )
        self.close_button.pack(side="right")
        
    def log_message(self, message):
        """Add a message to the log."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, status):
        """Update the status label."""
        self.status_label.config(text=status)
        self.root.update_idletasks()
        
    def start_installation(self):
        """Start the dependency installation process."""
        self.install_button.config(state="disabled")
        self.progress_bar.start()
        
        # Start installation in a separate thread
        thread = threading.Thread(target=self.install_dependencies)
        thread.daemon = True
        thread.start()
        
    def install_dependencies(self):
        """Install required dependencies."""
        try:
            self.update_status("Checking required dependencies...")
            self.log_message("🔍 Checking CodeSentinel dependencies...")
            
            # List of required packages
            required_packages = ["PyYAML", "keyring", "cryptography"]
            missing_packages = []
            
            # Check each package
            for package in required_packages:
                try:
                    if package == "PyYAML":
                        import yaml
                        self.log_message(f"✅ {package} - already installed")
                    elif package == "keyring":
                        import keyring
                        self.log_message(f"✅ {package} - already installed")
                    elif package == "cryptography":
                        import cryptography
                        self.log_message(f"✅ {package} - already installed")
                except ImportError:
                    missing_packages.append(package)
                    self.log_message(f"❌ {package} - missing")
            
            if not missing_packages:
                self.update_status("All dependencies already installed!")
                self.log_message("\n🎉 All dependencies are available!")
                self.installation_complete(success=True)
                return
            
            # Install missing packages
            self.update_status(f"Installing {len(missing_packages)} missing packages...")
            self.log_message(f"\n📦 Installing {len(missing_packages)} packages: {', '.join(missing_packages)}")
            
            for i, package in enumerate(missing_packages, 1):
                self.update_status(f"Installing {package} ({i}/{len(missing_packages)})...")
                self.log_message(f"\n🔧 Installing {package}...")
                
                # Run pip install
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_message(f"✅ {package} installed successfully")
                else:
                    self.log_message(f"❌ Failed to install {package}")
                    self.log_message(f"Error: {result.stderr}")
                    self.installation_complete(success=False)
                    return
            
            self.update_status("Verifying installation...")
            self.log_message("\n🔍 Verifying installation...")
            
            # Verify all packages are now available
            all_installed = True
            for package in required_packages:
                try:
                    if package == "PyYAML":
                        import yaml
                    elif package == "keyring":
                        import keyring
                    elif package == "cryptography":
                        import cryptography
                    self.log_message(f"✅ {package} - verified")
                except ImportError:
                    self.log_message(f"❌ {package} - verification failed")
                    all_installed = False
            
            if all_installed:
                self.log_message("\n🎉 All dependencies installed and verified!")
                self.update_status("Installation complete!")
                self.installation_complete(success=True)
            else:
                self.log_message("\n❌ Some packages failed verification")
                self.installation_complete(success=False)
                
        except Exception as e:
            self.log_message(f"\n💥 Installation error: {e}")
            self.installation_complete(success=False)
    
    def installation_complete(self, success):
        """Handle installation completion."""
        self.progress_bar.stop()
        
        if success:
            self.install_button.config(text="✅ Complete", state="disabled")
            self.skip_button.config(text="Launch Wizard", state="normal")
            self.close_button.config(state="normal")
        else:
            self.install_button.config(text="❌ Failed", state="disabled")
            self.skip_button.config(text="Continue Anyway", state="normal")
            self.close_button.config(state="normal")
    
    def skip_installation(self):
        """Skip installation and show next steps."""
        self.root.destroy()
        
        # Show informational message about next steps
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        # Destroy the temporary root BEFORE launching the main wizard to avoid multiple Tk roots
        root.destroy()
        
        try:
            # Prefer the new modular wizard if available
            try:
                from .gui_wizard_v2 import main as wizard_main
                wizard_main()
            except Exception:
                from .gui_project_setup import main as project_setup_main
                project_setup_main()
        except Exception as e:
            messagebox.showerror(
                "CodeSentinel Setup",
                "Could not launch the project setup wizard.\n\n"
                f"Error: {e}\n\n"
                "You can run it manually later with:\n"
                "  - codesentinel-setup-gui\n"
                "  - python -m codesentinel.cli setup --gui"
            )
    
    def launch_main_wizard(self):
        """Show completion message with next steps."""
        self.root.destroy()
        
        # Show completion message
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        messagebox.showinfo(
            "Dependencies Installed!", 
            "✅ All dependencies installed successfully!\n\n"
            "Next steps:\n"
            "1. Navigate to your project directory\n"
            "2. Run: codesentinel-setup\n\n"
            "Or to create a new CodeSentinel project:\n"
            "1. Create a new directory for your project\n"
            "2. Run: codesentinel-setup in that directory"
        )
        root.destroy()

def check_and_install_dependencies():
    """Check dependencies and show installer GUI if needed."""
    try:
        # Quick check of required packages
        import yaml
        import keyring
        import cryptography
        
        # All dependencies available, launch wizard directly
        print("✅ All dependencies available, launching wizard...")
        return launch_wizard_directly()
        
    except ImportError:
        # Show dependency installer GUI
        print("🔧 Missing dependencies detected, launching installer...")
        app = DependencyInstallerGUI()
        app.root.mainloop()

def launch_wizard_directly():
    """Show next steps when dependencies are available."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    # Destroy the temporary root BEFORE launching the main wizard to avoid multiple Tk roots
    root.destroy()
    
    try:
        # Prefer the new modular wizard if available
        try:
            from .gui_wizard_v2 import main as wizard_main
            wizard_main()
        except Exception as e:
            from .gui_project_setup import main as project_setup_main
            project_setup_main()
    except Exception as e:
        messagebox.showerror(
            "CodeSentinel Setup",
            "Could not launch the project setup wizard.\n\n"
            f"Error: {e}\n\n"
            "You can run it manually later with:\n"
            "  - codesentinel-setup-gui\n"
            "  - python -m codesentinel.cli setup --gui"
        )

def main():
    """Main entry point for GUI launcher."""
    print("🚀 CodeSentinel GUI Dependency Installer")
    print("Created by: joediggidyyy")
    print("Architecture: SECURITY > EFFICIENCY > MINIMALISM")
    print("=" * 50)
    
    # This is a standalone dependency installer
    # It doesn't require being in a CodeSentinel project
    print("📦 Standalone dependency installer")
    print("💡 This installer prepares your system for CodeSentinel")
    
    try:
        check_and_install_dependencies()
        return 0
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())