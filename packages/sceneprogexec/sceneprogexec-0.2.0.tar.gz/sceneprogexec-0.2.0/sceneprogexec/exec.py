import os
import subprocess
import shutil
import platform
import re
from pathlib import Path

def _is_executable(p: Path) -> bool:
    return p.is_file() and os.access(str(p), os.X_OK)

def _read_blender_version_folder(base: Path) -> str | None:
    """
    Blender bundle layout examples:
      macOS:   .../Blender.app/Contents/Resources/<ver>/python/bin/python3.x
      Linux:   .../blender-<ver>-linux-x64/<ver>/python/bin/python3.x
    We return the highest-looking <ver> present (e.g., '4.3' or '3.6').
    """
    candidates = []
    for child in (base.iterdir() if base.exists() else []):
        m = re.fullmatch(r"(\d+\.\d+)", child.name)  # '4.3', '3.6', '2.93'
        if m and child.is_dir():
            candidates.append((tuple(map(int, m.group(1).split("."))), m.group(1)))
    if not candidates:
        return None
    # pick the highest numeric version (e.g., 4.3 > 3.6 > 2.93)
    candidates.sort()
    return candidates[-1][1]

def _guess_python_binary(version_dir: Path) -> Path | None:
    """
    Inside <base>/<ver>/python/bin/ the binary is typically python3.x.
    We pick any python3* present, preferring the highest minor.
    """
    bin_dir = version_dir / "python" / "bin"
    if not bin_dir.is_dir():
        return None
    pybins = sorted([p for p in bin_dir.iterdir() if p.name.startswith("python3") and _is_executable(p)])
    if not pybins:
        return None
    # prefer higher minor, e.g. python3.11 over python3.10
    pybins.sort(key=lambda p: tuple(map(int, re.findall(r"\d+", p.name))), reverse=True)
    return pybins[0]

class BlenderPythonDetector:
    def __init__(self):
        pass

    def find_blender_path(self) -> str | None:
        # 1) Respect env var first
        env_path = os.environ.get("BLENDER_PATH")
        if env_path and _is_executable(Path(env_path)):
            return env_path

        system = platform.system()
        if system == "Darwin":
            mac_exec = Path("/Applications/Blender.app/Contents/MacOS/Blender")
            if _is_executable(mac_exec):
                return str(mac_exec)

        elif system == "Linux":
            # Try PATH
            which = shutil.which("blender")
            if which and _is_executable(Path(which)):
                return which

            # Try common locations
            common = [
                "/usr/bin/blender",
                "/usr/local/bin/blender",
                "/snap/bin/blender",
            ]
            for c in common:
                if _is_executable(Path(c)):
                    return c

            # Try portable folder pattern the user provided
            # e.g. /kunal/vlmaterial/blender-3.6.0-linux-x64/blender
            portable = Path.home()  # fallback search anchor if you like
            # If you know exact path, env would have caught it; here we just fail gracefully
            # (We won't recursively scan disks to avoid being slow.)
            # User can still set BLENDER_PATH explicitly.

        print("Blender executable not found. Set BLENDER_PATH to your Blender binary.")
        return None

    def find_blender_python_path(self, blender_path: str | None) -> str | None:
        # 1) Respect env var first
        env_py = os.environ.get("BLENDER_PYTHON")
        if env_py and _is_executable(Path(env_py)):
            return env_py

        if not blender_path:
            return None

        system = platform.system()
        bpath = Path(blender_path)

        if system == "Darwin":
            # /Applications/Blender.app/Contents/MacOS/Blender
            contents = bpath.parent  # .../Contents/MacOS
            resources = contents.parent / "Resources"
            ver = _read_blender_version_folder(resources)
            if not ver:
                return None
            pybin = _guess_python_binary(resources / ver)
            return str(pybin) if pybin else None

        elif system == "Linux":
            """
            Portable layout:
              .../blender-3.6.0-linux-x64/blender
              .../blender-3.6.0-linux-x64/3.6/python/bin/python3.10

            System package layout varies; when Blender is system-installed,
            it still bundles its own python in a sibling of the executable dir’s parent.
            We'll try the portable layout first.
            """
            base = bpath.parent  # .../blender-3.6.0-linux-x64
            ver = _read_blender_version_folder(base)
            if ver:
                pybin = _guess_python_binary(base / ver)
                if pybin:
                    return str(pybin)

            # Fallback: try calling Blender to discover the bundled python via sys.executable
            # (We run a tiny script inside Blender.)
            try:
                code = "import sys; print(sys.executable)"
                out = subprocess.run(
                    [blender_path, "--background", "--python-expr", code],
                    check=True, capture_output=True, text=True,
                )
                candidate = out.stdout.strip().splitlines()[-1].strip()
                if candidate and Path(candidate).exists():
                    return candidate
            except Exception:
                pass

            return None

        else:
            # Windows or other: not implemented here, but we won't break.
            return None

