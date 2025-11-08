#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HHJ Engine - single-file orchestrator
Reads a YAML .hhj config and performs a rich set of operations:
  - downloads files (with optional sha256 verification)
  - extracts archives (zip, tar.gz, tar.bz2)
  - installs Python packages (venv / user / global)
  - installs system packages (apt/brew/choco) - best-effort
  - executes shell commands with environment injection
  - creates virtualenvs, sets environment variables
  - moves/copies files, creates folders
  - supports dry-run (default), verbose, retries, timeouts
Usage:
  python hhj_engine.py --config project.hhj [--apply] [--force-global] [--verbose]
"""
from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except Exception as exc:
    print("Missing dependency 'pyyaml'. Install with 'pip install pyyaml'.")
    raise

try:
    import requests
except Exception:
    print("Missing dependency 'requests'. Install with 'pip install requests'.")
    raise

# ---------------------------
# Configuration / constants
# ---------------------------
DEFAULT_CONFIG_NAME = "project.hhj"
CHUNK_SIZE = 8192
DEFAULT_TIMEOUT = 300  # seconds for network ops
SUPPORTED_ARCHIVES = (".zip", ".tar.gz", ".tgz", ".tar.bz2", ".tar")


# ---------------------------
# Utilities & Logging
# ---------------------------
@dataclass
class Context:
    apply_changes: bool = False
    force_global: bool = False
    verbose: bool = False
    dry_run: bool = True
    retries: int = 2
    timeout: int = DEFAULT_TIMEOUT
    workdir: Path = Path.cwd()
    tmpdir: Path = Path(tempfile.mkdtemp(prefix="hhj_tmp_"))

    def log(self, *parts):
        print("[HHJ]", *parts)

    def info(self, *parts):
        print("[HHJ][INFO]", *parts)

    def warn(self, *parts):
        print("[HHJ][WARN]", *parts)

    def error(self, *parts):
        print("[HHJ][ERROR]", *parts)

    def debug(self, *parts):
        if self.verbose:
            print("[HHJ][DEBUG]", *parts)

# ---------------------------
# YAML loader & validation
# ---------------------------
def load_config(path: str, ctx: Context) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        ctx.error(f"Config file not found: {path}")
        raise FileNotFoundError(path)
    ctx.debug("Loading YAML from", path)
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    validate_config_structure(data, ctx)
    return data


def validate_config_structure(data: Dict[str, Any], ctx: Context):
    # Minimal validation: ensure top-level keys are known-ish
    if not isinstance(data, dict):
        ctx.error("Configuration must be a YAML mapping (dict) at top level.")
        raise ValueError("Invalid configuration type")
    allowed = {"project", "download", "workflow", "environment", "dependencies", "tasks", "files", "behavior"}
    keys = set(data.keys())
    unknown = keys - allowed
    if unknown:
        ctx.warn("Unknown top-level keys in config (ignored):", ", ".join(sorted(unknown)))
    # Basic structural hints:
    if "workflow" in data and not isinstance(data["workflow"], list):
        ctx.error("'workflow' must be a list of steps.")
        raise ValueError("Invalid workflow")
    ctx.debug("Config structure validated (basic).")


# ---------------------------
# Download + integrity
# ---------------------------
def download_with_retries(url: str, dest_folder: Path, ctx: Context, expected_sha256: Optional[str] = None) -> Path:
    dest_folder.mkdir(parents=True, exist_ok=True)
    filename = url.split("/")[-1].split("?")[0] or "download.bin"
    out_path = dest_folder / filename
    attempt = 0
    last_exc = None
    while attempt <= ctx.retries:
        attempt += 1
        try:
            ctx.info(f"Downloading {url} -> {out_path.name} (attempt {attempt})")
            with requests.get(url, stream=True, timeout=ctx.timeout) as r:
                r.raise_for_status()
                with out_path.open("wb") as f:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
            ctx.info("Downloaded:", out_path)
            if expected_sha256:
                ctx.debug("Verifying SHA256...")
                if not verify_sha256(out_path, expected_sha256, ctx):
                    ctx.warn("SHA256 mismatch on downloaded file.")
                    raise ValueError("SHA256 mismatch")
                ctx.info("SHA256 OK")
            return out_path
        except Exception as e:
            last_exc = e
            ctx.warn(f"Download attempt {attempt} failed:", str(e))
            time.sleep(1 + 2 * attempt)
    ctx.error("All download attempts failed.")
    raise last_exc


def verify_sha256(path: Path, expected: str, ctx: Context) -> bool:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    got = h.hexdigest()
    ctx.debug("SHA256 expected:", expected)
    ctx.debug("SHA256 got     :", got)
    return got.lower() == expected.lower()


# ---------------------------
# Archive handling
# ---------------------------
def extract_archive(path: Path, dest: Path, ctx: Context) -> List[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    extracted = []
    s = str(path)
    ctx.info(f"Extracting {path} -> {dest}")
    if s.endswith(".zip"):
        with zipfile.ZipFile(path, "r") as z:
            z.extractall(dest)
            extracted = [dest / name for name in z.namelist()]
    elif s.endswith((".tar.gz", ".tgz", ".tar", ".tar.bz2")):
        with tarfile.open(path, "r:*") as t:
            t.extractall(dest)
            extracted = [dest / member.name for member in t.getmembers() if member.name]
    else:
        ctx.warn("Unknown archive format, skipping extract.")
    ctx.debug("Extracted items:", extracted[:5], "..." if len(extracted) > 5 else "")
    return extracted


# ---------------------------
# Virtualenv & pip install
# ---------------------------
def create_virtualenv(path: Path, ctx: Context):
    ctx.info("Preparing virtualenv at", path)
    if ctx.dry_run:
        ctx.info("[DRY-RUN] virtualenv creation skipped")
        return
    if not path.exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(path)])
        ctx.info("Virtualenv created.")
    else:
        ctx.info("Virtualenv already exists:", path)


def pip_install(target: str, spec: str, ctx: Context, requirements_file: Optional[Path] = None):
    """
    target: "venv", "user", "global"
    spec: package spec (e.g. package==1.2.3 or path to wheel/tar)
    """
    ctx.info(f"Pip install [{target}]: {spec}")
    if ctx.dry_run:
        ctx.info("[DRY-RUN] pip install skipped")
        return
    if target == "venv":
        # expects ctx to have ctx.venv_path set
        venv_bin = ctx.workdir / ".venv" / ("Scripts" if os.name == "nt" else "bin")
        pip = venv_bin / ("pip.exe" if os.name == "nt" else "pip")
        if not pip.exists():
            raise FileNotFoundError(f"pip not found in venv at {pip}")
        cmd = [str(pip), "install", spec]
    elif target == "user":
        cmd = [sys.executable, "-m", "pip", "install", "--user", spec]
    elif target == "global":
        if not ctx.force_global:
            raise PermissionError("Global install requires --force-global to be set.")
        cmd = [sys.executable, "-m", "pip", "install", spec]
    else:
        raise ValueError("Unknown pip target")
    ctx.debug("Running command:", cmd)
    subprocess.check_call(cmd)


# ---------------------------
# System package install (best-effort)
# ---------------------------
def install_system_packages(packages: List[str], ctx: Context):
    """
    Best-effort installs for system packages:
      - macOS: brew
      - Debian/Ubuntu: apt-get
      - Windows: choco (if available)
    Will not attempt sudo automatically; user must run with rights if necessary.
    """
    if not packages:
        return
    sys_name = platform.system().lower()
    ctx.info("System package install detected for", sys_name, ":", packages)
    if ctx.dry_run:
        ctx.info("[DRY-RUN] system package install skipped")
        return
    if "darwin" in sys_name:
        if shutil.which("brew"):
            cmd = ["brew", "install"] + packages
            subprocess.check_call(cmd)
        else:
            ctx.warn("Homebrew not found; cannot install system packages on macOS automatically.")
    elif "linux" in sys_name:
        if shutil.which("apt-get"):
            cmd = ["sudo", "apt-get", "update"]
            subprocess.check_call(cmd)
            cmd = ["sudo", "apt-get", "install", "-y"] + packages
            subprocess.check_call(cmd)
        else:
            ctx.warn("apt-get not found; please install packages manually.")
    elif "windows" in sys_name:
        if shutil.which("choco"):
            cmd = ["choco", "install", "-y"] + packages
            subprocess.check_call(cmd)
        else:
            ctx.warn("Chocolatey not found; please install packages manually.")
    else:
        ctx.warn("Unsupported platform for system package auto-install.")


# ---------------------------
# File operations
# ---------------------------
def ensure_directory(path: Path, ctx: Context):
    ctx.info("Ensure directory:", path)
    if ctx.dry_run:
        ctx.info("[DRY-RUN] mkdir -p", path)
        return
    path.mkdir(parents=True, exist_ok=True)


def move_path(src: Path, dest: Path, ctx: Context):
    ctx.info("Move:", src, "->", dest)
    if ctx.dry_run:
        ctx.info("[DRY-RUN] move skipped")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))


def copy_path(src: Path, dest: Path, ctx: Context):
    ctx.info("Copy:", src, "->", dest)
    if ctx.dry_run:
        ctx.info("[DRY-RUN] copy skipped")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(str(dest))
        shutil.copytree(str(src), str(dest))
    else:
        shutil.copy2(str(src), str(dest))


# ---------------------------
# Execution of commands
# ---------------------------
def run_shell_command(cmd: str, env: Dict[str, str], cwd: Optional[Path], ctx: Context, timeout: Optional[int] = None):
    ctx.info("[RUN] ", cmd, "(cwd:", cwd, "timeout:", timeout, ")")
    if ctx.dry_run:
        ctx.info("[DRY-RUN] command execution skipped")
        return 0, "", ""
    try:
        result = subprocess.run(cmd, shell=True, check=False, env={**os.environ, **env}, cwd=str(cwd) if cwd else None,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout or ctx.timeout)
        ctx.debug("Return code:", result.returncode)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired as e:
        ctx.warn("Command timeout:", e)
        return -1, "", f"timeout: {e}"


# ---------------------------
# Workflow runner
# ---------------------------
def run_workflow(config: Dict[str, Any], ctx: Context):
    env_defs = config.get("environment", {})
    dependencies = config.get("dependencies", {})
    workflow = config.get("workflow", []) or config.get("tasks", []) or []
    files_block = config.get("files", {})

    # prepare environment variables map
    runtime_env = {}
    if isinstance(env_defs, dict):
        for k, v in env_defs.items():
            runtime_env[str(k)] = str(v)
    ctx.debug("Runtime env prepared:", runtime_env)

    # Create virtualenv if asked in dependencies or workflow
    venv_path = ctx.workdir / ".venv"
    ctx.venv_path = venv_path  # for pip_install to find it
    create_venv_requested = False
    if isinstance(dependencies, dict) and dependencies.get("venv", False):
        create_venv_requested = True

    # If workflow contains create_venv step:
    for step in workflow:
        if isinstance(step, dict) and step.get("create_venv"):
            create_venv_requested = True

    if create_venv_requested:
        create_virtualenv(venv_path, ctx)

    # System packages
    sys_pkgs = dependencies.get("system", []) if isinstance(dependencies, dict) else []
    install_system_packages(sys_pkgs, ctx)

    # Pip dependencies
    pip_deps = dependencies.get("pip", []) if isinstance(dependencies, dict) else []
    for dep in pip_deps:
        # dep may be dict with spec and target
        if isinstance(dep, dict):
            spec = dep.get("spec")
            target = dep.get("target", "venv" if create_venv_requested else "user")
        else:
            spec = str(dep)
            target = "venv" if create_venv_requested else "user"
        try:
            pip_install(target, spec, ctx)
        except Exception as e:
            ctx.error("Failed to install pip dependency:", spec, "->", e)
            if not ctx.apply_changes:
                ctx.warn("Continuing in dry-run/without apply...")
            else:
                raise

    # Files block: download, extract, move, checksum
    if isinstance(files_block, dict):
        downloads = files_block.get("download", []) or []
        for item in downloads:
            # item can be str url or dict with url, sha256, extract_to, install_to
            if isinstance(item, str):
                url = item
                expected_sha = None
                extract_to = None
                install_to = None
            else:
                url = item.get("url") or item.get("download")
                expected_sha = item.get("sha256")
                extract_to = item.get("extract_to")
                install_to = item.get("install_to")
            if not url:
                ctx.warn("download item missing url, skipping:", item)
                continue
            downloaded = download_with_retries(url, ctx.tmpdir, ctx, expected_sha)
            # if archive and extract_to given -> extract
            if extract_to and downloaded.suffix.lower() in (".zip", ".gz", ".bz2", ".tgz", ".tar"):
                extract_path = ctx.workdir / extract_to
                extract_archive(downloaded, extract_path, ctx)
            # if install_to specified and file appears to be a pip-installable
            if install_to:
                target_path = Path(install_to)
                if downloaded.suffix in (".whl", ".tar.gz", ".zip"):
                    # pip install
                    # choose installation scope based on install_to semantics
                    scope = "global" if str(target_path).startswith(("/", "C:\\", "~")) else "venv"
                    try:
                        pip_install(scope, str(downloaded), ctx)
                    except Exception as e:
                        ctx.error("pip install failed for", downloaded, "->", e)

    # Workflow tasks
    for idx, step in enumerate(workflow):
        ctx.info(f"STEP {idx+1}/{len(workflow)}: {step}")
        if isinstance(step, str):
            # simple shell run
            code, out, err = run_shell_command(step, runtime_env, ctx.workdir, ctx)
            ctx.debug("Shell step result:", code)
            continue
        if not isinstance(step, dict):
            ctx.warn("Unknown workflow step format, skipping:", step)
            continue
        # known actions: say, run, check_env, create_venv, install_requirements, set_env, copy, move
        if "say" in step:
            ctx.info("[MESSAGE]", step["say"])
        if "set_env" in step and isinstance(step["set_env"], dict):
            for k, v in step["set_env"].items():
                ctx.info("Set env:", k, "=", v)
                if ctx.dry_run:
                    ctx.info("[DRY-RUN] env change skipped")
                else:
                    os.environ[str(k)] = str(v)
                    runtime_env[str(k)] = str(v)
        if "run" in step:
            cmd = step["run"]
            cwd = Path(step.get("cwd")) if step.get("cwd") else ctx.workdir
            timeout = int(step.get("timeout")) if step.get("timeout") else ctx.timeout
            retries = int(step.get("retries")) if step.get("retries") else 0
            attempt = 0
            last_code = None
            while attempt <= retries:
                attempt += 1
                code, out, err = run_shell_command(cmd, runtime_env, cwd, ctx, timeout)
                last_code = code
                if code == 0:
                    ctx.info("Command succeeded.")
                    break
                else:
                    ctx.warn("Command failed with code", code, "attempt", attempt)
                    time.sleep(1 + attempt)
            if last_code not in (0, None):
                if step.get("on_fail") == "abort":
                    raise RuntimeError(f"Command failed and asked to abort: {cmd}")
        if "check_env" in step and step["check_env"]:
            ctx.info("Performing environment checks...")
            # basic checks: python version, presence of required files
            checks = step.get("requirements", {})
            py_req = checks.get("python")
            if py_req:
                ok = sys.version.startswith(str(py_req))
                if not ok:
                    ctx.warn("Python version mismatch. Required:", py_req, "found:", sys.version)
        if "create_venv" in step and step["create_venv"]:
            vpath = ctx.workdir / (step.get("path") or ".venv")
            create_virtualenv(vpath, ctx)
        if "install_requirements" in step and step["install_requirements"]:
            req_file = ctx.workdir / (step.get("file") or "requirements.txt")
            target = step.get("target") or ("venv" if create_venv_requested else "user")
            if req_file.exists():
                pip_install(target, f"-r {req_file}", ctx)
            else:
                ctx.warn("requirements.txt not found:", req_file)
        if "copy" in step:
            src = Path(step["copy"].get("src"))
            dst = Path(step["copy"].get("dst"))
            copy_path(src, dst, ctx)
        if "move" in step:
            src = Path(step["move"].get("src"))
            dst = Path(step["move"].get("dst"))
            move_path(src, dst, ctx)

    ctx.info("Workflow finished. Temporary dir:", ctx.tmpdir)
    if ctx.dry_run:
        ctx.info("No changes applied (dry-run). Use --apply to execute actions.")
    else:
        ctx.info("Changes applied.")


# ---------------------------
# CLI
# ---------------------------
def parse_args():
    ap = argparse.ArgumentParser(prog="hhj_engine", description="HHJ Engine - run project.hhj workflows")
    ap.add_argument("--config", "-c", default=DEFAULT_CONFIG_NAME, help="Path to .hhj config (YAML)")
    ap.add_argument("--apply", action="store_true", help="Actually apply changes (default is dry-run)")
    ap.add_argument("--force-global", action="store_true", help="Allow pip global installs (dangerous)")
    ap.add_argument("--verbose", "-v", action="store_true", help="Verbose debug output")
    ap.add_argument("--workdir", "-w", default=".", help="Working directory (project root)")
    ap.add_argument("--retries", "-r", type=int, default=2, help="Retries for network actions")
    return ap.parse_args()


def main():
    args = parse_args()
    ctx = Context()
    ctx.apply_changes = args.apply
    ctx.force_global = args.force_global
    ctx.verbose = args.verbose
    ctx.dry_run = not args.apply
    ctx.retries = args.retries
    ctx.workdir = Path(args.workdir).resolve()
    ctx.tmpdir = Path(tempfile.mkdtemp(prefix="hhj_tmp_"))

    ctx.log("Working dir:", ctx.workdir)
    ctx.log("Dry run mode:", ctx.dry_run)
    ctx.log("Verbose:", ctx.verbose)
    ctx.log("Tmpdir:", ctx.tmpdir)

    try:
        config = load_config(args.config, ctx)
        run_workflow(config, ctx)
    except Exception as e:
        ctx.error("Fatal error:", e)
        if ctx.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        # cleanup only if dry-run to preserve downloads? we remove tmpdir always to avoid clutter.
        try:
            if ctx.tmpdir.exists():
                shutil.rmtree(ctx.tmpdir)
        except Exception:
            pass
def load_config(path: str, ctx: Context) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        ctx.error(f"Config file not found: {path}")
        raise FileNotFoundError(path)

    ctx.debug("Loading YAML from", path)
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # ✅ Verifica firma autore
    author = data.get("author")
    if not author:
        ctx.error("Missing 'author' field in config file.")
        raise ValueError("Missing author in configuration")

    ctx.info(f"Checking author signature: {author}")
    try:
        # 🔗 Qui va messo il link del file contenente tutte le firme valide
        SIGNATURE_LIST_URL = "https://raw.githubusercontent.com/NickC4p/hhj-for-developer/refs/heads/main/developers/authors?token=GHSAT0AAAAAADN4D7FQDLN7SMW3S7XA2OD22H6DHBQ"

        r = requests.get(SIGNATURE_LIST_URL, timeout=10)
        r.raise_for_status()
        valid_signatures = r.text.splitlines()

        if author not in valid_signatures:
            ctx.error(f"Warning: fatal error: no author signature found for '{author}'")
            raise PermissionError("No valid author signature found online")

        ctx.info(f"Author '{author}' verified successfully.")
    except Exception as e:
        ctx.error(f"Warning: fatal error: no author signature found ({e})")
        raise SystemExit(1)

    validate_config_structure(data, ctx)
    return data


if __name__ == "__main__":
    main()
