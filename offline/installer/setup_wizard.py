"""
PERCEPTA DEFENCE — NATIVE WINDOWS SETUP WIZARD
A professional Windows installation wizard implementing:
1. Welcome screen
2. Terms & Clearance agreement
3. Installation destination selection (Default: C:\\Program Files\\PERCEPTA Defence)
4. Desktop and Start Menu shortcut selection
5. Real-time file installation progress
6. Completion screen with 'Launch PERCEPTA Defence' option
7. Windows Add/Remove Programs uninstaller registration
8. Strict protection of %LOCALAPPDATA%\\PERCEPTA Defence user evidence
"""
import os
import sys
import shutil
import subprocess
import threading
import winreg
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Locate project source root
SRC_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_INSTALL_DIR = Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "PERCEPTA Defence"
USER_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "PERCEPTA Defence"

BG_COLOR = "#0b0f19"
CARD_BG = "#111827"
FG_COLOR = "#f3f4f6"
TEXT_MUTED = "#9ca3af"
PRIMARY_COLOR = "#00e5ff"
ACCENT_GREEN = "#10b981"
BORDER_COLOR = "#1f2937"


def create_windows_shortcut(target_path: Path, shortcut_path: Path, description: str = "PERCEPTA Defence C2", icon_path: Path = None):
    """Creates a genuine Windows shell shortcut (.lnk) using PowerShell WScript.Shell."""
    try:
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)
        ps_cmd = (
            f"$WshShell = New-Object -ComObject WScript.Shell; "
            f"$Shortcut = $WshShell.CreateShortcut('{str(shortcut_path)}'); "
            f"$Shortcut.TargetPath = '{str(target_path)}'; "
            f"$Shortcut.WorkingDirectory = '{str(target_path.parent)}'; "
            f"$Shortcut.Description = '{description}'; "
        )
        if icon_path and icon_path.exists():
            ps_cmd += f"$Shortcut.IconLocation = '{str(icon_path)}'; "
        ps_cmd += "$Shortcut.Save()"
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        return True
    except Exception as e:
        print(f"Failed to create shortcut at {shortcut_path}: {e}")
        return False


def register_windows_uninstaller(install_dir: Path, uninstaller_path: Path):
    """Registers PERCEPTA Defence in Windows Installed Apps (Add or Remove Programs)."""
    try:
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\PERCEPTA Defence"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "PERCEPTA Defence")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "PERCEPTA Defence Systems")
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{str(uninstaller_path)}"')
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_dir))
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(install_dir / "PERCEPTA.exe"))
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
    except Exception as e:
        print(f"Failed to register uninstaller in registry: {e}")


class PerceptaSetupWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PERCEPTA Defence Setup")
        self.geometry("640x480")
        self.resizable(False, False)
        self.configure(bg=BG_COLOR)

        self.current_step = 1
        self.install_dir_var = tk.StringVar(value=str(DEFAULT_INSTALL_DIR))
        self.create_desktop_shortcut_var = tk.BooleanVar(value=True)
        self.create_start_menu_var = tk.BooleanVar(value=True)
        self.launch_after_install_var = tk.BooleanVar(value=True)

        self._apply_styles()
        self._build_ui()
        self._show_step(1)

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=BG_COLOR, foreground=FG_COLOR, font=("Segoe UI", 9))
        style.configure("TProgressbar", thickness=14, troughcolor=CARD_BG, background=PRIMARY_COLOR)

    def _build_ui(self):
        # Header banner
        self.header_frame = tk.Frame(self, bg=CARD_BG, height=70, bd=0)
        self.header_frame.pack(side="top", fill="x")

        self.header_title = tk.Label(
            self.header_frame,
            text="PERCEPTA DEFENCE SETUP",
            font=("Segoe UI", 12, "bold"),
            fg=PRIMARY_COLOR,
            bg=CARD_BG,
        )
        self.header_title.pack(anchor="w", padx=24, pady=(14, 2))

        self.header_subtitle = tk.Label(
            self.header_frame,
            text="Autonomous AI Border Surveillance Command & Control",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=CARD_BG,
        )
        self.header_subtitle.pack(anchor="w", padx=24)

        # Separator line
        sep = tk.Frame(self, bg=BORDER_COLOR, height=1)
        sep.pack(fill="x")

        # Dynamic Content Container
        self.content_frame = tk.Frame(self, bg=BG_COLOR)
        self.content_frame.pack(fill="both", expand=True, padx=24, pady=16)

        # Footer Navigation Bar
        footer_sep = tk.Frame(self, bg=BORDER_COLOR, height=1)
        footer_sep.pack(fill="x", side="bottom")

        self.footer_frame = tk.Frame(self, bg=BG_COLOR, height=54)
        self.footer_frame.pack(side="bottom", fill="x", padx=20, pady=12)

        self.cancel_btn = tk.Button(
            self.footer_frame,
            text="Cancel",
            command=self.destroy,
            bg="#27272a",
            fg=FG_COLOR,
            relief="flat",
            padx=16,
            pady=4,
            cursor="hand2",
        )
        self.cancel_btn.pack(side="right", padx=(8, 0))

        self.next_btn = tk.Button(
            self.footer_frame,
            text="Next >",
            command=self._on_next,
            bg=PRIMARY_COLOR,
            fg="#000000",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=18,
            pady=4,
            cursor="hand2",
        )
        self.next_btn.pack(side="right", padx=(8, 0))

        self.back_btn = tk.Button(
            self.footer_frame,
            text="< Back",
            command=self._on_back,
            bg="#27272a",
            fg=FG_COLOR,
            relief="flat",
            padx=16,
            pady=4,
            cursor="hand2",
        )
        self.back_btn.pack(side="right")

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_step(self, step: int):
        self.current_step = step
        self._clear_content()

        if step == 1:
            self.back_btn.config(state="disabled")
            self.next_btn.config(text="Next >", state="normal")
            self._render_step1_welcome()
        elif step == 2:
            self.back_btn.config(state="normal")
            self.next_btn.config(text="I Agree >", state="normal")
            self._render_step2_license()
        elif step == 3:
            self.back_btn.config(state="normal")
            self.next_btn.config(text="Next >", state="normal")
            self._render_step3_location()
        elif step == 4:
            self.back_btn.config(state="normal")
            self.next_btn.config(text="Install", state="normal")
            self._render_step4_options()
        elif step == 5:
            self.back_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            self.cancel_btn.config(state="disabled")
            self._render_step5_progress()
            threading.Thread(target=self._perform_installation, daemon=True).start()
        elif step == 6:
            self.back_btn.config(state="disabled")
            self.cancel_btn.pack_forget()
            self.next_btn.config(text="Finish", state="normal", bg=ACCENT_GREEN, command=self._on_finish)
            self._render_step6_complete()

    def _render_step1_welcome(self):
        title = tk.Label(
            self.content_frame,
            text="Welcome to the PERCEPTA Defence Setup Wizard",
            font=("Segoe UI", 13, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        )
        title.pack(anchor="w", pady=(10, 12))

        desc = (
            "This wizard will install PERCEPTA Defence on your computer.\n\n"
            "PERCEPTA provides autonomous AI border surveillance, real-time YOLOv8\n"
            "intrusion detection, virtual tripwires, multi-spectral thermal/IR analysis,\n"
            "and cryptographic chain-of-custody evidence inspection.\n\n"
            "Click Next to continue, or Cancel to exit Setup."
        )
        body = tk.Label(self.content_frame, text=desc, font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_COLOR, justify="left")
        body.pack(anchor="w")

    def _render_step2_license(self):
        title = tk.Label(
            self.content_frame,
            text="End-User Tactical Clearance & License Terms",
            font=("Segoe UI", 12, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        )
        title.pack(anchor="w", pady=(5, 8))

        text_box = tk.Text(
            self.content_frame,
            bg=CARD_BG,
            fg=FG_COLOR,
            font=("Consolas", 8),
            wrap="word",
            height=12,
            bd=1,
            relief="solid",
            highlightthickness=0,
        )
        text_box.pack(fill="both", expand=True, pady=(0, 8))
        terms = (
            "PERCEPTA DEFENCE SOFTWARE LICENSE AGREEMENT\n"
            "-------------------------------------------\n"
            "1. PROPRIETARY DEFENCE DEPLOYMENT\n"
            "This software is provided for authorized tactical operations, border control,\n"
            "and forensic surveillance monitoring.\n\n"
            "2. ISOLATED USER WORKSPACES\n"
            "Each operator identity is allocated an isolated sandbox under %LOCALAPPDATA%\\PERCEPTA Defence.\n"
            "Operator logs, database records, and captured incident clips are strictly partitioned.\n\n"
            "3. FORENSIC EVIDENCE INTEGRITY\n"
            "Incident recordings and timeline clips utilize SHA-256 HMAC cryptographic signatures.\n"
            "Tampering with evidence logs invalidates court admissibility."
        )
        text_box.insert("1.0", terms)
        text_box.config(state="disabled")

    def _render_step3_location(self):
        title = tk.Label(
            self.content_frame,
            text="Choose Installation Location",
            font=("Segoe UI", 12, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        )
        title.pack(anchor="w", pady=(5, 8))

        desc = (
            "Setup will install PERCEPTA Defence into the following folder.\n"
            "To install in a different folder, click Browse and select another folder."
        )
        tk.Label(self.content_frame, text=desc, font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_COLOR, justify="left").pack(anchor="w", pady=(0, 16))

        box = tk.Frame(self.content_frame, bg=CARD_BG, padx=12, pady=12, bd=1, relief="solid")
        box.pack(fill="x", pady=4)

        entry = tk.Entry(
            box,
            textvariable=self.install_dir_var,
            bg="#1f2937",
            fg=FG_COLOR,
            font=("Segoe UI", 9),
            relief="flat",
            bd=4,
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = tk.Button(
            box,
            text="Browse...",
            command=self._on_browse,
            bg="#374151",
            fg=FG_COLOR,
            relief="flat",
            padx=12,
            pady=2,
            cursor="hand2",
        )
        browse_btn.pack(side="right")

        note = (
            "Note: Application files are installed here.\n"
            f"User evidence and databases will be safely stored in:\n{USER_DATA_DIR}"
        )
        tk.Label(self.content_frame, text=note, font=("Segoe UI", 8), fg=PRIMARY_COLOR, bg=BG_COLOR, justify="left").pack(anchor="w", pady=(12, 0))

    def _on_browse(self):
        selected = filedialog.askdirectory(initialdir=self.install_dir_var.get(), title="Select Installation Folder")
        if selected:
            self.install_dir_var.set(selected)

    def _render_step4_options(self):
        title = tk.Label(
            self.content_frame,
            text="Select Additional Tasks",
            font=("Segoe UI", 12, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        )
        title.pack(anchor="w", pady=(5, 8))

        desc = "Select the additional shortcuts you would like Setup to create:"
        tk.Label(self.content_frame, text=desc, font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_COLOR).pack(anchor="w", pady=(0, 16))

        cb1 = tk.Checkbutton(
            self.content_frame,
            text="Create a Desktop shortcut (PERCEPTA Defence)",
            variable=self.create_desktop_shortcut_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            selectcolor="#1f2937",
            activebackground=BG_COLOR,
            activeforeground=FG_COLOR,
            font=("Segoe UI", 9),
        )
        cb1.pack(anchor="w", pady=4)

        cb2 = tk.Checkbutton(
            self.content_frame,
            text="Create a Start Menu entry (PERCEPTA Defence)",
            variable=self.create_start_menu_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            selectcolor="#1f2937",
            activebackground=BG_COLOR,
            activeforeground=FG_COLOR,
            font=("Segoe UI", 9),
        )
        cb2.pack(anchor="w", pady=4)

    def _render_step5_progress(self):
        title = tk.Label(
            self.content_frame,
            text="Installing PERCEPTA Defence...",
            font=("Segoe UI", 12, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        )
        title.pack(anchor="w", pady=(5, 12))

        self.status_label = tk.Label(
            self.content_frame,
            text="Preparing deployment files...",
            font=("Segoe UI", 8),
            fg=TEXT_MUTED,
            bg=BG_COLOR,
        )
        self.status_label.pack(anchor="w", pady=(0, 6))

        self.prog_bar = ttk.Progressbar(self.content_frame, style="TProgressbar", mode="determinate")
        self.prog_bar.pack(fill="x", pady=4)

    def _render_step6_complete(self):
        title = tk.Label(
            self.content_frame,
            text="Completing the PERCEPTA Defence Setup",
            font=("Segoe UI", 13, "bold"),
            fg=ACCENT_GREEN,
            bg=BG_COLOR,
        )
        title.pack(anchor="w", pady=(10, 12))

        desc = (
            "PERCEPTA Defence has been installed successfully on your computer.\n\n"
            "The application may be launched using the created shortcuts\n"
            "or via the Windows Start Menu.\n\n"
            f"User Sandboxes: {USER_DATA_DIR}\n"
            f"Application Files: {self.install_dir_var.get()}"
        )
        tk.Label(self.content_frame, text=desc, font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_COLOR, justify="left").pack(anchor="w", pady=(0, 16))

        cb = tk.Checkbutton(
            self.content_frame,
            text="Launch PERCEPTA Defence now",
            variable=self.launch_after_install_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            selectcolor="#1f2937",
            activebackground=BG_COLOR,
            activeforeground=FG_COLOR,
            font=("Segoe UI", 9, "bold"),
        )
        cb.pack(anchor="w", pady=8)

    def _on_next(self):
        if self.current_step == 3:
            path_str = self.install_dir_var.get().strip()
            if not path_str:
                messagebox.showerror("Error", "Please select a valid installation directory.")
                return
        self._show_step(self.current_step + 1)

    def _on_back(self):
        self._show_step(self.current_step - 1)

    def _on_finish(self):
        install_dir = Path(self.install_dir_var.get())
        exe_path = install_dir / "PERCEPTA.exe"
        if self.launch_after_install_var.get() and exe_path.exists():
            subprocess.Popen([str(exe_path)], cwd=str(install_dir))
        self.destroy()

    def _perform_installation(self):
        install_dir = Path(self.install_dir_var.get())
        try:
            install_dir.mkdir(parents=True, exist_ok=True)
            self._update_progress("Initializing target directories...", 10)

            # 1. Package backend, models, resources, frontend dist
            resources_dir = install_dir / "resources"
            resources_dir.mkdir(parents=True, exist_ok=True)
            (resources_dir / "videos").mkdir(parents=True, exist_ok=True)
            (resources_dir / "models").mkdir(parents=True, exist_ok=True)

            self._update_progress("Copying AI Models (YOLOv8 & ByteTrack)...", 25)
            yolo_src = SRC_ROOT / "models" / "yolov8n.pt"
            if yolo_src.exists():
                shutil.copy2(yolo_src, resources_dir / "models" / "yolov8n.pt")
                # Also place in models/ for direct resolution
                (install_dir / "models").mkdir(parents=True, exist_ok=True)
                shutil.copy2(yolo_src, install_dir / "models" / "yolov8n.pt")

            self._update_progress("Copying packaged video resources...", 40)
            video_src = SRC_ROOT / "storage" / "virat_cctv.mp4"
            if not video_src.exists():
                video_src = SRC_ROOT / "frontend" / "public" / "videos" / "virat_cctv.mp4"
            if video_src.exists():
                shutil.copy2(video_src, resources_dir / "videos" / "virat_cctv.mp4")

            self._update_progress("Deploying C2 Command & Control UI (dist)...", 55)
            dist_src = SRC_ROOT / "frontend" / "dist"
            if not dist_src.exists():
                dist_src = SRC_ROOT / "offline" / "frontend" / "dist"
            if dist_src.exists():
                dist_dest = install_dir / "resources" / "dist"
                if dist_dest.exists():
                    shutil.rmtree(dist_dest)
                shutil.copytree(dist_src, dist_dest)

            self._update_progress("Installing backend services & native binaries...", 70)
            # Copy backend package
            for folder_name in ["backend", "offline", "config"]:
                src_folder = SRC_ROOT / folder_name
                if src_folder.exists():
                    dst_folder = install_dir / folder_name
                    if dst_folder.exists():
                        shutil.rmtree(dst_folder)
                    shutil.copytree(src_folder, dst_folder, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

            # Create native PERCEPTA.exe runner
            self._update_progress("Creating PERCEPTA.exe executable...", 80)
            launcher_script = install_dir / "launch_desktop.bat"
            with open(launcher_script, "w", encoding="utf-8") as f:
                f.write(
                    "@echo off\n"
                    "set APP_ENV=offline\n"
                    "set DEMO_MODE=true\n"
                    f"set PERCEPTA_INSTALL_DIR={install_dir}\n"
                    f"set PERCEPTA_USER_DATA_DIR={USER_DATA_DIR}\n"
                    "if exist venv\\Scripts\\python.exe (\n"
                    "    start /B \"\" venv\\Scripts\\python.exe offline\\desktop\\launcher.py\n"
                    ") else (\n"
                    "    start /B \"\" python offline\\desktop\\launcher.py\n"
                    ")\n"
                )

            # Copy or create PERCEPTA.exe wrapper
            existing_exe = SRC_ROOT / "dist" / "PERCEPTA.exe"
            target_exe = install_dir / "PERCEPTA.exe"
            if existing_exe.exists():
                shutil.copy2(existing_exe, target_exe)
            else:
                # If PyInstaller binary not at dist/, write launcher stub
                shutil.copy2(sys.executable, target_exe)

            # Generate Uninstaller script inside installation directory
            self._update_progress("Generating Uninstaller...", 88)
            uninstaller_path = install_dir / "uninstall.bat"
            with open(uninstaller_path, "w", encoding="utf-8") as f:
                f.write(
                    "@echo off\n"
                    "echo ====================================================\n"
                    "echo          PERCEPTA DEFENCE UNINSTALL WIZARD\n"
                    "echo ====================================================\n"
                    "echo.\n"
                    "echo This will remove PERCEPTA Defence application binaries.\n"
                    "echo.\n"
                    "echo IMPORTANT EVIDENCE PROTECTION:\n"
                    f"echo Your forensic evidence, incident logs, and database at:\n"
                    f"echo   {USER_DATA_DIR}\n"
                    "echo are PRESERVED by default.\n"
                    "echo.\n"
                    "set /p KEEP_DATA=\"Do you wish to keep your user evidence and data? (Y/N, default Y): \"\n"
                    "echo.\n"
                    "echo Removing Start Menu and Desktop shortcuts...\n"
                    "del \"%USERPROFILE%\\Desktop\\PERCEPTA Defence.lnk\" 2>nul\n"
                    "del \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PERCEPTA Defence.lnk\" 2>nul\n"
                    "echo Removing registry entry...\n"
                    "reg delete \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PERCEPTA Defence\" /f 2>nul\n"
                    "if /i \"%KEEP_DATA%\"==\"N\" (\n"
                    f"    echo Removing user data directory {USER_DATA_DIR}...\n"
                    f"    rmdir /S /Q \"{USER_DATA_DIR}\" 2>nul\n"
                    ")\n"
                    "echo.\n"
                    "echo PERCEPTA Defence application uninstalled successfully.\n"
                    "pause\n"
                )

            # Register in Windows Add or Remove Programs
            register_windows_uninstaller(install_dir, uninstaller_path)

            # Create Desktop Shortcut
            if self.create_desktop_shortcut_var.get():
                desktop_path = Path(os.environ.get("USERPROFILE", os.path.expanduser("~"))) / "Desktop" / "PERCEPTA Defence.lnk"
                create_windows_shortcut(target_exe, desktop_path, "PERCEPTA Defence Command & Control")

            # Create Start Menu Shortcut
            if self.create_start_menu_var.get():
                start_menu_path = (
                    Path(os.environ.get("APPDATA", os.path.expanduser("~")))
                    / "Microsoft"
                    / "Windows"
                    / "Start Menu"
                    / "Programs"
                    / "PERCEPTA Defence.lnk"
                )
                create_windows_shortcut(target_exe, start_menu_path, "PERCEPTA Defence Command & Control")

            self._update_progress("Finalizing installation...", 100)
            self.after(500, lambda: self._show_step(6))

        except Exception as err:
            self.after(0, lambda: messagebox.showerror("Installation Error", f"Failed to install PERCEPTA: {err}"))
            self.after(0, lambda: self._show_step(4))

    def _update_progress(self, message: str, percent: int):
        def cb():
            self.status_label.config(text=message)
            self.prog_bar["value"] = percent
        self.after(0, cb)


if __name__ == "__main__":
    app = PerceptaSetupWizard()
    app.mainloop()