class SceneProgExec:
    def __init__(self, caller_path: str | None = None):
        """
        caller_path: str - Path to the caller script
        """
        self.caller_path = caller_path
        detector = BlenderPythonDetector()
        self.blender_path = detector.find_blender_path()
        self.blender_python = detector.find_blender_python_path(self.blender_path)

        # Helpful diagnostics
        problems = []
        if not self.blender_path:
            problems.append("BLENDER_PATH not found or not executable.")
        if not self.blender_python:
            problems.append("BLENDER_PYTHON not found or not executable.")

        if problems:
            msg = f"""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Could not resolve Blender and/or its bundled Python.

Diagnostics:
- BLENDER_PATH: {os.environ.get('BLENDER_PATH') or '(not set)'}
- BLENDER_PYTHON: {os.environ.get('BLENDER_PYTHON') or '(not set)'}
- Detected blender_path: {self.blender_path or '(none)'}
- Detected blender_python: {self.blender_python or '(none)'}
- Platform: {platform.system()}

Tips:
- macOS:
  export BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/Blender"
  export BLENDER_PYTHON="/Applications/Blender.app/Contents/Resources/<ver>/python/bin/python3.x"

- Linux (portable tarball like yours):
  export BLENDER_PATH="/kunal/vlmaterial/blender-3.6.0-linux-x64/blender"
  export BLENDER_PYTHON="/kunal/vlmaterial/blender-3.6.0-linux-x64/3.6/python/bin/python3.10"

- Make sure the Blender binary is executable: chmod +x "$BLENDER_PATH"

If Blender still fails to start in Docker with 'libXfixes.so.3' or similar,
install X11/OpenGL runtime libs (Debian/Ubuntu):
  apt-get update && apt-get install -y \\
    libxfixes3 libxi6 libxrender1 libgl1-mesa-glx libxkbcommon0 \\
    libx11-6 libxext6 libxtst6 libxcursor1 libxdamage1 libxrandr2 \\
    libxcb1 libxau6 libxdmcp6 libxss1 libsm6 libice6 libglu1-mesa \\
    libsdl2-2.0-0 libopenal1 libgomp1 libfftw3-3 libpng16-16 zlib1g
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""
            raise RuntimeError(msg)

        # Extract Blender *major.minor* version from the python path for user_modules
        # We look for '/<ver>/python/' pattern.
        m = re.search(r"[/\\]((\d+\.\d+))/python[/\\]", self.blender_python)
        blender_version = m.group(1) if m else "3.6"
        if platform.system() == "Darwin":
            self.user_modules = os.path.expanduser(
                f"~/Library/Application Support/Blender/{blender_version}/scripts/modules"
            )
        else:
            # Linux user scripts path
            self.user_modules = os.path.expanduser(
                f"~/.config/blender/{blender_version}/scripts/modules"
            )

    def __call__(self, script: str, target: str | None = None, verbose: bool = False):
        location = os.getcwd()
        random_uid = f"{int.from_bytes(os.urandom(4), 'big')}"
        tmp_script_path = os.path.join(location, f"{random_uid}.py")
        with open(tmp_script_path, "w") as f:
            f.write(script)

        try:
            output = self.run_script(tmp_script_path, target=target, verbose=verbose)
        finally:
            if os.path.exists(tmp_script_path):
                os.remove(tmp_script_path)
        return output

    def run_script(self, script_path: str, target: str | None = None, verbose: bool = False):
        script_abs = os.path.abspath(script_path)
        script_dir = os.path.dirname(script_abs)
        log_name = os.path.basename(script_path).replace(".py", ".log")
        self.log_path = os.path.join(script_dir, log_name)

        with open(script_path, "r") as f:
            script = f.read()

        code = f"import sys\nsys.path.append({script_dir!r})\n{script}\n"
        if target:
            code += f"\nimport bpy\nbpy.ops.wm.save_mainfile(filepath={os.path.abspath(target)!r})\n"
        if self.caller_path:
            code = f"import sys\nsys.path.append({self.caller_path!r})\n{code}"

        self.tmp_exec_path = script_abs.replace(".py", "_exec.py")
        with open(self.tmp_exec_path, "w") as f:
            f.write(code)

        if verbose:
            print(f"🚀 Running {script_path} in Blender (via wrapper)")

        # Use subprocess with proper args; capture stderr to file
        with open(self.log_path, "w") as logf:
            proc = subprocess.run(
                [self.blender_path, "--background", "--python", self.tmp_exec_path],
                cwd=script_dir,
                stdout=logf, stderr=subprocess.STDOUT, text=True
            )

        with open(self.log_path, "r") as log_file:
            blender_output = log_file.read().strip()

        self.cleanup()
        if verbose:
            print(blender_output)

        # Surface failure reason if Blender returned nonzero
        if proc.returncode != 0:
            raise RuntimeError(
                f"Blender exited with code {proc.returncode}. See log at {self.log_path}.\n\n{blender_output}"
            )

        return blender_output

    def cleanup(self):
        for p in [getattr(self, "tmp_exec_path", None), getattr(self, "log_path", None)]:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    def install_packages(self, packages, hard_reset=False):
        """Installs Python packages inside Blender's environment."""
        if hard_reset:
            print("\n🔄 Performing Hard Reset...\n")
            self._delete_all_third_party_packages()
            self._delete_user_modules()

        self.log_path = os.path.join(os.getcwd(), "blender_pip_log.txt")
        for package in packages:
            print(f"📦 Installing {package} inside Blender's Python...")
            with open(self.log_path, "w") as logf:
                subprocess.run(
                    [self.blender_python, "-m", "pip", "install", package, "--force"],
                    stdout=logf, stderr=subprocess.STDOUT, text=True
                )
            with open(self.log_path, "r") as log_file:
                print(log_file.read())

        print("✅ All packages installed.")
        try:
            os.remove(self.log_path)
        except Exception:
            pass

    def _delete_all_third_party_packages(self):
        """Deletes all third-party packages from Blender's site-packages."""
        try:
            result = subprocess.run(
                [self.blender_python, "-m", "pip", "freeze"],
                capture_output=True, text=True
            )
            packages = [line.split("==")[0] for line in result.stdout.splitlines() if line]
            if not packages:
                print("✅ No third-party packages found.")
                return

            print(f"🗑️ Removing {len(packages)} third-party packages...")
            subprocess.run(
                [self.blender_python, "-m", "pip", "uninstall", "-y", *packages],
                text=True
            )
            print("✅ All third-party packages removed.")
        except Exception as e:
            print(f"⚠️ Error removing packages: {e}")

    def _delete_user_modules(self):
        """Deletes all user-installed packages from Blender's user module directory."""
        if os.path.exists(self.user_modules):
            try:
                shutil.rmtree(self.user_modules)
                print(f"🗑️ Deleted all modules in {self.user_modules}")
            except Exception as e:
                print(f"⚠️ Could not delete user modules: {e}")
        else:
            print(f"✅ No user modules found in {self.user_modules}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SceneProgExec CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: install packages
    install_parser = subparsers.add_parser("install", help="Install packages inside Blender's Python")
    install_parser.add_argument("packages", nargs="+")
    install_parser.add_argument("--reset", action="store_true")

    # Subcommand: run a script
    run_parser = subparsers.add_parser("run", help="Run a Python script inside Blender and save as a .blend file")
    run_parser.add_argument("script_path")
    run_parser.add_argument("--target", required=False, help="Path to save the resulting .blend file")
    run_parser.add_argument("--verbose", action="store_true")

    # Subcommand: reset
    subparsers.add_parser("reset", help="Reset all third-party packages and user modules")
    args = parser.parse_args()

    executor = SceneProgExec()
    if args.command == "install":
        executor.install_packages(args.packages, hard_reset=args.reset)
    elif args.command == "run":
        _ = executor.run_script(args.script_path, target=args.target, verbose=args.verbose)
    elif args.command == "reset":
        executor._delete_all_third_party_packages()

if __name__ == "__main__":
    main()